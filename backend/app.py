from flask import Flask, request, jsonify
import os, re

app = Flask(__name__)

# Hardcoded cars for the showroom
CARS = [
    {"id": 1, "make": "Tesla Model 3", "price": 40000, "currency": "USD", "image": "https://images.unsplash.com/photo-1553440569-bcc63803a83d?auto=format&fit=crop&w=900&q=80"},
    {"id": 2, "make": "Porsche 911", "price": 120000, "currency": "USD", "image": "https://images.unsplash.com/photo-1503376780353-7c5f7adf58d3?auto=format&fit=crop&w=900&q=80"},
    {"id": 3, "make": "Toyota Camry", "price": 25000, "currency": "USD", "image": "https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?auto=format&fit=crop&w=900&q=80"},
    {"id": 4, "make": "Ford Mustang", "price": 32000, "currency": "USD", "image": "https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?auto=format&fit=crop&w=900&q=80"},
    {"id": 5, "make": "BMW 3 Series", "price": 45000, "currency": "USD", "image": "https://images.unsplash.com/photo-1511919884226-fd3cad34687c?auto=format&fit=crop&w=900&q=80"},
    {"id": 6, "make": "Mercedes C-Class", "price": 47000, "currency": "USD", "image": "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?auto=format&fit=crop&w=900&q=80"},
    {"id": 7, "make": "Honda Civic", "price": 28000, "currency": "USD", "image": "https://images.unsplash.com/photo-1559251606-c623743a6d76?auto=format&fit=crop&w=900&q=80"},
    {"id": 8, "make": "Audi A4", "price": 42000, "currency": "USD", "image": "https://images.unsplash.com/photo-1544636331-e26879cd4d9b?auto=format&fit=crop&w=900&q=80"},
    {"id": 9, "make": "Volkswagen Golf", "price": 30000, "currency": "USD", "image": "https://images.unsplash.com/photo-1549399542-7e3f8b79c341?auto=format&fit=crop&w=900&q=80"},
    {"id": 10, "make": "Chevrolet Corvette", "price": 66000, "currency": "USD", "image": "https://images.unsplash.com/photo-1605559424843-9e4c179359f4?auto=format&fit=crop&w=900&q=80"},
    {"id": 11, "make": "Lexus IS 300", "price": 43000, "currency": "USD", "image": "https://images.unsplash.com/photo-1494905998402-395d579af36f?auto=format&fit=crop&w=900&q=80"},
    {"id": 12, "make": "Nissan Altima", "price": 27000, "currency": "USD", "image": "https://images.unsplash.com/photo-1503736334956-4c8f8e92946d?auto=format&fit=crop&w=900&q=80"},
    {"id": 13, "make": "Subaru WRX", "price": 35000, "currency": "USD", "image": "https://images.unsplash.com/photo-1502877338535-766e1452684a?auto=format&fit=crop&w=900&q=80"}
]

CARTS = {}
ORDERS = {}


def luhn_checksum(card_number):
    digits = re.sub(r"\D", "", card_number)
    if len(digits) < 12:
        return False

    total = 0
    should_double = False
    for ch in reversed(digits):
        d = int(ch)
        if should_double:
            d *= 2
            if d > 9:
                d -= 9
        total += d
        should_double = not should_double
    return total % 10 == 0


def validate_card_details(card_number, expiry, cvv, name):
    if not name or not card_number or not expiry or not cvv:
        return False, "Please complete all card fields."

    if not luhn_checksum(card_number):
        return False, "Card number is invalid."

    if not re.match(r"^(0[1-9]|1[0-2])/(\d{2})$", expiry):
        return False, "Expiry must be in MM/YY format."

    if not re.match(r"^\d{3,4}$", cvv):
        return False, "CVV must be 3 or 4 digits."

    return True, "Card validated successfully."


@app.route('/cars', methods=['GET'])
def get_cars():
    return jsonify(CARS)


@app.route('/cart', methods=['POST', 'GET'])
def cart():
    payload = request.get_json(silent=True) or {}
    username = payload.get('username') or 'guest'
    car_id = payload.get('car_id')

    if request.method == 'POST' and car_id is not None:
        car = next((c for c in CARS if c['id'] == int(car_id)), None)
        if car:
            CARTS.setdefault(username, []).append(car)
            return jsonify({"message": f"{car['make']} added to cart!", "currency": "USD"})

    user_cart = CARTS.get(username, [])
    total = sum(item['price'] for item in user_cart)
    return jsonify({"cart": user_cart, "total": total, "currency": "USD"})


@app.route('/checkout', methods=['POST'])
def checkout():
    payload = request.get_json(silent=True) or {}
    username = payload.get('username') or 'guest'
    card_number = payload.get('card_number', '')
    expiry = payload.get('expiry', '')
    cvv = payload.get('cvv', '')
    card_name = payload.get('card_name', '')

    user_cart = CARTS.get(username, [])
    if not user_cart:
        return jsonify({"error": "Cart is empty"}), 400

    valid, message = validate_card_details(card_number, expiry, cvv, card_name)
    if not valid:
        return jsonify({"error": message}), 400

    total = sum(item['price'] for item in user_cart)
    order_id = f"MH-{len(ORDERS) + 1:04d}"
    ORDERS[order_id] = {
        "username": username,
        "items": [item['make'] for item in user_cart],
        "total": total,
        "currency": "USD",
        "card_last4": card_number[-4:]
    }
    CARTS[username] = []

    return jsonify({
        "message": "Checkout complete",
        "order_id": order_id,
        "total": total,
        "currency": "USD",
        "card_last4": card_number[-4:]
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)