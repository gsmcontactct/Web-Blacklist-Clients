import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, send_file

app = Flask(__name__)
app.secret_key = "supersecretkey"

DB_FILE = "blacklist.db"


def init_db():
    """Creează baza de date dacă nu există."""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute(
            """CREATE TABLE IF NOT EXISTS blacklist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nume TEXT NOT NULL,
                telefon TEXT NOT NULL
            )"""
        )
        conn.commit()


def get_all():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("SELECT id, nume, telefon FROM blacklist ORDER BY id DESC")
        return c.fetchall()


def search_rows(q):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        like = f"%{q}%"
        c.execute(
            "SELECT id, nume, telefon FROM blacklist WHERE nume LIKE ? OR telefon LIKE ? ORDER BY id DESC",
            (like, like),
        )
        return c.fetchall()


@app.route("/", methods=["GET", "POST"])
def index():
    q = request.args.get("q", "").strip()
    if q:
        rows = search_rows(q)
    else:
        rows = get_all()
    return render_template("index.html", rows=rows, query=q)


@app.route("/add", methods=["POST"])
def add():
    nume = request.form.get("nume", "").strip()
    telefon = request.form.get("telefon", "").strip()
    if nume and telefon:
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO blacklist (nume, telefon) VALUES (?, ?)", (nume, telefon))
            conn.commit()
        flash("Client adăugat în blacklist ✅", "success")
    else:
        flash("Toate câmpurile sunt obligatorii ❌", "danger")
    return redirect(url_for("index"))


@app.route("/delete", methods=["POST"])
def delete():
    row_id = request.form.get("id")
    if row_id:
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute("DELETE FROM blacklist WHERE id = ?", (row_id,))
            conn.commit()
        flash("Client șters din blacklist 🗑️", "warning")
    return redirect(url_for("index"))


@app.route("/download")
def download_db():
    if not os.path.exists(DB_FILE):
        flash("Baza de date nu există!", "danger")
        return redirect(url_for("index"))
    return send_file(DB_FILE, as_attachment=True)


@app.route("/upload", methods=["POST"])
def upload_db():
    file = request.files.get("file")
    if not file:
        flash("Nu ai selectat niciun fișier ❌", "danger")
        return redirect(url_for("index"))

    if not file.filename.endswith(".db"):
        flash("Trebuie să încarci un fișier .db ❌", "danger")
        return redirect(url_for("index"))

    file.save(DB_FILE)
    flash("Baza de date a fost încărcată cu succes ✅", "success")
    return redirect(url_for("index"))


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
