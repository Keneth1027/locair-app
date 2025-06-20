from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import hashlib

app = Flask(__name__)
CORS(app)

# Hash password helper
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# DB Connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="boarding_db"
    )

# Register
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data['username']
    password = hash_password(data['password'])

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password, role, name, gender) VALUES (%s, %s, 'user', '', '')", (username, password))
        conn.commit()
        conn.close()
        return jsonify({"message": "User registered successfully!"}), 201
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 400

# Login
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data['username']
    password = hash_password(data['password'])

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        return jsonify({
            "message": "Login successful",
            "user_id": user[0],
            "username": user[1],
            "role": user[3],
            "name": user[4],
            "gender": user[5]
        })
    else:
        return jsonify({"message": "Invalid credentials"}), 401

# View all houses
@app.route('/api/houses', methods=['GET'])
def get_houses():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM boarding_houses")
    houses = cursor.fetchall()
    conn.close()

    result = []
    for h in houses:
        result.append({
            "id": h[0],
            "name": h[1],
            "address": h[2],
            "price": h[3]
        })

    return jsonify(result)

# Add house (admin only)
@app.route('/api/houses', methods=['POST'])
def add_house():
    data = request.get_json()

    if 'username' not in data or 'role' not in data or data['role'] != 'admin':
        return jsonify({"message": "Access denied. Admins only."}), 403

    name = data['name']
    address = data['address']
    price = data['price']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO boarding_houses (name, address, price) VALUES (%s, %s, %s)",
                   (name, address, price))
    conn.commit()
    conn.close()

    return jsonify({"message": "Boarding house added successfully"})

# Get all users (admin view)
@app.route('/api/users', methods=['GET'])
def get_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, role, name, gender FROM users")
    users = cursor.fetchall()
    conn.close()

    result = []
    for user in users:
        result.append({
            "id": user[0],
            "username": user[1],
            "role": user[2],
            "name": user[3],
            "gender": user[4]
        })

    return jsonify(result)

# ✅ Update Profile (name + gender)
@app.route('/api/update_profile', methods=['POST'])
def update_profile():
    data = request.json
    user_id = data['user_id']
    name = data['name']
    gender = data['gender']

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET name = %s, gender = %s WHERE id = %s", (name, gender, user_id))
        conn.commit()
        conn.close()
        return jsonify({"message": "Profile updated successfully!"})
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 400

# Run server
if __name__ == '__main__':
    app.run(debug=True)
