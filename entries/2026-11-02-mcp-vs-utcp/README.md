# MCP vs UTCP: do you actually need a server in front of every API?

**Source:** LinkedIn post, shared 2026-11-02

## The idea

The post asks whether every API needs an MCP server in front of it.
UTCP's answer is no: let agents discover tools and call native
endpoints (REST, gRPC, WebSockets) directly, reusing the auth those
APIs already have. MCP's answer is a standardized protocol layer.
The post's position: it's not either/or — removing a wrapper doesn't
automatically solve authorization, observability, governance, or
transaction safety. The real question is *where* a protocol layer
earns its keep.

## What I built

One small orders API, exercised two ways, so the trade-off is visible
in running code instead of arguments:

- `native_api.py` — the "existing API": API-key auth, clean
  responses, mock data. No audit trail, no business-rule validation.
- `direct_client.py` — **UTCP-style.** A manual describes the tools;
  the agent calls the native endpoints directly.
- `policy_gateway.py` — **MCP-style.** A thin layer in front of the
  same API adding approval for side effects, input validation, and
  an audit log.
- `decision.py` — the post's closing question as a function: given a
  tool's profile, should it sit behind a protocol layer, and why?
- `demo.py` — runs one refund scenario through both paths.

The punchline the demo prints: on the direct path, a $10,000 refund
nobody approved sails through (201), because API-key auth cannot
tell a fine refund from a reckless one. Behind the gateway, the same
call is rejected, an absurd amount is rejected *even with* approval,
and every attempt is in the audit log.

## Run it

```bash
cd entries/2026-11-02-mcp-vs-utcp
python3 demo.py                        # the side-by-side comparison
python3 -m unittest discover -v        # 10 tests
```

No dependencies, no API key, no network.

## What to notice

- **The split is per tool, not per system.** In the gateway,
  read-only `get_order` needs no approval — the API's own auth is
  enough. Only the side-effecting `create_refund` picks up policy.
- **Auth ≠ authorization.** The native API authenticates callers
  perfectly and still can't express "refunds need a second pair of
  eyes." That gap — not protocol fashion — is what justifies a layer.
- **The wrapper is thin on purpose.** It re-implements nothing; it
  only adds the four things the post lists: authorization,
  observability, governance, transaction safety.

## Limits

The "API" is an in-process stand-in, not a real HTTP service, and the
gateway's approval is a boolean, not a real consent flow. A
production version would need real transport (an actual MCP server
or UTCP client), identity-aware approvals, and a durable audit
store. See the sibling project
[mcp-practical-toolkit](https://github.com/kbsai777/mcp-practical-toolkit)
for a real MCP server shape.
