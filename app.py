from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import sqlite3
import re
from pathlib import Path

DB_FILE = "blacklist.db"
app = Flask(__name__)
app.secret_key = "schimba_cheia_aici"  # schimbă în producție


def normalize(text):
    return re.sub(r'[^a-z0-9 ]', '', (text or "").lower().strip())


def init_db():
    """Creează baza de date și tabela dacă nu există"""
    Path(DB_FILE).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS blacklist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nume TEXT NOT NULL,
            telefon TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def get_all():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, nume, telefon FROM blacklist ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return rows


def search_rows(query):
    q = normalize(query)
    if q == "":
        return get_all()
    rows = get_all()
    filtered = [r for r in rows if q in normalize(r[1]) or q in normalize(r[2])]
    return filtered


@app.route("/", methods=["GET"])
def index():
    q = request.args.get("q", "")
    rows = search_rows(q)
    return render_template("index.html", rows=rows, query=q)


@app.route("/add", methods=["POST"])
def add():
    nume = request.form.get("nume", "").strip()
    telefon = request.form.get("telefon", "").strip()
    if not nume or not telefon:
        flash("Completează nume și telefon", "danger")
        return redirect(url_for("index"))

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO blacklist (nume, telefon) VALUES (?, ?)", (nume, telefon))
    conn.commit()
    conn.close()

    flash(f"Client adăugat: {nume} ({telefon})", "success")
    return redirect(url_for("index"))


@app.route("/delete", methods=["POST"])
def delete():
    pid = request.form.get("id")
    if not pid or not pid.isnumeric():
        flash("ID invalid", "danger")
        return redirect(url_for("index"))

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM blacklist WHERE id=?", (int(pid),))
    conn.commit()
    conn.close()

    flash("Client șters din blacklist", "info")
    return redirect(url_for("index"))


@app.route("/download-db")
def download_db():
    """Permite descărcarea bazei de date SQLite"""
    if not Path(DB_FILE).exists():
        flash("Nu există bază de date", "danger")
        return redirect(url_for("index"))
    return send_file(DB_FILE, as_attachment=True)


@app.route("/upload-db", methods=["POST"])
def upload_db():
    """Permite încărcarea unei baze de date SQLite"""
    file = request.files.get("file")
    if not file:
        flash("Nu ai selectat niciun fișier", "danger")
        return redirect(url_for("index"))

    # suprascrie fișierul existent
    file.save(DB_FILE)
    flash("Baza de date a fost încărcată cu succes!", "success")
    return redirect(url_for("index"))


# Rulează init_db la pornire (și local și pe Render/Gunicorn)
init_db()

if __name__ == "__main__":
    app.run(debug=True)
