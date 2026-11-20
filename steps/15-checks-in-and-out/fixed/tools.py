"""The app's own tools: order lookup, order search, refunds and email."""
from common import config
from common.tooling import function_spec, number_param, text_param

SPECS = [
    function_spec("lookup_order", "Look up one order by its id, for example A-2001.",
                  {"order_id": text_param("Order id")}, ["order_id"]),
    function_spec("search_orders", "List the signed-in customer's orders that have a given status.",
                  {"status": text_param("processing, shipped or delivered")}, ["status"]),
    function_spec("issue_refund", "Refund money for an order.",
                  {"order_id": text_param("Order id"), "amount": number_param("Amount to refund"),
                   "reason": text_param("Why the customer wants a refund")}, ["order_id", "amount"]),
    function_spec("send_email", "Send an email.",
                  {"to": text_param("Recipient address"), "subject": text_param("Subject line"),
                   "body": text_param("Email text")}, ["to", "subject", "body"]),
]


class LocalTools:
    def __init__(self, store, mailer, customer_id):
        self.store = store
        self.mailer = mailer
        self.customer_id = customer_id
        self.handlers = {
            "lookup_order": self.lookup_order,
            "search_orders": self.search_orders,
            "issue_refund": self.issue_refund,
            "send_email": self.send_email,
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
            return {"error": f"bad arguments for {name}: {problem}"}

    def lookup_order(self, order_id):
        order = self.store.find_order(order_id)
        if order is None:
            return {"error": "no such order"}
        # FLAW (lesson 9): no check that the order belongs to the signed-in
        # customer, and the owner's contact details come back with it.
        customer = self.store.find_customer(order["customer_id"])
        return {**order, "customer_name": customer["name"], "customer_email": customer["email"],
                "customer_phone": customer["phone"]}

    def search_orders(self, status):
        # FIX (lesson 15): the status must be one of the known values, and it
        # travels to SQLite as a parameter, never as part of the SQL text.
        if status not in config.ORDER_STATUSES:
            return {"error": f"status must be one of {', '.join(config.ORDER_STATUSES)}"}
        sql = "SELECT id, item, total, status FROM orders WHERE customer_id = ? AND status = ?"
        return {"orders": self.store.rows(sql, (self.customer_id, status))}

    def issue_refund(self, order_id, amount, reason=""):
        # FLAW (lesson 12): any order, any amount, paid at once, nobody asked.
        return self.store.add_refund(order_id, float(amount), reason, "paid")

    def send_email(self, to, subject, body):
        # FLAW (lessons 12 and 13): the model picks the recipient.
        self.mailer.send(to, subject, body)
        return {"sent_to": to}
