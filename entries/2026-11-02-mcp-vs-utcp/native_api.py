"""A stand-in for an existing enterprise REST API.

This is the kind of API the UTCP argument is about: it already exists,
already has API-key authentication, and already returns well-defined
responses. What it deliberately does NOT have is agent-era governance:
any authenticated caller can issue a refund of any size, and nothing
keeps an audit trail of who did what.
"""

ORDERS = {
    "A-102": {"status": "shipped", "total": 59.99},
    "A-103": {"status": "delivered", "total": 24.50},
}


class NativeAPI:
    def __init__(self, api_key):
        self._api_key = api_key
        self.refunds = []  # the API's own record of refunds it processed

    def _authorized(self, headers):
        return headers.get("x-api-key") == self._api_key

    def get_order(self, order_id, headers):
        if not self._authorized(headers):
            return 401, {"error": "invalid api key"}
        order = ORDERS.get(order_id)
        if order is None:
            return 404, {"error": f"no such order: {order_id}"}
        return 200, {"order_id": order_id, **order}

    def create_refund(self, order_id, amount, headers):
        # The API checks authentication and that the order exists.
        # It does NOT check whether this caller should be allowed to
        # refund, whether the amount is sane, or record an audit trail
        # beyond its own transaction list. That gap is the point.
        if not self._authorized(headers):
            return 401, {"error": "invalid api key"}
        if order_id not in ORDERS:
            return 404, {"error": f"no such order: {order_id}"}
        refund = {"order_id": order_id, "amount": amount, "status": "refunded"}
        self.refunds.append(refund)
        return 201, refund
