"""Builds n8n/mcp-vs-api-export.json. Run: python3 n8n/build_workflow.py

One manual run exports the same Sales Navigator list twice, side by side:
- top branch, through the Evaboot MCP server (MCP Client node, two tool calls);
- bottom branch, through the Evaboot REST API (HTTP Request nodes and a polling loop).
The last node compares the two: leads, emails found, safe emails, seconds per branch.
Each branch spends 1 Evaboot credit per lead: use a small list (10 leads or fewer).
"""
import json
import uuid
from pathlib import Path

EVABOOT_MCP = "https://mcp.evaboot.com/mcp"
API = "https://api.evaboot.com/v1"
CRED = {"httpBearerAuth": {"id": "", "name": "Evaboot (Bearer API key)"}}

nodes, connections = [], {}


def node(name, type_, version, params, pos, creds=None, **extra):
    n = {"parameters": params, "id": str(uuid.uuid4()), "name": name, "type": type_,
         "typeVersion": version, "position": pos, **extra}
    if creds:
        n["credentials"] = creds
    nodes.append(n)


def link(a, b, out=0):
    connections.setdefault(a, {}).setdefault("main", [])
    while len(connections[a]["main"]) <= out:
        connections[a]["main"].append([])
    connections[a]["main"][out].append({"node": b, "type": "main", "index": 0})


def mcp_call(name, tool, json_expr, pos):
    node(name, "@n8n/n8n-nodes-langchain.mcpClient", 1.1, {
        "endpointUrl": EVABOOT_MCP, "authentication": "bearerAuth",
        "tool": {"__rl": True, "mode": "list", "value": tool, "cachedResultName": tool},
        "inputMode": "json", "jsonInput": json_expr, "options": {"timeout": 120000},
    }, pos, CRED)


def http(name, method, url, pos, body=None, full=False):
    p = {"method": method, "url": url, "authentication": "genericCredentialType",
         "genericAuthType": "httpBearerAuth", "options": {}}
    if body:
        p.update({"sendBody": True, "specifyBody": "json", "jsonBody": body})
    if full:  # keep the status code: 202 = still running, 200 = done
        p["options"] = {"response": {"response": {"fullResponse": True, "neverError": True}}}
    node(name, "n8n-nodes-base.httpRequest", 4.2, p, pos, CRED)


def code(name, js, pos):
    node(name, "n8n-nodes-base.code", 2, {"jsCode": js}, pos)


def note(text, pos, w, h, color=7):
    node(f"Note {len(nodes)}", "n8n-nodes-base.stickyNote", 1,
         {"content": text, "width": w, "height": h, "color": color}, pos)


S = "$('Your settings').first().json"

SUMMARY_JS = r"""
// One row per branch: what came back and how long it took.
const s = $('Your settings').first().json;
const started = new Date(s.started_at);
const row = (path, leads, endedAt) => ({
  path,
  leads: leads.length,
  emails_found: leads.filter(l => l['Email']).length,
  safe_emails: leads.filter(l => l['Email Status'] === 'safe').length,
  seconds: Math.round((new Date(endedAt) - started) / 1000),
});
const r = $('MCP: results').last().json;
const mcpLeads = r.structuredContent?.result?.prospects || r.result?.prospects || [];
const apiLeads = $('API: poll').last().json.body.prospects || [];
return [row('MCP', mcpLeads, $('MCP: done at').first().json.done_at),
        row('API', apiLeads, $('API: done at').first().json.done_at)].map(json => ({ json }));
"""

note("## MCP vs API: the same export, both ways\n\nSet **Your settings**: a Sales Navigator **lead list** URL "
     "with 10 leads or fewer.\n\nOne credential for both "
     "branches: **Bearer Auth** with your Evaboot API key (dash.evaboot.com > Integrations > API).\n\nEach branch costs "
     "1 credit per lead. Setup guide: docs/n8n.md", [-420, -260], 380, 340, 5)
note("### Through the MCP server\nTwo MCP Client calls. `max_results` caps the export, so a big search "
     "cannot overspend.", [420, -240], 900, 320, 4)
note("### Through the REST API\nYou write the HTTP calls and the polling loop yourself. The API exports the "
     "**whole** search or list: there is no cap.", [420, 110], 1300, 300, 6)

