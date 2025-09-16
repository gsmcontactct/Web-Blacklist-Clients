import sqlite3
from flask import Flask, render_template, request, redirect, send_file, flash
import os

app = Flask(__name__)
app.secret_key = "super_secret_key"  # pentru flash messages

DB_FILE = "blacklist.db"


def init_db():
    """Creează baza de date dacă nu există."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS blacklist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            reason TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def get_all():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, name, phone, reason FROM blacklist ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return rows


@app.route("/")
def index():
    clients = get_all()
    return render_template("index.html", clients=clients)


@app.route("/add", methods=["POST"])
def add():
    name = request.form.get("name")
    phone = request.form.get("phone")
    reason = request.form.get("reason")

    if not name or not phone:
        flash("⚠️ Nume și telefon sunt obligatorii!", "danger")
        return redirect("/")

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "INSERT INTO blacklist (name, phone, reason) VALUES (?, ?, ?)",
        (name, phone, reason),
    )
    conn.commit()
    conn.close()

    flash(f"✅ Clientul {name} a fost adăugat în blacklist.", "success")
    return redirect("/")


@app.route("/delete/<int:client_id>")
def delete(client_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM blacklist WHERE id = ?", (client_id,))
    conn.commit()
    conn.close()

    flash("🗑️ Client șters.", "info")
    return redirect("/")


@app.route("/download-db")
def download_db():
    return send_file(DB_FILE, as_attachment=True)


if __name__ == "__main__":
    if not os.path.exists(DB_FILE):
        init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
