---
name: mcp-vs-api
description: Run the same small Evaboot export twice, once through the Evaboot MCP server and once through the Evaboot REST API, time both, compare what came back, and write results/comparison.md so a sales team can pick the right path. Use when the user asks "MCP or API?", wants to benchmark the two, or wants to see both paths on their own data.
---

# MCP vs API: the same export, both ways

Goal: one Sales Navigator lead list, exported twice. Once with the Evaboot MCP tools, once with `scripts/api_export.py`. Then `scripts/compare.py` writes `results/comparison.md`.

Cost: 1 Evaboot credit per lead **per path**. A 10-lead list costs about 20 credits. Confirm with the user before each export.

## 1. Check the connection

- MCP: call `get_daily_export_quota`. `has_valid_salesnav` must be `true`. If the Evaboot tools are missing, follow `docs/connect-your-agent.md`.
- API: `.env` must hold `EVABOOT_API_KEY` (the user copies it from dash.evaboot.com > Integrations > API). Never ask for the key in chat.

## 2. Pick a small lead list

The API exports the **whole** search or list it is given: it has no result cap. So both paths use the same Sales Navigator **lead list** of 10 leads or fewer.

- The user has one: `list_lead_lists`, pick it, confirm its `entityCount`.
- Otherwise: build a search with `build_sn_search_from_prompt` (ask the user how many results they want), then `create_lead_list_from_search` with `max_results: 10`. Poll `get_list_from_search_status` until `complete` and take `list_url`.

## 3. Export through the MCP

Write down the start time. Call `export_sn_search_or_list` with the list URL, `name: "MCP vs API test (MCP)"`, `max_results: 10`. Poll `get_export` with `limit: 0` every 30 s until the status is `EXECUTED`, then `get_export` without a limit. Save the `prospects` array to `results/mcp-leads.json` and write `results/mcp-run.json`:

```json
{"extraction_id": "...", "leads": 10, "seconds": 0, "tool_calls": 0}
```

## 4. Export through the API

```bash
python3 scripts/api_export.py export "<list url>" --name "MCP vs API test (API)"
```

It times every HTTP call and writes `results/api-leads.json` and `results/api-run.json`.

## 5. Compare

```bash
python3 scripts/compare.py
```

Show the user `results/comparison.md`: leads, emails found, safe emails, rows that disagree, seconds and calls per path. Then say which path fits them, with the rule in `docs/when-to-use-which.md`.

## Rules

- `data/` and `results/*-leads.json` hold real people's data: never commit them, never paste them in a shared place.
- Do not start a recurring export or push leads anywhere: this skill only reads.
