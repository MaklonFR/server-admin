import os
import sqlite3

from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
from flask_cors import CORS  # Import CORS
from datetime import date
from datetime import datetime

# Returns the current local date
today = date.today()
dtm = datetime.today()

# Enable CORS for a specific origin

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
myserver = "https://smkn1kuwus.sch.id/client-koperasi-boe/"

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # maximal space file 16 MB

app.secret_key = os.urandom(24)  # Secret key for session
app.config['JWT_SECRET_KEY'] = 'Web-Framework-2024'  #
bcrypt = Bcrypt(app)

# function to connect sqlite
def get_db_connection():
    conn = sqlite3.connect('db_products.db')
    conn.row_factory = sqlite3.Row
    return conn

#----------------------------------BEGIN LOGIN REGISTER-------------------------------#
# Route to login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'session_token' in session:
        return redirect(url_for('home'))
    else:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            conn = get_db_connection()
            admin = conn.execute('SELECT * FROM admin WHERE username = ?', (username,)).fetchone()
            conn.close()

            # Cek username dan password
            if admin and bcrypt.check_password_hash(admin['password'], password):
                session['session_token'] = admin['username']  # Store token in session
                #print("Token: " + access_token)
                return redirect(url_for('home'))
            return jsonify({"msg": "Login failed"}), 401
        return render_template('login.html')

#Route to pages register admin
@app.route ('/register_page')
def register_page():
    if 'session_token' in session:
        return render_template('index.html')
    else:
        return render_template("register.html")

# Route to Create register admin
@app.route('/register', methods=['POST'])
def register():
    username = request.json.get('username', None)
    password = request.json.get('password', None)

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    try:
        conn = get_db_connection()
        conn.execute('INSERT INTO admin (username, password) VALUES (?, ?)', (username, hashed_password))
        conn.commit()
        conn.close()
        return jsonify({"msg": "Admin registered successfully"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"msg": "Username already exists"}), 400

#----------------------------------END LOGIN REGISTER-------------------------------#

# Route to logout page (delete token from session)
@app.route('/logout')
def logout():
    session.pop('session_token', None)
    return redirect(url_for('login'))

@app.route ('/')
def main():
    if 'session_token' in session:
        return redirect(url_for('home'))
    else:
        return render_template("login.html")

@app.route('/home', methods=['GET'])
def home():
    if 'session_token' in session:
        return render_template('index.html')
    else:
        return render_template("login.html")

# 1. ---------------------------------BEGIN CRUD PRODUCT---------------------------------#
#Route to page list product
@app.route('/list_products')
def list_products():
    if 'session_token' in session:
        conn = get_db_connection()
        products = conn.execute('''
        SELECT 
            products.id AS product_id,
            products.name AS product_name,
            products.description AS product_description,
            products.price AS product_price,
            products.stock AS product_stock,
            products.sku AS product_sku,
            products.is_active AS product_status,
            products.image_url AS product_image_url,
            products.created_at AS product_created_at,
            products.updated_at AS product_updated_at,
            category.id AS category_id,
            category.name AS category_name,
            category.description AS category_description
        FROM 
            products
        LEFT JOIN 
            category ON products.category_id = category.id
        ''').fetchall()  # Ambil semua produk dari database
        conn.close()
        return render_template('products/list_products.html', products=products)
    else:
        return render_template("login.html")

# route to page add product
@app.route ('/add')
def add():
    if 'session_token' in session:
        conn = get_db_connection()
        cats = conn.execute('SELECT * FROM category').fetchall()  # Ambil semua produk dari database
        conn.close()
        return render_template('products/add_product.html', cats=cats)
    else:
        return render_template("login.html")

