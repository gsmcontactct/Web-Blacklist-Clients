from flask import Flask, render_template, request, redirect, send_file
import sqlite3
import os

app = Flask(__name__)
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


@app.route("/")
def index():
    init_db()  # se asigură că tabela există mereu
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


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
