import unittest

from decision import needs_protocol_layer
from direct_client import DirectClient
from native_api import NativeAPI
from policy_gateway import PolicyError, PolicyGateway

KEY = "demo-key"


class DirectPathTests(unittest.TestCase):
    def setUp(self):
        self.api = NativeAPI(KEY)
        self.client = DirectClient(self.api, KEY)

    def test_direct_refund_succeeds_without_any_approval(self):
        status, _ = self.client.call_tool(
            "create_refund", order_id="A-103", amount=24.50)
        self.assertEqual(status, 201)

    def test_direct_path_also_lets_an_absurd_refund_through(self):
        # The governance gap from the post, demonstrated: the API's
        # auth cannot distinguish a fine refund from a reckless one.
        status, _ = self.client.call_tool(
            "create_refund", order_id="A-103", amount=10000)
        self.assertEqual(status, 201)

    def test_direct_call_still_needs_the_apis_own_auth(self):
        stranger = DirectClient(self.api, "wrong-key")
        status, _ = stranger.call_tool("get_order", order_id="A-102")
        self.assertEqual(status, 401)


class GatewayPathTests(unittest.TestCase):
    def setUp(self):
        self.api = NativeAPI(KEY)
        self.gateway = PolicyGateway(self.api, KEY)

    def test_unapproved_refund_is_blocked_before_reaching_the_api(self):
        with self.assertRaises(PolicyError):
            self.gateway.call_tool(
                "create_refund", order_id="A-103", amount=24.50)
        self.assertEqual(self.api.refunds, [])

    def test_absurd_refund_is_blocked_even_with_approval(self):
        with self.assertRaises(PolicyError):
            self.gateway.call_tool(
                "create_refund", order_id="A-103", amount=10000,
                approved=True)
        self.assertEqual(self.api.refunds, [])

    def test_approved_sane_refund_goes_through(self):
        status, _ = self.gateway.call_tool(
            "create_refund", order_id="A-103", amount=24.50, approved=True)
        self.assertEqual(status, 201)
        self.assertEqual(len(self.api.refunds), 1)

    def test_every_attempt_lands_in_the_audit_log(self):
        for kwargs in ({"amount": 24.50}, {"amount": 10000, "approved": True}):
            with self.assertRaises(PolicyError):
                self.gateway.call_tool(
                    "create_refund", order_id="A-103", **kwargs)
        self.gateway.call_tool(
            "create_refund", order_id="A-103", amount=24.50, approved=True)
        outcomes = [e["outcome"] for e in self.gateway.audit_log]
        self.assertEqual(len(outcomes), 3)
        self.assertTrue(outcomes[0].startswith("rejected"))
        self.assertTrue(outcomes[1].startswith("rejected"))
        self.assertEqual(outcomes[2], "allowed")

    def test_read_only_calls_need_no_approval(self):
        status, body = self.gateway.call_tool("get_order", order_id="A-102")
        self.assertEqual(status, 200)
        self.assertEqual(body["status"], "shipped")


class DecisionTests(unittest.TestCase):
    def test_mature_read_only_api_needs_no_layer(self):
        verdict = needs_protocol_layer(
            has_side_effects=False, api_has_auth=True,
            api_has_audit_log=True, api_validates_inputs=True,
            multiple_agent_consumers=False)
        self.assertFalse(verdict["protocol_layer"])
        self.assertEqual(verdict["reasons"], [])

    def test_side_effects_alone_justify_a_layer(self):
        verdict = needs_protocol_layer(
            has_side_effects=True, api_has_auth=True,
            api_has_audit_log=True, api_validates_inputs=True,
            multiple_agent_consumers=False)
        self.assertTrue(verdict["protocol_layer"])


if __name__ == "__main__":
    unittest.main()
