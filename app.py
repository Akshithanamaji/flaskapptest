from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database initialization
def init_db():
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        # Create the users table if it does not exist
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT UNIQUE NOT NULL,
                            password TEXT NOT NULL)''')
        conn.commit()
        
        # Insert the admin user if it does not already exist
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('admin', 'admin123'))
            conn.commit()
        except sqlite3.IntegrityError:
            # Ignore the error if the admin user already exists
            pass

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('index'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        with sqlite3.connect('users.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
            user = cursor.fetchone()
        
        if user:
            session['username'] = username
            # Check if the user is admin
            if username == 'admin':
                return redirect(url_for('admin'))
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials. Please try again.', 'error')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        with sqlite3.connect('users.db') as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                conn.commit()
                flash('Registration successful! Please log in.', 'success')
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                flash('Username already exists. Try another one.', 'error')
    return render_template('register.html')

@app.route('/index')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', username=session['username'])

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))
@app.route('/admin')

@app.route('/admin')
def admin():
    if 'username' not in session or session['username'] != 'admin':
        flash('Access denied. Admins only.', 'error')
        return redirect(url_for('login'))
    
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username FROM users")
        users = cursor.fetchall()
    
    return render_template('admin.html', users=users)



if __name__ == '__main__':
    init_db()
    app.run(debug=True)
