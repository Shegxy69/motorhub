from flask import Flask, request, render_template_string
import urllib.request, json, os

app = Flask(__name__)
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:5000")


def get_car_options():
    try:
        req = urllib.request.Request(f"{BACKEND_URL}/cars")
        data = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
        return "".join(
            f'<option value="{car["id"]}">{car["make"]} ({car.get("currency", "USD")} {car["price"]})</option>'
            for car in data
        )
    except Exception:
        return ""


HTML_PAGE = """
<h1>Welcome to MotorHub</h1>
<h3>1. Authenticate</h3>
<form method="POST" action="/action">
    <input type="hidden" name="form_type" value="auth">
    <input type="text" name="username" placeholder="Username" required>
    <input type="password" name="password" placeholder="Password" required>
    <select name="action">
        <option value="signup">Sign Up</option>
        <option value="signin">Sign In</option>
    </select>
    <button type="submit">Submit</button>
</form>

<h3>2. Showroom & Cart</h3>
<form method="POST" action="/action">
    <input type="hidden" name="form_type" value="cart">
    <input type="text" name="username" placeholder="Confirm Username" required>
    <select name="car_id">
        {{ car_options|safe }}
    </select>
    <button type="submit">Add to Cart</button>
</form>

<hr>
<p><b>System Message:</b> {{ result }}</p>
<p><b>Your Cart Total:</b> {{ currency }} {{ total }}</p>
"""

@app.route('/')
def index():
    return render_template_string(HTML_PAGE, result="", total=0, currency="USD", car_options=get_car_options())

@app.route('/action', methods=['POST'])
def handle_action():
    form_type = request.form['form_type']
    username = request.form['username']
    message = ""
    total = 0
    currency = "USD"

    try:
        if form_type == 'auth':
            data = json.dumps({"username": username, "password": request.form['password'], "action": request.form['action']}).encode('utf-8')
            req = urllib.request.Request(f"{BACKEND_URL}/auth", data=data, headers={'Content-Type': 'application/json'})
            message = json.loads(urllib.request.urlopen(req).read().decode('utf-8')).get("message")

        elif form_type == 'cart':
            data = json.dumps({"username": username, "car_id": request.form['car_id']}).encode('utf-8')
            req = urllib.request.Request(f"{BACKEND_URL}/cart", data=data, headers={'Content-Type': 'application/json'})
            response = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
            message = response.get("message")

        # Always fetch updated cart total
        req_cart = urllib.request.Request(f"{BACKEND_URL}/cart", data=json.dumps({"username": username}).encode('utf-8'), headers={'Content-Type': 'application/json'})
        cart_response = json.loads(urllib.request.urlopen(req_cart).read().decode('utf-8'))
        total = cart_response.get("total", 0)
        currency = cart_response.get("currency", "USD")

    except Exception as e:
        message = f"Error: {str(e)}"

    return render_template_string(
        HTML_PAGE,
        result=message,
        total=total,
        currency=currency,
        car_options=get_car_options()
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)