# Route to function add product
@app.route('/addProduct', methods=('GET', 'POST'))
def addproduct():
    if 'session_token' in session:
        if request.method == 'POST':
            name = request.form['namep']
            price = request.form['price']
            stock = request.form['stock']
            category_id = request.form['category']
            status = request.form['status']
            sku = request.form['sku']
            description = request.form['description']

            # Cek if file di-upload
            if 'image' not in request.files:
                return "No file part"
            file = request.files['image']

            if file.filename == '':
                return "No selected file"

            if file:
                # security filename to save in directory
                filename = secure_filename(name + '_' + file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_url = os.path.join(app.config['UPLOAD_FOLDER'], filename)  # Path file yang diupload
                conn = get_db_connection()
                conn.execute('INSERT INTO products (name, price, stock, category_id, image_url, sku, is_active, description) '
                             'VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                             (name, price, stock, category_id, image_url, sku, status, description))
                conn.commit()
                conn.close()
                flash('Save successfully!', 'success')
                return redirect(url_for('list_products'))
            # {else File not found}
        #{else Method}
    else:
        return render_template("login.html")

# route to page edit product
@app.route ('/edit')
def edit():
    if 'session_token' in session:
        return render_template("products/edit_product.html")
    else:
        return render_template("login.html")

#route show detail product for update
@app.route('/edit_product/<int:idp>',  methods=['GET', 'POST'])
def edit_product(idp):
    if 'session_token' in session:
        conn = get_db_connection()
        if idp:
            cats = conn.execute('SELECT * FROM category').fetchall()  # Ambil semua produk dari database
            data_products = conn.execute('SELECT * FROM products WHERE id = ?', (idp,)).fetchall()
            conn.close()
            return render_template('products/edit_product.html', data_products=data_products, cats=cats)
        #{else idp null/empty}
    else:
        return render_template("login.html")

# Route to update product
@app.route('/updateProduct', methods=('GET', 'POST'))
def update_product():
    if 'session_token' in session:

        if request.method == 'POST':
            idp = request.form['idproduct']
            name = request.form['namep']
            price = request.form['price']
            stock = request.form['stock']
            category_id = request.form['category']
            status = request.form['status']
            sku = request.form['sku']
            description = request.form['description']
            # Get file name from database
            image_name = request.form['image_name']
            file_path = os.path.join(image_name)

            file = request.files['image']
            if file:
                try:
                    os.remove(file_path) #remove file image old from directory
                    # security filename to save in directory
                    filename = secure_filename(name + '_' + file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename)) # save image new from in directory
                    image_url = os.path.join(app.config['UPLOAD_FOLDER'], filename)  # Path file yang diupload
                    # update proses
                    conn = get_db_connection()
                    conn.execute(
                        "UPDATE products SET name = ?, price = ?, stock = ?, category_id = ?, image_url = ?, sku = ?, is_active = ?, description = ? WHERE id = ?",
                        (name, price, stock, category_id, image_url, sku, status, description, idp))
                    conn.commit()
                    conn.close()
                    flash('Update successfully!', 'success')
                    return redirect(url_for('list_products'))  # Redirect ke halaman add product setelah submit

                except FileNotFoundError:
                    flash('File not found!', 'error')
                    return redirect(url_for('list_products'))  # Redirect ke halaman add product setelah submit
            else:
                conn = get_db_connection()
                conn.execute("UPDATE products SET name = ?, price = ?, stock = ?, category_id = ?, sku = ?, is_active = ?, description = ? WHERE id = ?",
                            (name, price, stock, category_id, sku, status, description, idp))
                conn.commit()
                conn.close()
                flash('Update successfully!', 'success')
                return redirect(url_for('list_products'))  # Redirect ke halaman add product setelah submit

        #{else method}

    else:
        return render_template("login.html")

#route delete data product
@app.route('/delete_product/<int:idp>', methods=['POST'])
def delete_product(idp):
    if 'session_token' in session:
        conn = get_db_connection()
        data_products = conn.execute('SELECT * FROM products WHERE id = ?', (idp,)).fetchone()
        print(data_products['image_url'])
        filename_product = data_products['image_url']
        try:
            os.remove(filename_product)  # remove file image old from directory
        except FileNotFoundError:
            flash('File Not Found!', 'error')
        conn.execute("DELETE FROM products WHERE id = ?", (idp,))
        conn.commit()
        conn.close()
        flash('Deleted successfully!', 'success')
        return redirect(url_for('list_products'))
    else:
        return redirect(url_for('login'))

#------------------------------------END CRUD PRODUCT-----------------------------------#

# 2. ---------------------------------BEGIN CRUD CATEGORY---------------------------------#
# route to page add category
@app.route ('/add_category')
def add_category():
    if 'session_token' in session:
        return render_template('category/add_category.html')
    else:
        return render_template("login.html")

# Route to function add category
@app.route('/addCategory', methods=('GET', 'POST'))
def addcategory():
    if 'session_token' in session:
        conn = get_db_connection()
        if request.method == 'POST':
            name = request.form['name']
            description = request.form['description']

            conn.execute('INSERT INTO category (name,description) '
                             'VALUES (?, ?)',
                             (name,description))
            conn.commit()
            conn.close()
            flash('Save successfully!', 'success')
            return redirect(url_for('list_category'))
        #{else Method}
    else:
        return render_template("login.html")

# Route to update product
@app.route('/updateCategory', methods=('GET', 'POST'))
def update_category():
    if 'session_token' in session:
        if request.method == 'POST':
            idp = request.form['idcat']
            name = request.form['name']
            description = request.form['description']
            conn = get_db_connection()
            conn.execute(
            "UPDATE category SET name = ?, description = ? WHERE id = ?",
                (name, description, idp))
            conn.commit()
            conn.close()
            flash('Update successfully!', 'success')
            return redirect(url_for('list_category'))  # Redirect ke halaman add product setelah submit
        #{else method}

    else:
        return render_template("login.html")

#Route to page list category
@app.route('/list_category')
def list_category():
    if 'session_token' in session:
        conn = get_db_connection()
        list_cats = conn.execute("SELECT * FROM category").fetchall()  # Ambil semua produk dari database
        conn.close()
        return render_template('category/list_category.html', list_cats=list_cats)
    else:
        return render_template("login.html")

#route show detail category for update
@app.route('/edit_category/<int:idc>',  methods=['GET', 'POST'])
def edit_category(idc):
    if 'session_token' in session:
        conn = get_db_connection()
        if idc:
            data_category = conn.execute('SELECT * FROM category WHERE id = ?', (idc,)).fetchall()
            conn.close()
            return render_template('category/edit_category.html', data_category=data_category)
        #{else idp null/empty}
    else:
        return render_template("login.html")

#route delete data category
@app.route('/delete_category/<int:idc>', methods=['POST'])
def delete_category(idc):
    if 'session_token' in session:
        print('id category: ', idc)
        try:
            db = get_db_connection()
            cursor = db.cursor()
            # Check if there are any products associated with this category
            cursor.execute('SELECT COUNT(*) FROM products WHERE category_id = ?', (idc,))
            product_count = cursor.fetchone()[0]

            if product_count > 0:
                flash('Cannot delete category with associated products!', 'error')
                return redirect(url_for('list_category'))

            # Delete the category
            cursor.execute('DELETE FROM category WHERE id = ?', (idc,))
            db.commit()
            db.close()
            if cursor.rowcount == 0:
                flash('Category not found', 'error')

            flash('Deleted successfully!', 'success')
            return redirect(url_for('list_category'))

        except sqlite3.IntegrityError:
            flash('Failed to delete category due to database constraints', 'error')
    else:
        return redirect(url_for('login'))

# 2. ---------------------------------END CRUD CATEGORY---------------------------------#


# 3. ---------------------------------BEGIN CRUD TRANSACTION---------------------------------#
#Route to page list category
@app.route('/list_transaction')
def list_transaction():
    if 'session_token' in session:
        #conn = get_db_connection()
        #list_cats = conn.execute("SELECT * FROM category").fetchall()  # Ambil semua produk dari database
        #conn.close()
        return render_template('transaction/list_transaction.html')
    else:
        return render_template("login.html")

# seacrh product by SKU for transaction
@app.route('/search_product_with_category', methods=['GET'])
def search_product_with_category():
    sku = request.args.get('sku')
    if not sku:
        return jsonify({"error": "SKU is required"}), 400

    try:
        db = get_db_connection()
        cursor = db.cursor()

        # SQL join query to get product and category information
        cursor.execute('''
            SELECT p.id, p.sku, p.name AS product_name, p.price, p.stock, 
                   c.id AS category_id, c.name AS category_name
            FROM products p
            JOIN category c ON p.category_id = c.id
            WHERE p.sku = ?
        ''', (sku,))
        product = cursor.fetchone()

        if product:
            # Convert the result to a dictionary
            product_data = {
                "id": product["id"],
                "sku": product["sku"],
                "product_name": product["product_name"],
                "price": product["price"],
                "stock": product["stock"],
                "category_id": product["category_id"],
                "category_name": product["category_name"]
            }
            return jsonify(product_data), 200
        else:
            return jsonify({"error": "Product not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to create a transaction
@app.route('/transaction', methods=['POST'])
def create_transaction():
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity')

    if not all([product_id, quantity]):
        return jsonify({"error": "Product ID and quantity are required"}), 400

    try:
        db = get_db_connection()
        cursor = db.cursor()

        # Check stock and price for the product
        cursor.execute('SELECT stock, price FROM products WHERE id = ?', (product_id,))
        product = cursor.fetchone()
        print(product_id)

        if product is None:
            return jsonify({"error": "Product does not exist"}), 404

        if product["stock"] < quantity:
            return jsonify({"error": "Insufficient stock available"}), 400

        total_price = product["price"] * quantity
        new_stock = product["stock"] - quantity
        cursor.execute('UPDATE products SET stock = ? WHERE id = ?', (new_stock, product_id))

        cursor.execute(
            '''
            INSERT INTO transaction_product (product_id, quantity, total_price, transaction_date)
            VALUES (?, ?, ?, ?)
            ''', (product_id, quantity, total_price, dtm)
        )
        db.commit()

        return jsonify({
            "message": "Transaction created successfully",
            "transaction_id": cursor.lastrowid,
            "product_id": product_id,
            "quantity": quantity,
            "total_price": total_price
        }), 201

    except sqlite3.IntegrityError:
        return jsonify({"error": "Failed to create transaction due to database constraints"}), 400

#Get Transaction to show table
@app.route('/transactions', methods=['GET'])
def get_transactions():
    try:
        db = get_db_connection()
        cursor = db.cursor()
        query = '''
            SELECT t.id, t.product_id, t.quantity, t.total_price, t.transaction_date, p.name as product_name
            FROM transaction_product t
            JOIN products p ON t.product_id = p.id 
            WHERE DATE(transaction_date)= ?
        '''
        # Retrieve all transactions with product details
        transactions = cursor.execute(query, (today,)).fetchall()

        # Convert each row to a dictionary
        transactions_list = [
            {
                "id": row["id"],
                "product_id": row["product_id"],
                "product_name": row["product_name"],
                "quantity": row["quantity"],
                "total_price": row["total_price"],
                "transaction_date": row["transaction_date"]
            } for row in transactions
        ]

        return jsonify(transactions_list), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==========================GET API to Client====================================#
@app.route('/api/get_products', methods=['GET'])
def get_products():
    conn = get_db_connection()
    products = conn.execute('''
        SELECT 
            products.id AS product_id,
            products.name AS product_name,
            products.description AS product_description,
            products.price AS product_price,
            products.stock AS product_stock,
            products.sku AS product_sku,
            products.is_active AS product_status,
            products.image_url AS product_image_url,
            products.created_at AS product_created_at,
            products.updated_at AS product_updated_at,
            category.id AS category_id,
            category.name AS category_name,
            category.description AS category_description
        FROM 
            products
        LEFT JOIN 
            category ON products.category_id = category.id
        ''').fetchall()
    conn.close()
    return jsonify([dict(product) for product in products]), 200

# API endpoint to fetch categories based on name
@app.route('/api/categories/<string:category_id>',  methods=['GET', 'POST'])
def api_categories(category_id):
    conn  = get_db_connection()
    if category_id:
        categories = conn.execute('SELECT * FROM products WHERE category_id = ?', (category_id,)).fetchall()
    else:
        categories = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    # Convert categories to a list of dictionaries for JSON response
    return jsonify([dict(categories_list) for categories_list in categories]), 200

#route tampilkan (show) data detail produk
@app.route('/api/des_product/<string:idb>',  methods=['GET', 'POST'])
def show_desproduct(idb):
    conn = get_db_connection()
    if idb:
        desproduct = conn.execute('SELECT * FROM products WHERE id = ?', (idb,)).fetchall()
        return jsonify([dict(des) for des in desproduct]), 200

if __name__ == '__main__':
    app.run(debug=True, host="192.168.50.29", port=80)
