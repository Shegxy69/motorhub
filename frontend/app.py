from flask import Flask, request, render_template_string
import urllib.request, json, os

app = Flask(__name__)
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:5000")


def get_backend_json(path, payload=None):
    data = None if payload is None else json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(f"{BACKEND_URL}{path}", data=data, headers={'Content-Type': 'application/json'})
    return json.loads(urllib.request.urlopen(req).read().decode('utf-8'))


def get_car_cards(username='guest'):
    try:
        cars = get_backend_json('/cars')
        cards = []
        for car in cars:
            cards.append(f'''
                <div style="border:1px solid #ddd; border-radius:12px; overflow:hidden; max-width:260px; margin:12px; background:white;">
                    <img src="{car.get('image', '')}" alt="{car['make']}" style="width:100%; height:170px; object-fit:cover;">
                    <div style="padding:12px;">
                        <h4>{car['make']}</h4>
                        <p>{car.get('currency', 'USD')} {car['price']}</p>
                        <form method="POST" action="/action">
                            <input type="hidden" name="form_type" value="cart">
                            <input type="hidden" name="username" value="{username}">
                            <input type="hidden" name="car_id" value="{car['id']}">
                            <button type="submit">Add to cart</button>
                        </form>
                    </div>
                </div>
            ''')
        return "".join(cards)
    except Exception:
        return ""


HTML_PAGE = """
<!doctype html>
<html>
<head>
    <title>MotorHub</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f7f7f7; margin: 0; padding: 24px; }
        .container { max-width: 1100px; margin: 0 auto; }
        .grid { display: flex; flex-wrap: wrap; gap: 16px; }
        form { margin-bottom: 18px; }
        input, select, button { padding: 8px 10px; margin: 4px 0; }
        .summary { padding: 16px; background: white; border-radius: 12px; border: 1px solid #ddd; }
        .checkout-box { background: white; border: 1px solid #ddd; border-radius: 12px; padding: 18px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>MotorHub Store</h1>

        <div class="summary">
            <p><b>Cart Total:</b> {{ currency }} {{ total }}</p>
            <p><b>System Message:</b> {{ result }}</p>
        </div>

        <h3>Choose your car</h3>
        <div class="grid">
            {{ car_cards|safe }}
        </div>

        <div class="checkout-box">
            <h3>Checkout</h3>
            <form method="POST" action="/action">
                <input type="hidden" name="form_type" value="checkout">
                <input type="text" name="username" value="guest" placeholder="Guest name" required><br>
                <input type="text" name="card_name" placeholder="Name on card" required><br>
                <input type="text" name="card_number" placeholder="Card number" required><br>
                <input type="text" name="expiry" placeholder="MM/YY" required><br>
                <input type="text" name="cvv" placeholder="CVV" required><br>
                <button type="submit">Pay now</button>
            </form>
        </div>
    </div>
</body>
</html>
"""


@app.route('/')
def index():
    try:
        cart_response = get_backend_json('/cart', {'username': 'guest'})
        total = cart_response.get('total', 0)
        currency = cart_response.get('currency', 'USD')
    except Exception:
        total = 0
        currency = 'USD'

    return render_template_string(
        HTML_PAGE,
        result="",
        total=total,
        currency=currency,
        car_cards=get_car_cards('guest')
    )


@app.route('/action', methods=['POST'])
def handle_action():
    form_type = request.form['form_type']
    username = request.form.get('username', 'guest')
    message = ""
    total = 0
    currency = "USD"

    try:
        if form_type == 'cart':
            payload = {"username": username, "car_id": request.form['car_id']}
            response = get_backend_json('/cart', payload)
            message = response.get("message")

        elif form_type == 'checkout':
            payload = {
                "username": username,
                "card_name": request.form.get('card_name', ''),
                "card_number": request.form.get('card_number', ''),
                "expiry": request.form.get('expiry', ''),
                "cvv": request.form.get('cvv', '')
            }
            response = get_backend_json('/checkout', payload)
            message = response.get("message", "Checkout complete")

        cart_response = get_backend_json('/cart', {'username': username})
        total = cart_response.get("total", 0)
        currency = cart_response.get("currency", "USD")
    except Exception as e:
        message = f"Error: {str(e)}"

    return render_template_string(
        HTML_PAGE,
        result=message,
        total=total,
        currency=currency,
        car_cards=get_car_cards(username)
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)