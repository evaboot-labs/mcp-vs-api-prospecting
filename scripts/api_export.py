#!/usr/bin/env python3
"""The API side of the benchmark: one plain-language audience -> verified leads, through the Evaboot REST API.

Steps: quota check, search builder, URL extraction, poll until done, save the leads.
Every call is timed and written to results/api-run.json.

Usage:
  python3 scripts/api_export.py build "Heads of Sales at software companies ... in Lyon, France"
  python3 scripts/api_export.py export "<sales navigator url>" --name "MCP vs API test"

Run `build` first and open the URL in Sales Navigator: the API exports the WHOLE search
(1 credit per lead) and has no max_results, so check the result count before `export`.
Needs EVABOOT_API_KEY in .env (dash.evaboot.com > Integrations > API).
"""
import argparse, json, os, pathlib, sys, time, urllib.request, urllib.error

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = "https://api.evaboot.com/v1"


def key():
    if os.environ.get("EVABOOT_API_KEY"):
        return os.environ["EVABOOT_API_KEY"]
    env = ROOT / ".env"
    for line in (env.read_text().splitlines() if env.exists() else []):
        if line.startswith("EVABOOT_API_KEY="):
            return line.split("=", 1)[1].strip()
    sys.exit("EVABOOT_API_KEY missing: copy .env.example to .env and add your key")


LOG = []


def call(method, path, body=None):
    req = urllib.request.Request(BASE + path, method=method,
                                 data=json.dumps(body).encode() if body else None,
                                 headers={"Authorization": f"Bearer {key()}",
                                          "Content-Type": "application/json"})
    t = time.time()
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            code, raw = r.status, r.read()
    except urllib.error.HTTPError as e:
        code, raw = e.code, e.read()
    except urllib.error.URLError as e:  # network error: code 0, retried by the poll loop
        code, raw = 0, json.dumps({"error": str(e.reason)}).encode()
    try:
        data = json.loads(raw or b"{}")
    except ValueError:  # an HTML gateway page instead of JSON
        data = {"error": raw[:200].decode(errors="replace")}
    LOG.append({"call": f"{method} {path.split('?')[0]}", "status": code, "seconds": round(time.time() - t, 2)})
    return code, data


def save(name, obj):
    (ROOT / "results").mkdir(exist_ok=True)
    (ROOT / "results" / name).write_text(json.dumps(obj, indent=2, ensure_ascii=False))


def build(prompt):
    t0 = time.time()
    code, q = call("GET", "/quota/")
    print("quota:", code, q.get("quota", q).get("remaining"), "profiles left today")
    code, out = call("POST", "/search-builder/", {"description": prompt, "search_type": "LEAD"})
    print("search builder:", code)
    print(json.dumps(out.get("filters_used", out), indent=2, ensure_ascii=False))
    print("url:", out.get("url"))
    save("api-build.json", {"prompt": prompt, "response": out, "calls": LOG,
                            "seconds": round(time.time() - t0, 1)})


def export(url, name, poll_every):
    t0 = time.time()
    code, job = call("POST", "/extractions/url/", {"linkedin_url": url, "search_name": name})
    if code >= 300:
        sys.exit(f"extraction refused ({code}): {job}")
    xid = job["extraction_id"]
    print("extraction:", xid)
    retries = 0
    while True:
        code, res = call("GET", f"/extractions/{xid}/")
        if code == 200:
            break
        if code in (0, 502, 503, 504) and retries < 5:  # transient: wait and poll again
            retries += 1
            print(f"  {code or 'network error'}, retry {retries}/5")
        elif code != 202:
            sys.exit(f"poll failed ({code}): {res}. Read it later with GET /v1/extractions/{xid}/")
        else:
            print(f"  {res.get('status')} {res.get('progress')}%")
        time.sleep(poll_every)
    leads = res.get("prospects", [])
    save("api-leads.json", leads)
    save("api-run.json", {"extraction_id": xid, "url": url, "leads": len(leads),
                          "seconds": round(time.time() - t0, 1), "calls": LOG})
    print(f"done: {len(leads)} leads in {time.time() - t0:.0f} s, {len(LOG)} HTTP calls")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build"); b.add_argument("prompt")
    e = sub.add_parser("export"); e.add_argument("url"); e.add_argument("--name", default="MCP vs API test")
    e.add_argument("--poll-every", type=int, default=15)
    a = p.parse_args()
    build(a.prompt) if a.cmd == "build" else export(a.url, a.name, a.poll_every)
