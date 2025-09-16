import os
import sqlite3
from flask import Flask, render_template, request, redirect, send_file, flash

app = Flask(__name__)
app.secret_key = "supersecret"  # necesar pt flash messages

DB_FILE = "blacklist.db"

# --- INIT DB ---
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

init_db()

# --- HELPERS ---
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

# --- ROUTES ---
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
        flash("⚠️ Nume și telefon obligatorii!", "danger")
    else:
        add_client(name, phone, reason)
        flash("✅ Client adăugat cu succes!", "success")
    return redirect("/")

@app.route("/delete/<int:client_id>")
def delete(client_id):
    delete_client(client_id)
    flash("🗑️ Client șters!", "info")
    return redirect("/")

@app.route("/download-db")
def download_db():
    if os.path.exists(DB_FILE):
        return send_file(DB_FILE, as_attachment=True)
    flash("⚠️ Baza de date nu există încă!", "danger")
    return redirect("/")

# --- START ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
