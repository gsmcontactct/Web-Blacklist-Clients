from flask import Flask, render_template, request, redirect, url_for, send_file, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"  # pentru flash messages
DATABASE = "blacklist.db"


# === Baza de date ===
def init_db():
    conn = sqlite3.connect(DATABASE)
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
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT id, name, phone, reason FROM blacklist ORDER BY id DESC")
    data = c.fetchall()
    conn.close()
    return data


def add_client(name, phone, reason):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("INSERT INTO blacklist (name, phone, reason) VALUES (?, ?, ?)", (name, phone, reason))
    conn.commit()
    conn.close()


def delete_client(client_id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("DELETE FROM blacklist WHERE id = ?", (client_id,))
    conn.commit()
    conn.close()


# === Rute Flask ===
@app.route("/")
def index():
    clients = get_all()
    return render_template("index.html", clients=clients)


@app.route("/add", methods=["POST"])
def add():
    name = request.form["name"]
    phone = request.form["phone"]
    reason = request.form.get("reason", "")

    add_client(name, phone, reason)
    flash("Client adăugat cu succes ✅", "success")
    return redirect(url_for("index"))


@app.route("/delete/<int:client_id>")
def delete(client_id):
    delete_client(client_id)
    flash("Client șters ❌", "warning")
    return redirect(url_for("index"))


@app.route("/download-db")
def download_db():
    if os.path.exists(DATABASE):
        return send_file(DATABASE, as_attachment=True)
    flash("Nu există baza de date de descărcat", "danger")
    return redirect(url_for("index"))


@app.route("/upload-db", methods=["POST"])
def upload_db():
    if "file" not in request.files:
        flash("Niciun fișier selectat", "danger")
        return redirect(url_for("index"))

    file = request.files["file"]
    if file.filename == "":
        flash("Numele fișierului este invalid", "danger")
        return redirect(url_for("index"))

    if file:
        file.save(DATABASE)  # suprascrie DB
        flash("Baza de date a fost încărcată cu succes ✅", "success")
        return redirect(url_for("index"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
