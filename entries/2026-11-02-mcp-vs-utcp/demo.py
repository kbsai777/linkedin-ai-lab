"""Run both patterns against the same API and compare.

Scenario: an agent needs to refund order A-103 ($24.50).

1. UTCP-style direct call — succeeds instantly, nothing in the way.
   Also succeeds for a $10,000 refund nobody approved. That is the
   governance gap, not a bug in the API.
2. MCP-style wrapped call — the same refund is refused until it is
   approved, an absurd amount is refused even with approval, and
   every attempt is in the audit log.
3. The decision helper — when a layer is and is not worth adding.
"""

from decision import needs_protocol_layer
from direct_client import DirectClient
from native_api import NativeAPI
from policy_gateway import PolicyError, PolicyGateway

API_KEY = "demo-key"


def main():
    print("=== 1. Direct (UTCP-style): agent -> native API ===")
    api = NativeAPI(API_KEY)
    direct = DirectClient(api, API_KEY)
    print("refund $24.50:", direct.call_tool(
        "create_refund", order_id="A-103", amount=24.50))
    print("refund $10,000, unapproved:", direct.call_tool(
        "create_refund", order_id="A-103", amount=10000))
    print("audit trail kept by the API about *who/why*: none\n")

    print("=== 2. Wrapped (MCP-style): agent -> gateway -> native API ===")
    api2 = NativeAPI(API_KEY)
    gateway = PolicyGateway(api2, API_KEY)
    try:
        gateway.call_tool("create_refund", order_id="A-103", amount=24.50)
    except PolicyError as exc:
        print("unapproved refund:", exc)
    try:
        gateway.call_tool(
            "create_refund", order_id="A-103", amount=10000, approved=True)
    except PolicyError as exc:
        print("approved but absurd refund:", exc)
    print("approved refund $24.50:", gateway.call_tool(
        "create_refund", order_id="A-103", amount=24.50, approved=True))
    print("audit log:")
    for entry in gateway.audit_log:
        print("  ", entry)
    print()

    print("=== 3. So where does the layer belong? ===")
    read_only = needs_protocol_layer(
        has_side_effects=False, api_has_auth=True, api_has_audit_log=True,
        api_validates_inputs=True, multiple_agent_consumers=False)
    print("read-only lookup on a mature API:", read_only)
    refunding = needs_protocol_layer(
        has_side_effects=True, api_has_auth=True, api_has_audit_log=False,
        api_validates_inputs=False, multiple_agent_consumers=True)
    print("refund tool on this API:", refunding)


if __name__ == "__main__":
    main()
