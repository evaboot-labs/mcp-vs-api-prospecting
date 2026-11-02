# Agent instructions

This repo runs the same small Evaboot export twice: once through the Evaboot MCP server, once through the Evaboot REST API. It times both, compares what came back and writes `results/comparison.md`, so the user can choose the path that fits their team.

1. Follow the skill in `skills/mcp-vs-api/SKILL.md` step by step.
2. The API side is `scripts/api_export.py`. The comparison is `scripts/compare.py`.
3. If the Evaboot MCP tools or the API key are missing, follow `docs/connect-your-agent.md`.
4. To explain the result, use `docs/when-to-use-which.md`.
5. If the user wants the comparison in n8n, follow `docs/n8n.md` with them one step at a time.

Confirm with the user before every export: each path costs 1 Evaboot credit per lead. Never ask for or handle the API key in chat: the user writes it into `.env`. Never commit `.env`, `data/` or `results/*-leads.json`: they hold secrets and real people's data.
