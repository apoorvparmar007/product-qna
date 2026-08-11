import sqlite3
from langchain_core.tools import tool

@tool
def check_product_price(product_name: str) -> str:
    """Check price for a toy product by name.

    Args:
        product_name: The name of the toy product to look up for price.
    """
    conn = sqlite3.connect("database/toyshop.db")
    cur = conn.cursor()

    cur.execute("SELECT price FROM products WHERE name LIKE ?", (f"%{product_name}%",))
    count = cur.fetchall()

    conn.close()

    return (f"""Price of {product_name} is {count}""")


@tool
def check_product_availability(product_name: str) -> str:
    """Check availability for a toy product by name.

    Args:
        product_name: The name of the toy product to look up.
    """
    conn = sqlite3.connect("database/toyshop.db")
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM products WHERE name LIKE ?", (f"%{product_name}%",))
    count = cur.fetchall()

    conn.close()

    return (f"""Found {count} records""")
    

    # for row in rows:
    #     print(row)

    # 
