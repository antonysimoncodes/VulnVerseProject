from flask import Flask, render_template, request, redirect, url_for, session, flash
import hashlib
import hmac
import os
import sqlite3

app = Flask(__name__)
# VULNERABLE: hardcoded secret key and weak token secret
app.config['SECRET_KEY'] = 'crypto_fail_secret'
WEAK_TOKEN_SECRET = b'insecure-shared-secret'


def init_db():
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        password_md5 TEXT NOT NULL,
        email TEXT NOT NULL
    )''')
    # Seed a demo user if none exist
    cur.execute('SELECT COUNT(*) FROM users')
    if cur.fetchone()[0] == 0:
        # password: password123
        md5_pwd = hashlib.md5('password123'.encode()).hexdigest()
        cur.execute('INSERT INTO users (username, password_md5, email) VALUES (?, ?, ?)',
                    ('alice', md5_pwd, 'alice@example.com'))
    conn.commit()
    conn.close()


# Initialize DB at import time (Flask 3 has no before_first_request)
init_db()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        email = request.form.get('email', '')
        # VULNERABLE: store password using MD5 (no salt, no stretching)
        pwd_md5 = hashlib.md5(password.encode()).hexdigest()
        try:
            conn = sqlite3.connect('users.db')
            cur = conn.cursor()
            cur.execute('INSERT INTO users (username, password_md5, email) VALUES (?, ?, ?)',
                        (username, pwd_md5, email))
            conn.commit()
            flash('Registered. Please login.')
            return redirect(url_for('login'))
        except Exception:
            flash('Registration failed (maybe username exists).')
        finally:
            conn.close()
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        # VULNERABLE: MD5 compare
        candidate = hashlib.md5(password.encode()).hexdigest()
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        cur.execute('SELECT id, username, password_md5, email FROM users WHERE username=?', (username,))
        row = cur.fetchone()
        conn.close()
        if row and hmac.compare_digest(candidate, row[2]):
            session['user_id'] = row[0]
            session['username'] = row[1]
            session['email'] = row[3]
            # VULNERABLE: predictable auth token (HMAC over username with weak secret)
            token = hmac.new(WEAK_TOKEN_SECRET, row[1].encode(), hashlib.sha1).hexdigest()
            session['auth_token'] = token
            return redirect(url_for('profile'))
        error = 'Invalid credentials'
    return render_template('login.html', error=error)


@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('profile.html', username=session.get('username'), email=session.get('email'), token=session.get('auth_token'))


@app.route('/verify_token')
def verify_token():
    # VULNERABLE: weak HMAC secret makes tokens guessable
    username = request.args.get('u', '')
    token = request.args.get('t', '')
    calc = hmac.new(WEAK_TOKEN_SECRET, username.encode(), hashlib.sha1).hexdigest()
    ok = hmac.compare_digest(calc, token)
    return {'username': username, 'token_valid': ok}


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


