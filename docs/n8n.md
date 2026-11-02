# Both paths in n8n

`n8n/mcp-vs-api-export.json` exports the same lead list twice in one run: an MCP branch (MCP Client node) and an API branch (HTTP Request nodes with a polling loop). A Compare node counts leads, emails, safe emails and seconds per branch.

Tested on 2026-11-02 with n8n 1.x (Docker): both branches returned 9 leads with 9 safe emails.

## 1. Import

In n8n: *Workflows > Add workflow > ... > Import from File*, pick `n8n/mcp-vs-api-export.json`.

## 2. One credential for both branches

Create a **Bearer Auth** credential named `Evaboot (Bearer API key)`. Token: your Evaboot API key, from [dash.evaboot.com](https://dash.evaboot.com/dash/integrations/#api) > Integrations > API. Select it on the four Evaboot nodes: `MCP: export`, `MCP: results`, `API: start export`, `API: poll`.

The MCP Client node ships with n8n (`@n8n/n8n-nodes-langchain`). Its endpoint is `https://mcp.evaboot.com/mcp`.

## 3. Your settings

Open **Your settings** and set `list_url` to a Sales Navigator lead list URL, `https://www.linkedin.com/sales/lists/people/<id>`, with 10 leads or fewer. The API branch exports the whole list.

## 4. Run

Click **Execute workflow**. Each branch waits 30 seconds between status checks, so a small list takes one to two minutes. Open **Compare** for the result.

Cost: 1 Evaboot credit per lead, per branch.

## Rebuild the JSON

```bash
python3 n8n/build_workflow.py
```

Back to the [README](../README.md).