node("Run", "n8n-nodes-base.manualTrigger", 1, {}, [-400, 120])
node("Your settings", "n8n-nodes-base.set", 3.4, {"assignments": {"assignments": [
    {"id": "u", "name": "list_url", "type": "string",
     "value": "https://www.linkedin.com/sales/lists/people/REPLACE_WITH_YOUR_LIST_ID"},
    {"id": "n", "name": "max_results", "type": "number", "value": 10},
    {"id": "t", "name": "started_at", "type": "string", "value": "={{ $now.toISO() }}"},
]}}, [-160, 120])
# MCP branch
mcp_call("MCP: export", "export_sn_search_or_list",
         f"={{{{ JSON.stringify({{ search_url: {S}.list_url, name: 'MCP vs API test (n8n, MCP)', "
         f"max_results: {S}.max_results }}) }}}}", [480, -40])
node("MCP: wait 30 s", "n8n-nodes-base.wait", 1.1, {"amount": 30}, [700, -40], webhookId=str(uuid.uuid4()))
mcp_call("MCP: results", "get_export",
         "={{ JSON.stringify({ extraction_id: $('MCP: export').first().json.structuredContent?.result?.extraction_id "
         "|| $('MCP: export').first().json.result?.extraction_id }) }}", [920, -40])
node("MCP: finished?", "n8n-nodes-base.if", 2.2, {"conditions": {"options": {"caseSensitive": True, "typeValidation": "loose"},
     "conditions": [{"id": "f", "leftValue": "={{ ($json.structuredContent?.result || $json.result || {}).status }}",
                     "rightValue": "EXECUTED", "operator": {"type": "string", "operation": "equals"}}],
     "combinator": "and"}}, [1140, -40])
node("MCP: done at", "n8n-nodes-base.set", 3.4, {"assignments": {"assignments": [
    {"id": "d", "name": "done_at", "type": "string", "value": "={{ $now.toISO() }}"}]}}, [1360, -60])

# API branch
http("API: start export", "POST", f"{API}/extractions/url/", [480, 260],
     body=f"={{{{ JSON.stringify({{ linkedin_url: {S}.list_url, search_name: 'MCP vs API test (n8n, API)' }}) }}}}")
node("API: wait 30 s", "n8n-nodes-base.wait", 1.1, {"amount": 30}, [700, 260], webhookId=str(uuid.uuid4()))
http("API: poll", "GET", f"={API}/extractions/{{{{ $('API: start export').first().json.extraction_id }}}}/",
     [920, 260], full=True)
node("API: finished?", "n8n-nodes-base.if", 2.2, {"conditions": {"options": {"caseSensitive": True, "typeValidation": "loose"},
     "conditions": [{"id": "s", "leftValue": "={{ $json.statusCode }}", "rightValue": 200,
                     "operator": {"type": "number", "operation": "equals"}}],
     "combinator": "and"}}, [1140, 260])
node("API: done at", "n8n-nodes-base.set", 3.4, {"assignments": {"assignments": [
    {"id": "d", "name": "done_at", "type": "string", "value": "={{ $now.toISO() }}"}]}}, [1360, 240])

node("Wait for both", "n8n-nodes-base.merge", 3.1, {"mode": "chooseBranch", "chooseBranchMode": "waitForAll",
     "output": "empty"}, [1580, 120])
code("Compare", SUMMARY_JS, [1800, 120])

for a, b in [("Run", "Your settings"), ("Your settings", "MCP: export"), ("MCP: export", "MCP: wait 30 s"), ("MCP: wait 30 s", "MCP: results"),
             ("MCP: results", "MCP: finished?"), ("MCP: finished?", "MCP: done at"),
             ("Your settings", "API: start export"), ("API: start export", "API: wait 30 s"),
             ("API: wait 30 s", "API: poll"), ("API: poll", "API: finished?"), ("API: finished?", "API: done at")]:
    link(a, b)
link("MCP: finished?", "MCP: wait 30 s", out=1)   # not done yet: wait and ask again
link("API: finished?", "API: wait 30 s", out=1)   # 202: wait and poll again
link("MCP: done at", "Wait for both")
connections.setdefault("API: done at", {"main": [[]]})["main"][0].append(
    {"node": "Wait for both", "type": "main", "index": 1})
link("Wait for both", "Compare")

wf = {"name": "MCP vs API: the same Evaboot export, both ways", "nodes": nodes, "connections": connections,
      "settings": {"executionOrder": "v1"}, "pinData": {}}
out = Path(__file__).with_name("mcp-vs-api-export.json")
out.write_text(json.dumps(wf, indent=2) + "\n")
print(f"wrote {out} ({len(nodes)} nodes)")
