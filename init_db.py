import sqlite3
from werkzeug.security import generate_password_hash


# -------------------------
# DATABASE CONNECTION
# -------------------------

connection = sqlite3.connect("database.db")
cursor = connection.cursor()


# -------------------------
# CREATE PRODUCTS TABLE
# -------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    price REAL NOT NULL,
    description TEXT,
    image TEXT
)
""")


# -------------------------
# CREATE USERS TABLE
# -------------------------

# We recreate the users table during development
# because its structure has changed.
cursor.execute("DROP TABLE IF EXISTS users")

cursor.execute("""
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    age INTEGER,
    preferred_category TEXT
)
""")


# -------------------------
# CLEAR PRODUCTS
# -------------------------

cursor.execute("DELETE FROM products")


# -------------------------
# PRODUCTS DATA
# -------------------------

products = [
    (
        "Nova X Pro",
        "Smartphones",
        899.00,
        "Powerful performance for everyday life.",
        "phone.png"
    ),
    (
        "AirBeat Pro",
        "Audio",
        249.00,
        "Immersive sound wherever you go.",
        "headphones.png"
    ),
    (
        "Nexa Watch",
        "Wearables",
        329.00,
        "Your day, connected and smarter.",
        "watch.png"
    ),
    (
        "Nexa Tab Air",
        "Tablets",
        649.00,
        "Work and entertainment anywhere.",
        "tablet.png"
    ),
    (
        "NexaBook Pro",
        "Computers",
        1199.00,
        "Powerful performance in a sleek and portable design.",
        "laptop.png"
    ),
    (
        "Nexa Buds Pro",
        "Audio",
        149.00,
        "Compact wireless earbuds with immersive sound.",
        "earbuds.png"
    ),
    (
        "Nexa Power 20K",
        "Accessories",
        79.00,
        "Portable power for your devices wherever you go.",
        "powerbank.png"
    ),
    (
        "Nexa Sound",
        "Audio",
        129.00,
        "Portable wireless sound with powerful performance.",
        "speaker.png"
    ),
    (
        "Nexa Gaming Mouse",
        "Gaming",
        89.00,
        "Precision and comfort designed for gaming.",
        "mouse.png"
    ),
    (
        "Nexa Keys",
        "Gaming",
        119.00,
        "Wireless keyboard with a modern illuminated design.",
        "keyboard.png"
    ),
    (
        "Nexa Fit",
        "Wearables",
        99.00,
        "Track your activity and stay connected every day.",
        "fitness-band.png"
    ),
    (
        "Nexa Shield Case",
        "Accessories",
        39.00,
        "Stylish everyday protection for your smartphone.",
        "phone-case.png"
    ),
    (
        "Nexa Charge",
        "Accessories",
        59.00,
        "Fast and convenient wireless charging.",
        "wireless-charger.png"
    ),
    (
        "Nexa Drive",
        "Storage",
        139.00,
        "Fast portable storage in a compact premium design.",
        "ssd.png"
    ),
    (
        "Nexa Hub",
        "Accessories",
        69.00,
        "Connect all your essential devices through one compact hub.",
        "usb-hub.png"
    )
]


# -------------------------
# INSERT PRODUCTS
# -------------------------

cursor.executemany("""
INSERT INTO products (
    name,
    category,
    price,
    description,
    image
)
VALUES (?, ?, ?, ?, ?)
""", products)


# -------------------------
# DEMO USERS DATA
# -------------------------

users = [
    (
        "Maria",
        "maria@nexora.com",
        generate_password_hash("maria123", method="pbkdf2:sha256"),
        25,
        "Smartphones"
    ),
    (
        "Nikos",
        "nikos@nexora.com",
        generate_password_hash("nikos123", method="pbkdf2:sha256"),
        31,
        "Gaming"
    ),
    (
        "Eleni",
        "eleni@nexora.com",
        generate_password_hash("eleni123", method="pbkdf2:sha256"),
        28,
        "Wearables"
    )
]


# -------------------------
# INSERT USERS
# -------------------------

cursor.executemany("""
INSERT INTO users (
    name,
    email,
    password_hash,
    age,
    preferred_category
)
VALUES (?, ?, ?, ?, ?)
""", users)


# -------------------------
# CREATE PRODUCT VIEWS TABLE
# -------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS product_views (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
)
""")

# -------------------------
# SAVE DATABASE
# -------------------------

connection.commit()
connection.close()


print("Nexora database initialized successfully!")
print(f"{len(products)} products added.")
print(f"{len(users)} users added.")