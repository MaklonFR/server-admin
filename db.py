from flask import Flask
import sqlite3 as sql

con = sql.connect('db_product.db')
print("Database berhasil dibuat!")

con.close()
