from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Fungsi untuk koneksi ke database
def get_db_connection():
    conn = sqlite3.connect('db_products.db')
    conn.row_factory = sqlite3.Row
    return conn

# Buat tabel produk jika belum ada
def create_table():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            description TEXT,
            stock INTEGER DEFAULT 0,
            category TEXT NOT NULL,
            image_url TEXT,
            sku TEXT UNIQUE,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Buat tabel produk jika belum ada
def create_table_admin():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Route untuk menambahkan produk
@app.route('/add', methods=('GET', 'POST'))
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        description = request.form['description']
        stock = request.form['stock']
        category = request.form['category']
        image_url = request.form['image_url']
        sku = request.form['sku']

        conn = get_db_connection()
        conn.execute('''
            INSERT INTO products (name, price, description, stock, category, image_url, sku)
            VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (name, price, description, stock, category, image_url, sku))
        conn.commit()
        conn.close()
        return redirect(url_for('add_product'))  # Redirect to add product page after submitting
    return render_template('add_product.html')

# Jalankan aplikasi Flask
if __name__ == '__main__':
    create_table()  # Membuat tabel saat aplikasi dijalankan pertama kali
    create_table_admin()
    app.run(debug=True)
