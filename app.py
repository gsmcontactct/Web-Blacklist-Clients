from flask import Flask, render_template, request, redirect, send_file
import sqlite3
import os

app = Flask(__name__)
DB_FILE = "clients.db"


def init_db():
    conn = sqlite3.connect(DB_FILE)
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
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, name, phone, reason FROM blacklist ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return rows


def add_client(name, phone, reason):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO blacklist (name, phone, reason) VALUES (?, ?, ?)", (name, phone, reason))
    conn.commit()
    conn.close()


def delete_client(client_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM blacklist WHERE id = ?", (client_id,))
    conn.commit()
    conn.close()


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
    return redirect("/")


@app.route("/delete/<int:client_id>")
def delete(client_id):
    delete_client(client_id)
    return redirect("/")


@app.route("/download-db")
def download_db():
    return send_file(DB_FILE, as_attachment=True)


if __name__ == "__main__":
    init_db()  # <-- creează tabela dacă nu există
    app.run(host="0.0.0.0", port=5000, debug=True)
