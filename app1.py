from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
import pymysql

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

# Database setup with ngrok-provided host and port
def get_db():
    conn = pymysql.connect(
        host='https://e258-31-217-3-166.ngrok-free.app',  # Replace with ngrok host (e.g., 7.tcp.eu.ngrok.io)
        port=8000,  # Replace with ngrok port (e.g., 17117)
        user='emil.lovrekovic@gmail.com',  # Your MySQL user (usually 'root')
        password='Dubrovnik50#',  # Your MySQL password
        db='app008'  # Your database name
    )
    return conn

# Create users table if it doesn't exist
def create_user_table():
    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                gesture_pattern VARCHAR(255) NOT NULL
            )
        ''')
    conn.commit()
    conn.close()

create_user_table()

# Register API endpoint
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    gesture_pattern = data.get('gesture_pattern')

    if not username or not password or not gesture_pattern:
        return jsonify({"error": "Please provide username, password, and gesture pattern"}), 400

    hashed_password = generate_password_hash(password)

    try:
        conn = get_db()
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO users (username, password, gesture_pattern) VALUES (%s, %s, %s)", 
                           (username, hashed_password, gesture_pattern))
        conn.commit()
        conn.close()
        return jsonify({"message": "User registered successfully!"}), 201
    except pymysql.err.IntegrityError:
        return jsonify({"error": "Username already exists"}), 400

# Login API endpoint
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    gesture_pattern = data.get('gesture_pattern')

    if not username or not password or not gesture_pattern:
        return jsonify({"error": "Please provide username, password, and gesture pattern"}), 400

    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user[2], password) and user[3] == gesture_pattern:
        return jsonify({"message": "Login successful!"}), 200
    else:
        return jsonify({"error": "Invalid credentials or gesture pattern"}), 400

# Run the Flask app (Flask will be hosted on Render, not locally)
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
