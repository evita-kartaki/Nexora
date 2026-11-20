from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = "nexora-secret-key"


# -------------------------
# DATABASE CONNECTION
# -------------------------

def get_db_connection():
    connection = sqlite3.connect("database.db")
    connection.row_factory = sqlite3.Row
    return connection


# -------------------------
# PERSONALIZATION ENGINE
# -------------------------

def calculate_interest_scores(connection, user_id, preferred_category):

    # Get categories that currently have products
    category_rows = connection.execute("""
        SELECT DISTINCT category
        FROM products
        WHERE category IS NOT NULL
          AND TRIM(category) != ''
    """).fetchall()

    available_categories = {
        row["category"] for row in category_rows
    }

    interest_scores = {}

    # Declared preference = +2 points
    if preferred_category in available_categories:
        interest_scores[preferred_category] = 2

    # Product views = +1 point per view
    viewed_categories = connection.execute("""
        SELECT products.category, COUNT(*) AS view_count
        FROM product_views
        JOIN products
            ON product_views.product_id = products.id
        WHERE product_views.user_id = ?
        GROUP BY products.category
    """, (user_id,)).fetchall()

    for row in viewed_categories:
        category = row["category"]

        if category in available_categories:
            interest_scores[category] = (
                interest_scores.get(category, 0)
                + row["view_count"]
            )

    # Purchases = +3 points per purchased unit
    purchased_categories = connection.execute("""
        SELECT products.category, COUNT(*) AS purchase_count
        FROM purchases
        JOIN products
            ON purchases.product_id = products.id
        WHERE purchases.user_id = ?
        GROUP BY products.category
    """, (user_id,)).fetchall()

    for row in purchased_categories:
        category = row["category"]

        if category in available_categories:
            interest_scores[category] = (
                interest_scores.get(category, 0)
                + row["purchase_count"] * 3
            )

    return interest_scores, available_categories


# -------------------------
# STEREOTYPE-BASED USER PROFILE
# -------------------------

def classify_user_stereotype(interest_scores):

    stereotypes = {
        "Gaming": "Gaming Enthusiast",
        "Audio": "Audio Lover",
        "Smartphones": "Smartphone Enthusiast",
        "Wearables": "Wearables Enthusiast",
        "Computers": "Computer Enthusiast",
        "Tablets": "Tablet Enthusiast",
        "Accessories": "Accessories Enthusiast",
        "Storage": "Storage Enthusiast"
    }

    if not interest_scores:
        return "General Tech Explorer"

    # Find category with highest interest score
    top_category = sorted(
        interest_scores.items(),
        key=lambda item: (-item[1], item[0])
    )[0][0]

    return stereotypes.get(
        top_category,
        "General Tech Explorer"
    )


# -------------------------
# CART COUNTER
# -------------------------

@app.context_processor
def inject_cart_count():

    if "user_id" not in session:
        return {"cart_count": 0}

    connection = get_db_connection()

    result = connection.execute("""
        SELECT COALESCE(SUM(quantity), 0) AS total
        FROM cart_items
        WHERE user_id = ?
    """, (session["user_id"],)).fetchone()

    connection.close()

    return {"cart_count": result["total"]}


# -------------------------
# HOME
# -------------------------


@app.route("/")
def home():

    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()

    user = connection.execute("""
        SELECT *
        FROM users
        WHERE id = ?
    """, (session["user_id"],)).fetchone()

    if user is None:
        connection.close()
        session.clear()
        return redirect(url_for("login"))

    # Calculate personalized interest scores
    interest_scores, available_categories = calculate_interest_scores(
        connection,
        session["user_id"],
        user["preferred_category"]
    )

    # Sort categories from highest to lowest score
    sorted_interests = sorted(
        interest_scores.items(),
        key=lambda item: (-item[1], item[0])
    )

    # Select up to 3 categories
    top_categories = [
        category
        for category, score in sorted_interests[:3]
    ]

    recommendation_category = (
        top_categories[0]
        if top_categories
        else None
    )

    recommendation_score = (
        interest_scores[recommendation_category]
        if recommendation_category
        else 0
    )

    # Get up to 2 products per category
    recommended_products = []

    for category in top_categories:

        category_products = connection.execute("""
            SELECT *
            FROM products
            WHERE category = ?
            ORDER BY id
            LIMIT 2
        """, (category,)).fetchall()

        for product in category_products:

            recommended_products.append({
                "id": product["id"],
                "name": product["name"],
                "category": product["category"],
                "price": product["price"],
                "description": product["description"],
                "image": product["image"],
                "reason": (
                    "Recommended based on your interest in "
                    + category
                )
            })

    # If no interest data exists, show a few products
    if not recommended_products:

        fallback_products = connection.execute("""
            SELECT *
            FROM products
            ORDER BY id
            LIMIT 6
        """).fetchall()

        for product in fallback_products:

            recommended_products.append({
                "id": product["id"],
                "name": product["name"],
                "category": product["category"],
                "price": product["price"],
                "description": product["description"],
                "image": product["image"],
                "reason": "Explore our products"
            })

    connection.close()

    return render_template(
        "home.html",
        user=user,
        products=recommended_products,
        recommendation_category=recommendation_category,
        recommendation_score=recommendation_score,
        interest_scores=interest_scores,
        top_categories=top_categories
    )



