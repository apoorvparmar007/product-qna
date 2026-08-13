import sqlite3
import sys

DB_PATH = "database/toyshop.db"


def view_products(limit: int):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("SELECT * FROM products LIMIT ?", (limit,))
    rows = cur.fetchall()

    if not rows:
        print("No records found.")
        conn.close()
        return

    columns = rows[0].keys()
    widths = [max(len(col), *(len(str(row[col])) for row in rows)) for col in columns]

    header = " | ".join(col.ljust(w) for col, w in zip(columns, widths))
    print(header)
    print("-+-".join("-" * w for w in widths))
    for row in rows:
        print(" | ".join(str(row[col]).ljust(w) for col, w in zip(columns, widths)))

    cur.execute("SELECT COUNT(*) FROM products")
    total = cur.fetchone()[0]
    print(f"\nShowing {len(rows)} of {total} records.")

    conn.close()


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    view_products(n)
