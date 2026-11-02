"""UTCP-style access: discover the tool, call the native API directly.

A "manual" describes the API's tools in its native terms. The agent
reads the manual and talks straight to the endpoint — REST here —
reusing the API's own authentication. No wrapper, no extra service
to deploy. This is the low-infrastructure path, and for read-only or
already well-governed APIs it is often the right one.
"""

MANUAL = {
    "name": "orders-api",
    "version": "1.0",
    "tools": [
        {
            "name": "get_order",
            "call": "GET /orders/{order_id}",
            "auth": "x-api-key header",
        },
        {
            "name": "create_refund",
            "call": "POST /refunds",
            "auth": "x-api-key header",
        },
    ],
}


class DirectClient:
    """Calls the native API exactly as its manual describes."""

    def __init__(self, api, api_key):
        self.api = api
        self.headers = {"x-api-key": api_key}

    def call_tool(self, name, **arguments):
        if name == "get_order":
            return self.api.get_order(arguments["order_id"], self.headers)
        if name == "create_refund":
            return self.api.create_refund(
                arguments["order_id"], arguments["amount"], self.headers
            )
        raise ValueError(f"tool not in manual: {name}")
