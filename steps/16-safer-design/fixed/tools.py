"""The app's own tools: order lookup, order search, refund requests and email."""
from common import config
from common.tooling import function_spec, number_param, text_param

REFUND_AWAITING_APPROVAL = "awaiting_approval"

SPECS = [
    function_spec("lookup_order", "Look up one of the signed-in customer's orders by its id, for example A-2001.",
                  {"order_id": text_param("Order id")}, ["order_id"]),
    function_spec("search_orders", "List the signed-in customer's orders that have a given status.",
                  {"status": text_param("processing, shipped or delivered")}, ["status"]),
    function_spec("request_refund", "Ask a staff member to approve a refund for one of the customer's orders.",
                  {"order_id": text_param("Order id"), "amount": number_param("Amount to refund"),
                   "reason": text_param("Why the customer wants a refund")}, ["order_id", "amount"]),
    # FIX (lesson 16): there is no recipient parameter. Email can only go to
    # the signed-in customer's address on file.
    function_spec("email_customer", "Email the signed-in customer at the address on file.",
                  {"subject": text_param("Subject line"), "body": text_param("Email text")}, ["subject", "body"]),
]


def _refused(reason):
    return {"error": reason}


class LocalTools:
    def __init__(self, store, mailer, customer_id):
        self.store = store
        self.mailer = mailer
        self.customer_id = customer_id
        self.handlers = {
            "lookup_order": self.lookup_order,
            "search_orders": self.search_orders,
            "request_refund": self.request_refund,
            "email_customer": self.email_customer,
        }

    def specs(self):
        return SPECS

    def run(self, name, arguments):
        handler = self.handlers.get(name)
        if handler is None:
            return None
        try:
            return handler(**arguments)
        except TypeError as problem:
            return _refused(f"bad arguments for {name}: {problem}")

    def _own_order(self, order_id):
        """The order, if it exists and belongs to the signed-in customer."""
        order = self.store.find_order(order_id)
        if order is None or order["customer_id"] != self.customer_id:
            return None
        return order

    def lookup_order(self, order_id):
        # FIX (lesson 16): only the customer's own orders, and no contact details.
        order = self._own_order(order_id)
        if order is None:
            return _refused("no order with that id on this account")
        return {key: order[key] for key in ("id", "item", "total", "status")}

    def search_orders(self, status):
        # FIX (lesson 15): the status must be one of the known values, and it
        # travels to SQLite as a parameter, never as part of the SQL text.
        if status not in config.ORDER_STATUSES:
            return _refused(f"status must be one of {', '.join(config.ORDER_STATUSES)}")
        sql = "SELECT id, item, total, status FROM orders WHERE customer_id = ? AND status = ?"
        return {"orders": self.store.rows(sql, (self.customer_id, status))}

    def request_refund(self, order_id, amount, reason=""):
        # FIX (lesson 16): own orders only, never more than was paid, and a
        # person approves every refund before any money moves.
        order = self._own_order(order_id)
        if order is None:
            return _refused("no order with that id on this account")
        try:
            amount = float(amount)
        except ValueError:
            return _refused("amount must be a number")
        still_refundable = order["total"] - self.store.refunded_total(order_id)
        if amount <= 0 or amount > still_refundable:
            return _refused(f"amount must be more than 0 and at most {still_refundable:.2f}")
        refund = self.store.add_refund(order_id, amount, reason, REFUND_AWAITING_APPROVAL)
        return {**refund, "note": "A staff member will review this refund."}

    def email_customer(self, subject, body):
        customer = self.store.find_customer(self.customer_id)
        self.mailer.send(customer["email"], subject, body)
        return {"sent_to": "the address on file"}
