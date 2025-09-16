import os
import sqlite3
from flask import Flask, render_template, request, redirect, send_file, flash

app = Flask(__name__)
app.secret_key = "secret-key"  # necesar pentru flash messages

DB_NAME = "blacklist.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
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
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, name, phone, reason FROM blacklist ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return rows


def add_client(name, phone, reason):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO blacklist (name, phone, reason) VALUES (?, ?, ?)", (name, phone, reason))
    conn.commit()
    conn.close()


def delete_client(client_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM blacklist WHERE id=?", (client_id,))
    conn.commit()
    conn.close()


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
        flash("✅ Client adăugat cu succes!", "success")
    else:
        flash("⚠️ Nume și telefon sunt obligatorii!", "danger")
    return redirect("/")


@app.route("/delete/<int:client_id>")
def delete(client_id):
    delete_client(client_id)
    flash("🗑️ Client șters!", "info")
    return redirect("/")


@app.route("/download-db")
def download_db():
    return send_file(DB_NAME, as_attachment=True)


@app.route("/upload-db", methods=["POST"])
def upload_db():
    if "file" not in request.files:
        flash("⚠️ Nicio fișă nu a fost trimisă!", "danger")
        return redirect("/")
    file = request.files["file"]
    if file.filename == "":
        flash("⚠️ Nicio fișă selectată!", "danger")
