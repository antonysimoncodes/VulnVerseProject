from flask import Flask, render_template, request, redirect, url_for, session, abort
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = 'vulnerable_secret_key_bac'


def init_db():
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )''')
    cur.execute('SELECT COUNT(*) FROM users')
    if cur.fetchone()[0] == 0:
        users = [
            (1, 'admin', 'admin123', 'admin'),
            (2, 'jane', 'password', 'user'),
            (3, 'bob', 'password', 'user')
        ]
        cur.executemany('INSERT INTO users VALUES (?, ?, ?, ?)', users)
    conn.commit()
    conn.close()


# Flask 3 removed before_first_request. Initialize DB at startup.
init_db()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        # VULNERABLE: no rate limiting, weak auth, plain text
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        cur.execute('SELECT id, username, password, role FROM users WHERE username=?', (username,))
        row = cur.fetchone()
        conn.close()
        if row and row[2] == password:
            session['user_id'] = row[0]
            session['username'] = row[1]
            session['role'] = row[3]
            return redirect(url_for('dashboard'))
        error = 'Invalid credentials'
    return render_template('login.html', error=error)


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session.get('username'), role=session.get('role'))


@app.route('/admin')
def admin():
    # VULNERABILITY: Broken Access Control
    # Access is granted if a query parameter is present, ignoring actual role
    # Example exploit: /admin?as=admin
    if request.args.get('as') == 'admin':
        return render_template('admin.html')

    # Intended control (but missing enforcement): only admins should access
    if session.get('role') == 'admin':
        return render_template('admin.html')

    # Insecure: reveal existence of admin area without proper 403 handling
    abort(403)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