# -------------------------
# ALL PRODUCTS
# -------------------------

@app.route("/products")
def products():

    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()

    all_products = connection.execute("""
        SELECT *
        FROM products
        ORDER BY category, name
    """).fetchall()

    connection.close()

    return render_template(
        "products.html",
        products=all_products,
        selected_category="All"
    )


# -------------------------
# PRODUCTS BY CATEGORY
# -------------------------

@app.route("/category/<category>")
def category_products(category):

    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()

    category_items = connection.execute("""
        SELECT *
        FROM products
        WHERE category = ?
        ORDER BY name
    """, (category,)).fetchall()

    connection.close()

    return render_template(
        "products.html",
        products=category_items,
        selected_category=category
    )


# -------------------------
# PRODUCT DETAILS
# -------------------------

@app.route("/product/<int:product_id>")
def product_details(product_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()

    product = connection.execute("""
        SELECT *
        FROM products
        WHERE id = ?
    """, (product_id,)).fetchone()

    if product is None:
        connection.close()
        return "Product not found", 404


    # -------------------------
    # RECORD PRODUCT VIEW
    # -------------------------

    connection.execute("""
        INSERT INTO product_views (
            user_id,
            product_id
        )
        VALUES (?, ?)
    """, (
        session["user_id"],
        product_id
    ))

    connection.commit()
    connection.close()


    return render_template(
        "product.html",
        product=product
    )


# -------------------------
# ADD TO CART
# -------------------------

@app.route("/add-to-cart/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()

    # Check if product exists
    product = connection.execute("""
        SELECT id
        FROM products
        WHERE id = ?
    """, (product_id,)).fetchone()

    if product is None:
        connection.close()
        return "Product not found", 404

    # Check if product is already in cart
    cart_item = connection.execute("""
        SELECT *
        FROM cart_items
        WHERE user_id = ? AND product_id = ?
    """, (session["user_id"], product_id)).fetchone()

    if cart_item:
        # Increase quantity
        connection.execute("""
            UPDATE cart_items
            SET quantity = quantity + 1
            WHERE id = ?
        """, (cart_item["id"],))
    else:
        # Add new item
        connection.execute("""
            INSERT INTO cart_items (user_id, product_id, quantity)
            VALUES (?, ?, 1)
        """, (session["user_id"], product_id))

    connection.commit()
    connection.close()

    return redirect(url_for("cart"))


# -------------------------
# CART PAGE
# -------------------------

@app.route("/cart")
def cart():

    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()

    cart_items = connection.execute("""
        SELECT
            cart_items.id,
            cart_items.product_id,
            cart_items.quantity,
            products.name,
            products.price,
            products.image,
            products.category
        FROM cart_items
        JOIN products
            ON cart_items.product_id = products.id
        WHERE cart_items.user_id = ?
        ORDER BY cart_items.id DESC
    """, (session["user_id"],)).fetchall()

    connection.close()

    total = sum(
        item["price"] * item["quantity"]
        for item in cart_items
    )

    return render_template(
        "cart.html",
        cart_items=cart_items,
        total=total
    )


# -------------------------
# REMOVE FROM CART
# -------------------------

@app.route("/cart/remove/<int:item_id>", methods=["POST"])
def remove_from_cart(item_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()

    connection.execute("""
        DELETE FROM cart_items
        WHERE id = ? AND user_id = ?
    """, (item_id, session["user_id"]))

    connection.commit()
    connection.close()

    return redirect(url_for("cart"))


# -------------------------
# BUY PRODUCT
# -------------------------

@app.route("/buy/<int:product_id>", methods=["POST"])
def buy_product(product_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()

    product = connection.execute("""
        SELECT *
        FROM products
        WHERE id = ?
    """, (product_id,)).fetchone()

    if product is None:
        connection.close()
        return "Product not found", 404


    # Record purchase
    connection.execute("""
        INSERT INTO purchases (
            user_id,
            product_id
        )
        VALUES (?, ?)
    """, (
        session["user_id"],
        product_id
    ))

    connection.commit()
    connection.close()

    return redirect(url_for("home"))


# -------------------------
# REGISTER
# -------------------------

@app.route("/register", methods=["GET", "POST"])
def register():

    error = None

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        age = request.form["age"]
        preferred_category = request.form["preferred_category"]

        connection = get_db_connection()

        existing_user = connection.execute("""
            SELECT *
            FROM users
            WHERE email = ?
        """, (email,)).fetchone()


        if existing_user:

            error = "An account with this email already exists."

        else:

            password_hash = generate_password_hash(
                password,
                method="pbkdf2:sha256"
            )

            cursor = connection.execute("""
                INSERT INTO users (
                    name,
                    email,
                    password_hash,
                    age,
                    preferred_category
                )
                VALUES (?, ?, ?, ?, ?)
            """, (
                name,
                email,
                password_hash,
                age,
                preferred_category
            ))

            connection.commit()

            session["user_id"] = cursor.lastrowid
            session["user_name"] = name

            connection.close()

            return redirect(url_for("home"))

        connection.close()


    return render_template(
        "register.html",
        error=error
    )


# -------------------------
# LOGIN
# -------------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    error = None

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        connection = get_db_connection()

        user = connection.execute("""
            SELECT *
            FROM users
            WHERE email = ?
        """, (email,)).fetchone()

        connection.close()


        if user and check_password_hash(
            user["password_hash"],
            password
        ):

            session["user_id"] = user["id"]
            session["user_name"] = user["name"]

            return redirect(url_for("home"))

        else:

            error = "Invalid email or password."


    return render_template(
        "login.html",
        error=error
    )


# -------------------------
# LOGOUT
# -------------------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


# -------------------------
# UPDATE CART QUANTITY
# -------------------------

@app.route("/cart/update/<int:item_id>", methods=["POST"])
def update_cart_quantity(item_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    action = request.form.get("action")

    if action not in ("increase", "decrease"):
        return redirect(url_for("cart"))

    connection = get_db_connection()

    item = connection.execute("""
        SELECT *
        FROM cart_items
        WHERE id = ? AND user_id = ?
    """, (item_id, session["user_id"])).fetchone()

    if item is None:
        connection.close()
        return redirect(url_for("cart"))

    if action == "increase":
        new_quantity = item["quantity"] + 1
    else:
        new_quantity = item["quantity"] - 1

    if new_quantity <= 0:
        connection.execute("""
            DELETE FROM cart_items
            WHERE id = ? AND user_id = ?
        """, (item_id, session["user_id"]))
    else:
        connection.execute("""
            UPDATE cart_items
            SET quantity = ?
            WHERE id = ? AND user_id = ?
        """, (new_quantity, item_id, session["user_id"]))

    connection.commit()
    connection.close()

    return redirect(url_for("cart"))


# -------------------------
# CHECKOUT
# -------------------------

@app.route("/cart/checkout", methods=["POST"])
def checkout():

    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()

    cart_items = connection.execute("""
        SELECT product_id, quantity
        FROM cart_items
        WHERE user_id = ?
    """, (session["user_id"],)).fetchall()

    if not cart_items:
        connection.close()
        return redirect(url_for("cart"))

    # Record purchases
    for item in cart_items:
        for _ in range(item["quantity"]):
            connection.execute("""
                INSERT INTO purchases (user_id, product_id)
                VALUES (?, ?)
            """, (
                session["user_id"],
                item["product_id"]
            ))

    # Empty the cart after checkout
    connection.execute("""
        DELETE FROM cart_items
        WHERE user_id = ?
    """, (session["user_id"],))

    connection.commit()
    connection.close()

    return redirect(url_for("order_success"))


# -------------------------
# ORDER SUCCESS
# -------------------------

@app.route("/order-success")
def order_success():

    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template("order_success.html")


# -------------------------
# PURCHASE HISTORY
# -------------------------

@app.route("/purchase-history")
def purchase_history():

    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()

    purchases = connection.execute("""
        SELECT
            purchases.id,
            purchases.purchased_at,
            products.name,
            products.category,
            products.price,
            products.image
        FROM purchases
        JOIN products
            ON purchases.product_id = products.id
        WHERE purchases.user_id = ?
        ORDER BY purchases.purchased_at DESC, purchases.id DESC
    """, (session["user_id"],)).fetchall()

    connection.close()

    return render_template(
        "purchase_history.html",
        purchases=purchases
    )





# -------------------------
# MY PREFERENCES
# -------------------------

@app.route("/my-preferences")
def my_preferences():

    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()

    user = connection.execute("""
        SELECT name, preferred_category
        FROM users
        WHERE id = ?
    """, (session["user_id"],)).fetchone()

    if user is None:
        connection.close()
        session.clear()
        return redirect(url_for("login"))

    preferred_category = user["preferred_category"]

    # Use the shared personalization engine
    interest_scores, available_categories = calculate_interest_scores(
        connection,
        session["user_id"],
        preferred_category
    )

    connection.close()


    # Classify user into a stereotype
    user_stereotype = classify_user_stereotype(
        interest_scores
    )

    sorted_interests = sorted(
        interest_scores.items(),
        key=lambda item: (-item[1], item[0])
    )

    recommendation_category = (
        sorted_interests[0][0]
        if sorted_interests
        else None
    )

    max_score = max(
        interest_scores.values(),
        default=0
    )

    interest_bars = [
        {
            "category": category,
            "score": score,
            "percentage": (
                round(score / max_score * 100, 1)
                if max_score > 0
                else 0
            )
        }
        for category, score in sorted_interests
    ]

    return render_template(
        "preferences.html",
        user=user,
        preferred_category=(
            preferred_category
            if preferred_category in available_categories
            else "Not selected"
        ),
        recommendation_category=recommendation_category,
        interest_bars=interest_bars,
        user_stereotype=user_stereotype
    )



# -------------------------
# RUN APP
# -------------------------

if __name__ == "__main__":
    app.run(debug=True)