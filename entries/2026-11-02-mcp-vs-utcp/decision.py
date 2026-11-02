"""The post's closing question, as code.

"Where do we actually need an agent-specific protocol layer, and
where are existing APIs already sufficient?"

Answer it per tool, not per ideology: a layer earns its keep only
when it supplies something the native API does not.
"""


def needs_protocol_layer(
    *,
    has_side_effects,
    api_has_auth,
    api_has_audit_log,
    api_validates_inputs,
    multiple_agent_consumers,
):
    """Return {'protocol_layer': bool, 'reasons': [str, ...]}."""
    reasons = []
    if has_side_effects:
        reasons.append(
            "the tool changes state, so calls need an approval/policy point"
        )
    if not api_has_auth:
        reasons.append("the API has no authentication for agents to reuse")
    if not api_has_audit_log:
        reasons.append("the API keeps no audit trail of agent actions")
    if not api_validates_inputs:
        reasons.append("the API does not validate inputs against business rules")
    if multiple_agent_consumers:
        reasons.append("several agents need one governed entry point")
    return {"protocol_layer": bool(reasons), "reasons": reasons}
