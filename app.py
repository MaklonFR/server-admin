import os
import sqlite3

import requests
from flask import Flask, request, jsonify, render_template, redirect, url_for, abort, session
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
from flask_cors import CORS  # Import CORS

# Enable CORS for a specific origin

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
myserver = "https://smkn1kuwus.sch.id/client-koperasi-boe/"

UPLOAD_FOLDER = myserver + 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Maksimal ukuran file 16 MB

bcrypt = Bcrypt(app)

# Fungsi untuk berinteraksi dengan database SQLite
def get_db_connection():
    conn = sqlite3.connect('db_products.db')
    conn.row_factory = sqlite3.Row
    print("connecsi susess")
    return conn


# Route untuk halaman login
@app.route('/login', methods=['GET', 'POST'])
def login():
        if request.method == 'POST':
            username = request.json.get('username', None)
            password = request.json.get('password', None)
            conn = get_db_connection()
            admin = conn.execute('SELECT * FROM admin WHERE username = ?', (username,)).fetchone()
            conn.close()

            # Cek username dan password
            if admin and bcrypt.check_password_hash(admin['password'], password):
                return jsonify(admin), 200
            return jsonify({"msg": "Login failed"}), 401
        return render_template('login.html')

# Route untuk register admin
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

# Route untuk logout (menghapus token dari session)
@app.route('/logout')
def logout():
    session.pop('access_token', None)
    return redirect(url_for('login'))

@app.route ('/')
def main():
    return render_template("login.html")

@app.route ('/home')
def home():
    return render_template("index.html")

@app.route ('/register_page')
def register_page():
    return render_template("register.html")

@app.route ('/login_page')
def login_page():
    return render_template("login.html")

# Route untuk menambahkan item (butuh autentikasi)
@app.route('/addProduct', methods=('GET', 'POST'))
def addProduct():
    # Pastikan user masih login dengan token yang valid
    if request.method == 'POST':
        name = request.form['namep']
        price = request.form['price']
        stock = request.form['stock']
        category = request.form['category']
        status = request.form['status']
        sku = request.form['sku']
        description = request.form['description']

        # Cek apakah file di-upload
        if 'image' not in request.files:
            return "No file part"
        file = request.files['image']

        if file.filename == '':
            return "No selected file"

        if file:
            # Amankan nama file dan simpan di direktori upload
            filename = secure_filename(file.filename)
            try:
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_url = os.path.join(app.config['UPLOAD_FOLDER'], filename)  # Path file yang diupload
                conn = get_db_connection()
                conn.execute(
                    'INSERT INTO products (name, price, stock, category, image_url, sku, is_active, description) '
                    'VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                    (name, price, stock, category, image_url, sku, status, description))
                conn.commit()
                conn.close()
                return redirect(url_for('list_products'))  # Redirect ke halaman add product setelah submit

            except OSError as e:
                return f'Error saving file: {e}', 500

            return 'File uploaded successfully', 200

@app.route ('/add')
def add():
    return render_template("products/add_product.html")

@app.route ('/products')
def products():
    return render_template("products/products.html")

@app.route('/list_products')
def list_products():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products').fetchall()  # Ambil semua produk dari database
    conn.close()
    return render_template('products/list_products.html', products=products, myserver=myserver)


# ==========================GET API====================================#
@app.route('/api/get_products', methods=['GET'])
def get_products():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    return jsonify([dict(product) for product in products]), 200

# API endpoint to fetch categories based on name
@app.route('/api/categories/<string:category>',  methods=['GET', 'POST'])
def api_categories(category):
    conn  = get_db_connection()
    if category:
        categories = conn.execute('SELECT * FROM products WHERE category = ?', (category,)).fetchall()
    else:
        categories = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    # Convert categories to a list of dictionaries for JSON response
    return jsonify([dict(categories_list) for categories_list in categories]), 200
    print(categories_list)

#route tampilkan (show) data detail student
@app.route('/api/des_product/<string:idb>',  methods=['GET', 'POST'])
def show_desproduct(idb):
    conn = get_db_connection()
    if idb:
        desproduct = conn.execute('SELECT * FROM products WHERE id = ?', (idb,)).fetchall()
    return jsonify([dict(des) for des in desproduct]), 200

if __name__ == '__main__':
    app.run(debug=True, host="192.168.100.239", port=8000)