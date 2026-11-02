# LinkedIn AI Lab

**Every LinkedIn AI post, implemented.**

I post short updates about AI on LinkedIn. This repository is where each
post gets turned into small, runnable, tested code — so the ideas don't
stay as posts; they become things you can clone and run.

## How it works

1. A LinkedIn post explores an AI idea or pattern.
2. The idea is implemented here as a minimal, self-contained example.
3. The example ships with tests and runs locally — no paid API key
   required for the basic version.
4. The entry is indexed below with a link back to the post's concept.

## Entries

| Date | Entry | What it shows |
| --- | --- | --- |
| 2026-11-02 | [MCP vs UTCP: do you need a server in front of every API?](entries/2026-11-02-mcp-vs-utcp/) | The same API called directly (UTCP-style) vs through a policy gateway (MCP-style) — and a decision function for where the layer belongs |

## Entry format

Each entry lives in `entries/YYYY-MM-DD-slug/` with:

- `README.md` — the idea, what was built, how to run it
- the implementation (small, readable, dependency-light)
- tests proving it works

See [TEMPLATE.md](TEMPLATE.md) for the structure every entry follows.

## License

MIT — see [LICENSE](LICENSE).
