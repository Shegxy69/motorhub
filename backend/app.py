from flask import Flask, request, jsonify
import os, psycopg2

app = Flask(__name__)

# Manual Secret will provide these later!
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASS = os.environ.get("DB_PASS", "password")

# Hardcoded cars for the showroom
CARS = [
    {"id": 1, "make": "Tesla Model 3", "price": 40000, "currency": "USD"},
    {"id": 2, "make": "Porsche 911", "price": 120000, "currency": "USD"},
    {"id": 3, "make": "Toyota Camry", "price": 25000, "currency": "USD"},
    {"id": 4, "make": "Ford Mustang", "price": 32000, "currency": "USD"},
    {"id": 5, "make": "BMW 3 Series", "price": 45000, "currency": "USD"},
    {"id": 6, "make": "Mercedes C-Class", "price": 47000, "currency": "USD"},
    {"id": 7, "make": "Honda Civic", "price": 28000, "currency": "USD"},
    {"id": 8, "make": "Audi A4", "price": 42000, "currency": "USD"},
    {"id": 9, "make": "Volkswagen Golf", "price": 30000, "currency": "USD"},
    {"id": 10, "make": "Chevrolet Corvette", "price": 66000, "currency": "USD"},
    {"id": 11, "make": "Lexus IS 300", "price": 43000, "currency": "USD"},
    {"id": 12, "make": "Nissan Altima", "price": 27000, "currency": "USD"},
    {"id": 13, "make": "Subaru WRX", "price": 35000, "currency": "USD"}
]

# Simple in-memory cart (username -> list of cars)
CARTS = {}

def get_db_connection():
    return psycopg2.connect(host=DB_HOST, user=DB_USER, password=DB_PASS, dbname="motorhub")

@app.route('/auth', methods=['POST'])
def auth():
    data = request.json or {}
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        if data.get('action') == 'signup':
            cur.execute(
                "INSERT INTO users (username, password) VALUES (%s, %s)",
                (data['username'], data['password'])
            )
            conn.commit()
            msg = "User created!"
        else:
            cur.execute(
                "SELECT * FROM users WHERE username = %s AND password = %s",
                (data['username'], data['password'])
            )
            if not cur.fetchone():
                cur.close()
                conn.close()
                return jsonify({"error": "Invalid credentials"}), 401
            msg = "Logged in!"

        cur.close()
        conn.close()
        return jsonify({"message": msg}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def init_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(50) NOT NULL
            );
        ''')
        conn.commit()
        cur.close()
        conn.close()
    except Exception:
        print("Database not ready yet...")


# Call it before the app starts
init_db()

@app.route('/cars', methods=['GET'])
def get_cars():
    return jsonify(CARS)

@app.route('/cart', methods=['POST', 'GET'])
def cart():
    payload = request.get_json(silent=True) or {}
    username = payload.get('username')

    if request.method == 'POST':
        car_id = payload.get('car_id')
        car = next((c for c in CARS if c['id'] == int(car_id)), None)
        if car:
            CARTS.setdefault(username, []).append(car)
            return jsonify({"message": f"{car['make']} added to cart!", "currency": "USD"})

    # GET cart
    user_cart = CARTS.get(username, [])
    total = sum(item['price'] for item in user_cart)
    return jsonify({"cart": user_cart, "total": total, "currency": "USD"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
