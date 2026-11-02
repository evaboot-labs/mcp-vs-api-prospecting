# Connect your AI Agent

The comparison needs two things: the Evaboot MCP server in your agent, and an Evaboot API key in `.env`.

## 1. Accounts

- An [Evaboot account](https://dash.evaboot.com/accounts/signup/?last_click_origin=mcp-vs-api-prospecting-repo) with credits, and a Sales Navigator seat connected to it.

## 2. Get the repo

```bash
git clone https://github.com/evaboot-labs/mcp-vs-api-prospecting
cd mcp-vs-api-prospecting
cp .env.example .env
```

Write your API key into `.env` as `EVABOOT_API_KEY`. You find it in [dash.evaboot.com](https://dash.evaboot.com/dash/integrations/#api) > Integrations > API.

## 3. Connect the MCP server

**Claude (web and desktop app):** *Settings > Connectors > Add custom connector*: name `Evaboot`, URL `https://mcp.evaboot.com/mcp`. Sign in to Evaboot and approve.

**Claude Code:** sign in with the same Claude account and the connector is there. Or start Claude Code from this folder: the repo's `.mcp.json` uses the key in `.env`.

**Codex, Cursor:** add `https://mcp.evaboot.com/mcp` as an HTTP MCP server with the header `Authorization: Bearer <key>`.

## 4. Check

Ask your AI Agent: "Check my Evaboot quota and whether my Sales Navigator is connected." Then run `python3 scripts/api_export.py build "VPs of Sales at SaaS companies in France"`: a Sales Navigator URL means the API key works.

Back to the [README](../README.md).
