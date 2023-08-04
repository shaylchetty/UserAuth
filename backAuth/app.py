from flask import Flask, render_template, request
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

# Set up the SQLite database connection


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Create the database and users table if they don't exist


def create_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            username TEXT,
            password TEXT
        )
    ''')
    conn.commit()
    conn.close()


@app.route('/')
def home():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    conn.close()
    return render_template('index.html', users=users)

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if the user already exists in the database
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()

        if user is None:
            return 'User not found'
        else:
            stored_password = user['password']

            if password == stored_password:
                return 'Login successful'
            else:
                return 'Incorrect password'

        conn.close()

    return 'Invalid request'



@app.route('/create_account', methods=['POST'])
def create_account():
    if request.method == 'POST':
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if the user already exists in the database
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        users = cursor.fetchall()

        if len(users) == 0:
            # User does not exist, insert a new record
            cursor.execute(
                'INSERT INTO users (name, username, password) VALUES (?, ?, ?)', (name, username, password))
            conn.commit()
            conn.close()
            return 'Account created successfully'
        else:
            existing_username = users[0]['username']  # Access the 'username' column from the first row
            conn.close()
            return f'Account already exists: {existing_username}'

    return 'Invalid request'


if __name__ == '__main__':
    create_database()
    app.run(debug=True)
