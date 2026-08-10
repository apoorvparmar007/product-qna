import sqlite3

conn = sqlite3.connect("database/toyshop.db")
cur = conn.cursor()

cur.execute("SELECT * FROM products LIMIT 1")
first_row = cur.fetchone()

if first_row:
    column_names = first_row.keys()
    print(column_names)

conn.close()