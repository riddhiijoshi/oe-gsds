from flask import Flask, render_template, request, jsonify, redirect, url_for
from pymongo import MongoClient
import bcrypt

app = Flask(__name__)

client = MongoClient("mongodb+srv://pranaybhandekar8841:73gUQjssxcijpJDD@cluster2.cnwqzic.mongodb.net/?retryWrites=true&w=majority&appName=Cluster2") 
db = client["e-commerce"]
products_collection = db["products"]
carts_collection = db["carts"]
user_collection = db["user"]

@app.route('/')
def index():
    # Get the user_id from the query parameters
    user_id = request.args.get('user_id')
    
    # Fetch products from the database
    products = list(products_collection.find())
    
    # Render the index.html template with products and user_id
    return render_template('index.html', products=products, user_id=user_id)

@app.route("/signin", methods=['GET'])
def signin():
    return render_template("login.html")

from flask import request

@app.route('/products', methods=['GET'])
def display_products():
    user_id = request.args.get('user_id')
    products = list(products_collection.find({}, {"_id": 0}))
    return render_template('product.html', products=products, user_id=user_id)


@app.route("/signup", methods=["GET"])
def signup():
    return render_template("signup.html")

from flask import jsonify

@app.route('/register', methods=['POST'])
def register():
    # Get form data
    username = request.form.get('username')
    email = request.form.get('email')
    phone = request.form.get('phone')
    password = request.form.get('password')

    # Check if username or email already exists in the database
    existing_user = user_collection.find_one({"$or": [{"username": username}, {"email": email}]})
    if existing_user:
        return jsonify({'error': 'Username or email already exists'}), 400

    # Insert new user into the database
    new_user = {
        "username": username,
        "email": email,
        "phone": phone,
        "password": password  # Store password as plain text (not recommended)
    }
    user_collection.insert_one(new_user)

    return jsonify({'message': 'User registered successfully'}), 201


@app.route('/login', methods=['POST'])
def login():
    # Retrieve email and password from the request
    email = request.json.get('email')
    password = request.json.get('password')

    # Find the user in the database
    user = user_collection.find_one({"email": email})

    # Check if the user exists and if the password matches
    if user and user['password'] == password:
        # Fetch the user ID
        user_id = str(user['_id'])
        return jsonify({'user_id': user_id})  # Return user_id to the client
    else:
        return jsonify({'error': 'Invalid email or password'}), 401



@app.route('/logout')
def logout():
    return redirect(url_for('index'))



@app.route('/add_product', methods=['POST'])
def add_product():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON data'}), 400

    result = products_collection.insert_one(data)
    new_product = products_collection.find_one({"_id": result.inserted_id}, {"_id": 0})
    return jsonify(new_product), 201

@app.route('/search_products', methods=['GET'])
def search_products():
    keyword = request.args.get('keyword')
    if not keyword:
        return jsonify({'error': 'Please provide a keyword to search for'}), 400

    matching_products = list(products_collection.find({
        "$or": [
            {"name": {"$regex": keyword, "$options": "i"}},
            {"description": {"$regex": keyword, "$options": "i"}}
        ]
    }, {"_id": 0}))

    if not matching_products:
        return jsonify({'message': 'No products found matching the keyword'}), 404

    print(matching_products)  # Log the matching products
    return jsonify(matching_products)

# @app.route('/cart', methods=['GET'])
# def view_cart():
#     user_id = request.args.get('user_id')
#     user_cart = carts_collection.find_one({"user_id": user_id}, {"_id": 0})
#     if user_cart:
#         return jsonify(user_cart)
#     else:
#         return jsonify({'message': 'Cart not found'}), 404

# @app.route('/add_to_cart', methods=['POST'])
# def add_to_cart():
#     data = request.get_json()
#     user_id = data.get('user_id')
#     product_id = data.get('product_id')
#     quantity = data.get('quantity', 1)

#     product = products_collection.find_one({"id": product_id}, {"_id": 0})
#     if not product:
#         return jsonify({'error': 'Product not found'}), 404

#     user_cart = carts_collection.find_one({"user_id": user_id}, {"_id": 0})
#     if not user_cart:
#         user_cart = {"user_id": user_id, "cart_items": {}}

#     cart_items = user_cart.get("cart_items")
#     cart_items[str(product_id)] = cart_items.get(str(product_id), 0) + quantity
#     user_cart["cart_items"] = cart_items

#     if carts_collection.find_one({"user_id": user_id}):
#         carts_collection.replace_one({"user_id": user_id}, user_cart)
#     else:
#         carts_collection.insert_one(user_cart)

#     return jsonify(user_cart)

# @app.route('/delete_from_cart', methods=['POST'])
# def delete_from_cart():
#     data = request.get_json()
#     user_id = data.get('user_id')
#     product_id = data.get('product_id')

#     user_cart = carts_collection.find_one({"user_id": user_id}, {"_id": 0})
#     if user_cart:
#         cart_items = user_cart.get("cart_items")
#         if str(product_id) in cart_items:
#             del cart_items[str(product_id)]
#             user_cart["cart_items"] = cart_items
#             carts_collection.replace_one({"user_id": user_id}, user_cart)

#     return jsonify(user_cart)

if __name__ == '__main__':
    app.run(debug=True)
