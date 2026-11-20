
import sqlite3
import os

DB_PATH = os.environ.get("DATABASE_PATH", "database.db")


def initialize_database():
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            age INTEGER,
            preferred_category TEXT
        )
    """)

    # Create products table
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

    # Create product views table
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

    # Create cart table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cart_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (product_id) REFERENCES products(id),
            UNIQUE(user_id, product_id)
        )
    """)

    # Create purchases table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            purchased_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)

    # Product catalog
    products = [
        ("Nova X Pro", "Smartphones", 899.00,
         "Powerful performance for everyday life.", "phone.png"),

        ("AirBeat Pro", "Audio", 249.00,
         "Immersive sound wherever you go.", "headphones.png"),

        ("Nexa Watch", "Wearables", 329.00,
         "Your day, connected and smarter.", "watch.png"),

        ("Nexa Tab Air", "Tablets", 649.00,
         "Work and entertainment anywhere.", "tablet.png"),

        ("NexaBook Pro", "Computers", 1199.00,
         "Powerful performance in a sleek and portable design.", "laptop.png"),

        ("Nexa Buds Pro", "Audio", 149.00,
         "Compact wireless earbuds with immersive sound.", "earbuds.png"),

        ("Nexa Power 20K", "Accessories", 79.00,
         "Portable power for your devices wherever you go.", "powerbank.png"),

        ("Nexa Sound", "Audio", 129.00,
         "Portable wireless sound with powerful performance.", "speaker.png"),

        ("Nexa Gaming Mouse", "Gaming", 89.00,
         "Precision and comfort designed for gaming.", "mouse.png"),

        ("Nexa Keys", "Gaming", 119.00,
         "Wireless keyboard with a modern illuminated design.", "keyboard.png"),

        ("Nexa Fit", "Wearables", 99.00,
         "Track your activity and stay connected every day.", "fitness-band.png"),

        ("Nexa Shield Case", "Accessories", 39.00,
         "Stylish everyday protection for your smartphone.", "phone-case.png"),

        ("Nexa Charge", "Accessories", 59.00,
         "Fast and convenient wireless charging.", "wireless-charger.png"),

        ("Nexa Drive", "Storage", 139.00,
         "Fast portable storage in a compact premium design.", "ssd.png"),

        ("Nexa Hub", "Accessories", 69.00,
         "Connect all your essential devices through one compact hub.", "usb-hub.png")
    ]

    # Insert products only if catalog is empty
    cursor.execute("SELECT COUNT(*) FROM products")
    product_count = cursor.fetchone()[0]

    if product_count == 0:
        cursor.executemany("""
            INSERT INTO products
            (name, category, price, description, image)
            VALUES (?, ?, ?, ?, ?)
        """, products)

        print(f"{len(products)} products added.")
    else:
        print("Products already exist. No changes made.")

    connection.commit()
    connection.close()

    print("Nexora database ready!")


if __name__ == "__main__":
    initialize_database()
