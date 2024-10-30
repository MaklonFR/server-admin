from types import MethodType

import requests
from flask import Flask, jsonify
from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import hashlib

app = Flask(__name__)
app.config['SECRET_KEY'] = 'pemrograman-web-framework'
IP_SERVER = "https://c300-182-3-199-57.ngrok-free.app/"

def create_connection():
    conn = sqlite3.connect('db_products.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row  # Ensure that rows are returned as dictionaries
    return conn

# In-memory storage for products
products = []

@app.route ('/')
def main():
    # Replace this URL with the actual endpoint of your PHP API
    api_url = IP_SERVER+"/api/get_products"
    try:
        # Mengambil data dari API
        response = requests.get(api_url)
        # Memeriksa apakah permintaan berhasil
        response.raise_for_status()  # Akan memunculkan pengecualian jika status code bukan 200
        # Mengambil data JSON dari respon
        products = response.json()
        # kirim IPSERVER
        server = {
            'ipserver': IP_SERVER,
        }
        # Menampilkan data produk
        print("Daftar Produk:")
        for product in products:
            print(f"ID: {product['id']}, Nama: {product['name']}, Harga: {product['price']}")
        return render_template("main.html", products=products, **server)

    except requests.exceptions.RequestException as e:
        print(f"Terjadi kesalahan: {e}")


@app.route ('/product_details')
def product_details():
    return render_template("products.html")

# Route to render the HTML template
@app.route('/cat')
def display_categories():
    return render_template('categories.html')

# Route to fetch products
@app.route('/show/<string:cat>',  methods=['GET', 'POST'])
def api_categories(cat):
    cat= cat
    #return render_template("products.html")
    api_url = IP_SERVER+"/api/categories/"+ cat
    try:
        # Mengambil data dari API
        response = requests.get(api_url)
        # Memeriksa apakah permintaan berhasil
        response.raise_for_status()  # Akan memunculkan pengecualian jika status code bukan 200
        # Mengambil data JSON dari respon
        products = response.json()
        # kirim IPSERVER
        server = {
            'ipserver': IP_SERVER,
        }
        # Menampilkan data produk
        print("Daftar Produk:")
        for product in products:
            print(f"ID: {product['id']}, Nama: {product['name']}, Harga: {product['price']}")
        return render_template("products.html", products=products, **server)

    except requests.exceptions.RequestException as e:
        print(f"Terjadi kesalahan: {e}")

# Route to fetch description products
@app.route('/description_product/<string:idb>',  methods=['GET', 'POST'])
def show_desproduct(idb):
    idb= idb
    #return render_template("products.html")
    api_url = IP_SERVER+"/api/des_product/"+ idb
    try:
        # Mengambil data dari API
        response = requests.get(api_url)
        # Memeriksa apakah permintaan berhasil
        response.raise_for_status()  # Akan memunculkan pengecualian jika status code bukan 200
        # Mengambil data JSON dari respon
        products = response.json()
        # kirim IPSERVER
        server = {
            'ipserver': IP_SERVER,
        }
        # Menampilkan data produk
        for product in products:
            print(f"ID: {product['id']}, Nama: {product['name']}, Harga: {product['price']}")
        return render_template('products/list_products.html',des_product=products, **server)
    except requests.exceptions.RequestException as e:
        print(f"Terjadi kesalahan: {e}")

if __name__ == '__main__':
    app.run(debug=True, host="192.168.100.239", port=5000)