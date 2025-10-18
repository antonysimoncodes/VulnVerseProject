from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
import os
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = 'vulnerable_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Create database and tables
def init_db():
    # Connect to SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        email TEXT NOT NULL,
        role TEXT NOT NULL
    )
    ''')
    
    # Create products table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT NOT NULL,
        price REAL NOT NULL
    )
    ''')
    
    # Insert sample data if tables are empty
    cursor.execute('SELECT COUNT(*) FROM users')
    if cursor.fetchone()[0] == 0:
        # Insert sample users
        users = [
            (1, 'admin', 'admin123', 'admin@example.com', 'admin'),
            (2, 'john', 'password123', 'john@example.com', 'user'),
            (3, 'alice', 'securepass', 'alice@example.com', 'user'),
            (4, 'bob', 'bobpass', 'bob@example.com', 'user'),
            (5, 'superadmin', 'supersecret!', 'superadmin@internal.com', 'superadmin')
        ]
        cursor.executemany('INSERT INTO users VALUES (?, ?, ?, ?, ?)', users)
    
    cursor.execute('SELECT COUNT(*) FROM products')
    if cursor.fetchone()[0] == 0:
        # Insert sample products
        products = [
            (1, 'Laptop', 'High-performance laptop', 999.99),
            (2, 'Smartphone', 'Latest smartphone model', 699.99),
            (3, 'Tablet', '10-inch tablet', 349.99),
            (4, 'Headphones', 'Noise-cancelling headphones', 149.99),
            (5, 'Smartwatch', 'Fitness tracking smartwatch', 199.99)
        ]
        cursor.executemany('INSERT INTO products VALUES (?, ?, ?, ?)', products)
    
    # Commit changes and close connection
    conn.commit()
    conn.close()

# Routes

# Home page
@app.route('/')
def index():
    return render_template('index.html')

# Login page (SQLi vulnerable)
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # VULNERABLE: Direct string concatenation in SQL query
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        cursor.execute(query)
        user = cursor.fetchone()
        conn.close()
        if user:
            session['logged_in'] = True
            session['username'] = username
            session['role'] = user[4]
            flash('You were successfully logged in')
            return redirect(url_for('dashboard'))
        else:
            error = 'Invalid credentials. Please try again.'
    return render_template('login.html', error=error)

# Dashboard page (shows products)
@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products')
    products = cursor.fetchall()
    conn.close()
    return render_template('dashboard.html', username=session.get('username'), role=session.get('role'), products=products)

# Product search (SQLi vulnerable)
@app.route('/search', methods=['GET', 'POST'])
def search():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    results = []
    search_term = ''
    if request.method == 'POST':
        search_term = request.form['search_term']
        # VULNERABLE: Direct string concatenation in SQL query
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        query = f"SELECT * FROM products WHERE name LIKE '%{search_term}%' OR description LIKE '%{search_term}%'"
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
    return render_template('search.html', results=results, search_term=search_term)

# User profile (SQLi vulnerable)
@app.route('/user/<username>')
def user_profile(username):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    # VULNERABLE: Direct string concatenation in SQL query
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)
    user = cursor.fetchone()
    conn.close()
    if user:
        return render_template('user_profile.html', user=user)
    else:
        flash('User not found')
        return redirect(url_for('dashboard'))

# Logout
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    session.pop('role', None)
    flash('You were logged out')
    return redirect(url_for('index'))

# Initialize database before first request
@app.before_first_request
def before_first_request():
    init_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)