import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "supersecret"

DB_FILE = "blacklist.db"


def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS blacklist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nume TEXT NOT NULL,
            telefon TEXT NOT NULL
        )"""
    )
    conn.commit()
    conn.close()


def get_all():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, nume, telefon FROM blacklist ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return rows


@app.route("/", methods=["GET"])
def index():
    q = request.args.get("q", "")
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    if q:
        c.execute(
            "SELECT id, nume, telefon FROM blacklist WHERE nume LIKE ? OR telefon LIKE ? ORDER BY id DESC",
            (f"%{q}%", f"%{q}%"),
        )
    else:
        c.execute("SELECT id, nume, telefon FROM blacklist ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return render_template("index.html", rows=rows, query=q)


@app.route("/add", methods=["POST"])
def add():
    nume = request.form["nume"]
    telefon = request.form["telefon"]
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO blacklist (nume, telefon) VALUES (?, ?)", (nume, telefon))
    conn.commit()
    conn.close()
    flash("Client adăugat în blacklist", "success")
    return redirect(url_for("index"))


@app.route("/delete", methods=["POST"])
def delete():
    client_id = request.form["id"]
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM blacklist WHERE id=?", (client_id,))
    conn.commit()
    conn.close()
    flash("Client șters", "warning")
    return redirect(url_for("index"))


@app.route("/download_db")
def download_db():
    return send_file(DB_FILE, as_attachment=True)


@app.route("/upload_db", methods=["POST"])
def upload_db():
    if "file" not in request.files:
        flash("Niciun fișier selectat", "danger")
        return redirect(url_for("index"))

    file = request.files["file"]
    if file.filename == "":
        flash("Numele fișierului este gol", "danger")
        return redirect(url_for("index"))

    filename = secure_filename(file.filename)
    file.save(DB_FILE)
    flash("Baza de date a fost încărcată cu succes", "success")
    return redirect(url_for("index"))


# ⚡ Asta face ca init_db să ruleze și pe Render, nu doar local
init_db()

if __name__ == "__main__":
    app.run(debug=True)
