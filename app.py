from flask import Flask, render_template, request, redirect, jsonify
import sqlite3
import os

app = Flask(__name__)

# --- Database Setup ---
DB_NAME = "cart.db"

def init_db():
    """Initializes SQLite database for storing cart items."""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS cart (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            price REAL NOT NULL,
            quantity INTEGER DEFAULT 1
        )
    """)
    conn.commit()
    conn.close()

# --- Helper Function ---
def get_cart_items():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT * FROM cart")
    items = cur.fetchall()
    conn.close()
    total = sum(item[2] * item[3] for item in items)
    return items, total

# --- Routes ---
@app.route("/")
def home():
    """Homepage route"""
    return render_template("index.html")

@app.route("/products")
def product_page():
    """Products page"""
    return render_template("product.html")

@app.route("/cart")
def cart_page():
    """Display shopping cart"""
    items, total = get_cart_items()
    return render_template("cart.html", items=items, total=total)

@app.route("/profile")
def profile_page():
    """Profile page"""
    return render_template("profile.html")

@app.route("/contact")
def contact_page():
    """Contact page"""
    return render_template("contact.html")

# --- Cart Operations ---
@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    """Add a product to cart (called via JS fetch API)."""
    data = request.get_json()
    product = data.get("product_name")
    price = float(data.get("price", 0))

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT * FROM cart WHERE product_name=?", (product,))
    existing = cur.fetchone()

    if existing:
        cur.execute("UPDATE cart SET quantity = quantity + 1 WHERE product_name=?", (product,))
    else:
        cur.execute("INSERT INTO cart (product_name, price, quantity) VALUES (?, ?, ?)",
                    (product, price, 1))
    conn.commit()
    conn.close()

    return jsonify({"message": f"{product} added to cart ✅"}), 200

@app.route("/remove_item/<int:item_id>", methods=["POST"])
def remove_item(item_id):
    """Remove a specific item from cart."""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("DELETE FROM cart WHERE id=?", (item_id,))
    conn.commit()
    conn.close()
    return redirect("/cart")

@app.route("/clear_cart", methods=["POST"])
def clear_cart():
    """Clear the entire shopping cart."""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("DELETE FROM cart")
    conn.commit()
    conn.close()
    return redirect("/cart")

# --- Run App ---
if __name__ == "__main__":
    if not os.path.exists(DB_NAME):
        init_db()

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
