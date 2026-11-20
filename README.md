
# NEXORA
### Personalized E-Commerce Recommendation System

Nexora is a web-based e-commerce application developed as a university project for the course **Software Personalization Technologies**.

The application provides personalized product recommendations based on user preferences, browsing behavior, and purchase history.

It uses a **rule-based recommendation engine** and **stereotype-based user profiling** to dynamically adapt product suggestions to each user's interests.

## Technologies Used

- Python
- Flask
- SQLite
- HTML5
- CSS3
- JavaScript
- Jinja2
- Werkzeug (password hashing)

## Main Features

### User Authentication
- User registration and login
- Secure password hashing
- User sessions
- Preferred product category selection during registration

### Product Catalog
- Product browsing
- Product categories
- Product detail pages
- Responsive product cards

### Shopping Cart
- Add products to cart
- Increase or decrease quantities
- Remove products
- Calculate total price
- Simulated checkout

### Purchase History
- Record completed simulated purchases
- Display previous orders
- Associate purchases with individual users

### Personalized Recommendations
- Track product detail views
- Analyze purchase history
- Calculate category interest scores
- Recommend products from up to three top-interest categories
- Display explanations for recommendations

### User Interest Profile
- Display preferred category
- Show interest scores and progress bars
- Identify the highest-interest category
- Assign a stereotype-based user profile

## Personalization Algorithm

Nexora uses a rule-based scoring system to estimate user interests.

| User Activity | Interest Score |
|---------------|----------------|
| Declared preferred category | +2 points |
| Product detail view | +1 point |
| Purchased product unit | +3 points |

The total interest score for a category is calculated as:

```text
Interest Score =
    (2 × Declared Preference)
  + (1 × Product Views)
  + (3 × Purchased Units)
```

The recommendation engine:

1. Retrieves the user's preferred category.
2. Counts product views by category.
3. Counts purchased units by category.
4. Calculates interest scores using predefined rules.
5. Ranks categories by interest score.
6. Selects up to three highest-scoring categories.
7. Recommends up to two products from each selected category.

Only categories currently available in the product catalog are considered.

If no interest data is available, the homepage displays a selection of general products.

## Stereotype-Based User Profiling

Nexora classifies users into predefined interest-based stereotypes according to their highest-scoring category.

| Product Category | User Stereotype |
|------------------|-----------------|
| Gaming | Gaming Enthusiast |
| Audio | Audio Lover |
| Smartphones | Smartphone Enthusiast |
| Wearables | Wearables Enthusiast |
| Computers | Computer Enthusiast |
| Tablets | Tablet Enthusiast |
| Accessories | Accessories Enthusiast |
| Storage | Storage Enthusiast |

Users without sufficient interest data are assigned the profile:

**General Tech Explorer**

Stereotype classification is dynamically updated as user behavior changes.

## Database

Nexora uses SQLite to store application data.

Main database tables:

| Table | Purpose |
|-------|---------|
| users | User accounts and preferences |
| products | Product catalog |
| product_views | Browsing activity |
| purchases | Simulated purchase history |
| cart_items | Shopping cart contents |

## Project Structure

```text
Nexora/
├── app.py
├── database.db
├── init_db.py
├── create_views_table.py
├── create_purchases_table.py
├── create_cart_table.py
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── login.html
│   ├── register.html
│   ├── products.html
│   ├── product.html
│   ├── cart.html
│   ├── order_success.html
│   ├── purchase_history.html
│   └── preferences.html
├── static/
│   ├── css/
│   │   └── style.css
│   └── images/
└── README.md
```

## Installation and Setup

### 1. Requirements

- Python 3.9 or newer
- pip
- A web browser

### 2. Open the project directory

```bash
cd Nexora
```

### 3. Create a virtual environment

```bash
python3 -m venv venv
```

### 4. Activate the virtual environment

macOS / Linux:

```bash
source venv/bin/activate
```

Windows:

```bash
venv\Scripts\activate
```

### 5. Install dependencies

```bash
pip install Flask
```

### 6. Run the application

```bash
python app.py
```

### 7. Open the application

Visit:

http://127.0.0.1:5000

The application requires a pre-populated SQLite database (`database.db`) containing the necessary tables and products.

**Important:** Do not run `init_db.py` on an existing database, as it may reset stored data.

## Example Personalization Scenario

Consider two users with different browsing and purchase histories.

**User A: Maria**

- Top interest: Audio
- Audio interest score: 8
- Assigned stereotype: Audio Lover

**User B: Nikos**

- Top interest: Wearables
- Wearables interest score: 8
- Assigned stereotype: Wearables Enthusiast

Although both users access the same e-commerce platform, Nexora generates different product recommendations based on their individual interest profiles.

## Academic Context

This application was developed for the university course:

**Software Personalization Technologies**

Project topic:

**Software Personalization Technologies for Product Recommendations in E-Commerce**

The project demonstrates how rule-based inference, implicit user behavior tracking, and stereotype-based profiling can be used to provide personalized recommendations.

## Limitations

- The recommendation engine uses predefined rules rather than machine learning.
- Recommendations are based primarily on product category interests.
- Product selection within each category follows product ID order.
- Checkout is simulated and does not process real payments.
- The application is intended for academic demonstration rather than production deployment.

## Future Improvements

- Collaborative filtering
- Content-based product recommendations
- Machine learning-based user profiling
- Personalized promotions
- More advanced recommendation explanations
- User preference editing
- Recommendation evaluation metrics

## License

Developed for educational and academic purposes.
