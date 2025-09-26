from flask import Flask, render_template, request, redirect, send_file, flash
import sqlite3
import os
import dropbox

app = Flask(__name__)
app.secret_key = "supersecret"
DB_NAME = "clients.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS blacklist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            reason TEXT
        )
    """)
    conn.commit()
    conn.close()


def get_all():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, name, phone, reason FROM blacklist ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return rows


def get_dropbox_client():
    token = os.environ.get("DROPBOX_TOKEN")
    if not token:
        raise ValueError("Lipsește DROPBOX_TOKEN în environment variables")
    return dropbox.Dropbox(token)


@app.route("/")
def index():
    init_db()
    clients = get_all()
    return render_template("index.html", clients=clients)


@app.route("/add", methods=["POST"])
def add():
    name = request.form.get("name")
    phone = request.form.get("phone")
    reason = request.form.get("reason")

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO blacklist (name, phone, reason) VALUES (?, ?, ?)",
              (name, phone, reason))
    conn.commit()
    conn.close()
    return redirect("/")


@app.route("/delete/<int:client_id>")
def delete(client_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM blacklist WHERE id = ?", (client_id,))
    conn.commit()
    conn.close()
    return redirect("/")


@app.route("/download-db")
def download_db():
    return send_file(DB_NAME, as_attachment=True)


@app.route("/upload-db", methods=["POST"])
def upload_db():
    if "file" not in request.files:
        return "No file part", 400

    file = request.files["file"]
    if file.filename == "":
        return "No selected file", 400

    file.save(DB_NAME)
    init_db()
    return redirect("/")


# === Dropbox Routes ===
@app.route("/save-dropbox")
def save_dropbox():
    dbx = get_dropbox_client()
    with open(DB_NAME, "rb") as f:
        dbx.files_upload(f.read(), f"/{DB_NAME}", mode=dropbox.files.WriteMode.overwrite)
    flash("📤 Baza de date a fost salvată în Dropbox", "success")
    return redirect("/")


@app.route("/load-dropbox")
def load_dropbox():
    dbx = get_dropbox_client()
    try:
        _, res = dbx.files_download(f"/{DB_NAME}")
        with open(DB_NAME, "wb") as f:
            f.write(res.content)
        flash("📥 Baza de date a fost încărcată din Dropbox", "success")
    except dropbox.exceptions.ApiError:
        flash("❌ Fișierul nu există în Dropbox", "error")
    init_db()
    return redirect("/")


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
