"""Fake customers, orders and refunds in an in-memory SQLite database.

The database is rebuilt from the seed data on every start, so a restart resets
the lab. Every name, address and order in here is made up.
"""
import sqlite3

SCHEMA = """
CREATE TABLE customers (id TEXT PRIMARY KEY, name TEXT, email TEXT, phone TEXT);
CREATE TABLE orders (id TEXT PRIMARY KEY, customer_id TEXT, item TEXT, total REAL, status TEXT);
CREATE TABLE refunds (id INTEGER PRIMARY KEY AUTOINCREMENT, order_id TEXT, amount REAL, reason TEXT, state TEXT);
"""

SEED_CUSTOMERS = [
    ("C-1001", "Asha Rao", "asha.rao@example.test", "+00 555 0101"),
    ("C-1002", "Tom Becker", "tom.becker@example.test", "+00 555 0102"),
    ("C-1003", "Lina Okafor", "lina.okafor@example.test", "+00 555 0103"),
]

SEED_ORDERS = [
    ("A-2001", "C-1001", "Kettle Pro 2", 89.00, "delivered"),
    ("A-2002", "C-1001", "Tea Sampler Box", 24.50, "shipped"),
    ("A-2003", "C-1002", "Kettle Mini", 39.00, "delivered"),
    ("A-2004", "C-1003", "Kettle Pro 2", 89.00, "processing"),
]


class OrderStore:
    def __init__(self):
        # FastAPI runs request handlers on worker threads, so the one
        # in-memory connection is shared across threads.
        self.connection = sqlite3.connect(":memory:", check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self.connection.executescript(SCHEMA)
        self.connection.executemany("INSERT INTO customers VALUES (?, ?, ?, ?)", SEED_CUSTOMERS)
        self.connection.executemany("INSERT INTO orders VALUES (?, ?, ?, ?, ?)", SEED_ORDERS)
        self.connection.commit()

    def rows(self, sql, params=()):
        """Run a SELECT and return the rows as plain dicts."""
        return [dict(row) for row in self.connection.execute(sql, params)]

    def find_order(self, order_id):
        found = self.rows("SELECT * FROM orders WHERE id = ?", (order_id,))
        return found[0] if found else None

    def find_customer(self, customer_id):
        found = self.rows("SELECT * FROM customers WHERE id = ?", (customer_id,))
        return found[0] if found else None

    def add_refund(self, order_id, amount, reason, state):
        cursor = self.connection.execute(
            "INSERT INTO refunds (order_id, amount, reason, state) VALUES (?, ?, ?, ?)",
            (order_id, amount, reason, state),
        )
        self.connection.commit()
        return {"refund_id": cursor.lastrowid, "order_id": order_id, "amount": amount, "state": state}

    def refunds(self, state=None):
        if state is None:
            return self.rows("SELECT * FROM refunds ORDER BY id")
        return self.rows("SELECT * FROM refunds WHERE state = ? ORDER BY id", (state,))

    def refunded_total(self, order_id):
        """Money already refunded or waiting for approval on one order. Rejected refunds do not count."""
        found = self.rows(
            "SELECT COALESCE(SUM(amount), 0) AS total FROM refunds WHERE order_id = ? AND state != 'rejected'",
            (order_id,),
        )
        return found[0]["total"]

    def set_refund_state(self, refund_id, state):
        self.connection.execute("UPDATE refunds SET state = ? WHERE id = ?", (state, refund_id))
        self.connection.commit()
