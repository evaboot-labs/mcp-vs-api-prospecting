#!/usr/bin/env python3
"""Compare the MCP export and the API export of the same list. Writes results/comparison.md.

Reads results/{mcp,api}-leads.json (the prospects arrays) and results/{mcp,api}-run.json (timings).
Prints aggregates only: no names, no emails.
"""
import json, pathlib

R = pathlib.Path(__file__).resolve().parent.parent / "results"


def load(name, default):
    p = R / name
    return json.loads(p.read_text()) if p.exists() else default


def key(lead):
    return (lead.get("Linkedin URL Unique ID") or lead.get("Sales Navigator URL") or
            f"{lead.get('First Name')} {lead.get('Last Name')}|{lead.get('Company Name')}")


def stats(leads):
    status = {}
    for l in leads:
        s = l.get("Email Status") or "none"
        status[s] = status.get(s, 0) + 1
    return {"leads": len(leads), "emails": sum(1 for l in leads if l.get("Email")),
            "safe": status.get("safe", 0), "status": status,
            "matches": sum(1 for l in leads if str(l.get("Matches Filters", "")).upper() == "YES"),
            "columns": len(leads[0]) if leads else 0}


mcp, api = load("mcp-leads.json", []), load("api-leads.json", [])
mrun, arun = load("mcp-run.json", {}), load("api-run.json", {})
m, a = stats(mcp), stats(api)
mk, ak = {key(l): l for l in mcp}, {key(l): l for l in api}
both = mk.keys() & ak.keys()
diff_email = sum(1 for k in both if mk[k].get("Email") != ak[k].get("Email"))
diff_status = sum(1 for k in both if mk[k].get("Email Status") != ak[k].get("Email Status"))
cols = sorted(set(mcp[0]) ^ set(api[0])) if mcp and api else []

rows = [("Leads returned", m["leads"], a["leads"]),
        ("Emails found", m["emails"], a["emails"]),
        ("Safe emails", m["safe"], a["safe"]),
        ("Matches filters = YES", m["matches"], a["matches"]),
        ("Columns per lead", m["columns"], a["columns"]),
        ("Seconds, start to leads", mrun.get("seconds", "?"), arun.get("seconds", "?")),
        ("Calls made", mrun.get("tool_calls", "?"), len(arun.get("calls", [])) or "?")]
md = ["# MCP vs API: the same export", "",
      "| | MCP | API |", "|---|---|---|"] + [f"| {r[0]} | {r[1]} | {r[2]} |" for r in rows] + [
      "", f"Same leads in both: {len(both)}. Different email: {diff_email}. Different email status: {diff_status}.",
      f"Columns in only one of the two: {', '.join(cols) if cols else 'none'}.",
      f"Email status, MCP: {m['status']}. API: {a['status']}."]
(R / "comparison.md").write_text("\n".join(md) + "\n")
w = max(len(r[0]) for r in rows)
print(f"{'':<{w}}  {'MCP':>6}  {'API':>6}")
for r in rows:
    print(f"{r[0]:<{w}}  {str(r[1]):>6}  {str(r[2]):>6}")
print("\n" + "\n".join(md[-3:]))
print("Written to results/comparison.md")
