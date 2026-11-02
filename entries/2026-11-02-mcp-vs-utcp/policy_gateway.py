"""MCP-style access: a thin protocol layer in front of the same API.

The wrapper does not re-implement the API. It adds the four things
the LinkedIn post says removing a wrapper does NOT magically solve:

- authorization: side-effecting tools require explicit approval
- governance:    arguments are validated against business rules
- observability: every attempted call lands in an audit log
- safety:        rejected calls never reach the native API
"""

from native_api import ORDERS


class PolicyError(Exception):
    """Raised when the gateway refuses a call."""


class PolicyGateway:
    def __init__(self, api, api_key):
        self.api = api
        self.headers = {"x-api-key": api_key}
        self.audit_log = []

    def _audit(self, tool, arguments, outcome):
        self.audit_log.append(
            {"tool": tool, "arguments": arguments, "outcome": outcome}
        )

    def call_tool(self, name, approved=False, **arguments):
        try:
            result = self._dispatch(name, approved, arguments)
        except PolicyError as exc:
            self._audit(name, arguments, f"rejected: {exc}")
            raise
        self._audit(name, arguments, "allowed")
        return result

    def _dispatch(self, name, approved, arguments):
        if name == "get_order":
            # Read-only: the API's own auth is enough.
            return self.api.get_order(arguments["order_id"], self.headers)
        if name == "create_refund":
            return self._refund(approved, arguments)
        raise PolicyError(f"unknown tool: {name}")

    def _refund(self, approved, arguments):
        if not approved:
            raise PolicyError("create_refund has side effects and needs approval")
        order = ORDERS.get(arguments["order_id"])
        if order is None:
            raise PolicyError(f"no such order: {arguments['order_id']}")
        amount = arguments["amount"]
        if amount <= 0 or amount > order["total"]:
            raise PolicyError(
                f"refund amount {amount} outside 0..{order['total']} for "
                f"order {arguments['order_id']}"
            )
        return self.api.create_refund(
            arguments["order_id"], amount, self.headers
        )
