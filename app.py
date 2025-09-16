from flask import Flask, render_template, request, redirect, send_file
import sqlite3
import os

app = Flask(__name__)
DB_FILE = "blacklist.db"

# --- INIT DB ---
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS blacklist (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    reason TEXT
                )''')
    conn.commit()
    conn.close()

# rulează automat la start
init_db()


# --- DATABASE FUNCS ---
def get_all():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, name, phone, reason FROM blacklist ORDER BY id DESC")
    data = c.fetchall()
    conn.close()
    return data

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
    if name and phone:
        add_client(name, phone, reason)
    return redirect("/")

@app.route("/delete/<int:client_id>")
def delete(client_id):
    delete_client(client_id)
    return redirect("/")

@app.route("/download-db")
def download_db():
    if os.path.exists(DB_FILE):
        return send_file(DB_FILE, as_attachment=True)
    return "Database not found", 404


# --- START LOCAL ---
if __name__ == "__main__":
    app.run(debug=True)
