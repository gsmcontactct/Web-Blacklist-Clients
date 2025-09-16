from flask import Flask, render_template, request, redirect, url_for, send_file
import sqlite3, os

app = Flask(__name__)

# folosim /tmp ca să fim siguri că avem write access pe Render
DB_NAME = os.path.join("/tmp", "blacklist.db")

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS clients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    reason TEXT)''')
    conn.commit()
    conn.close()

# APEL DIRECT LA IMPORT (fix pentru Render)
init_db()

@app.route('/')
def index():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM clients")
    clients = c.fetchall()
    conn.close()
    return render_template('index.html', clients=clients)

@app.route('/add', methods=['POST'])
def add_client():
    name = request.form['name']
    phone = request.form['phone']
    reason = request.form['reason']
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO clients (name, phone, reason) VALUES (?, ?, ?)", (name, phone, reason))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/delete/<int:client_id>')
def delete_client(client_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM clients WHERE id=?", (client_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/download-db')
def download_db():
    return send_file(DB_NAME, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
