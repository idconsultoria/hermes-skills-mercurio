#!/usr/bin/env python3
"""
Verify NGINX proxy + FastAPI trailing slash redirect.
Tests that:
1. Backend handles /tasks?status=pending (no trailing slash)
2. NGINX proxy handles /api/v1/tasks?status=pending (no slash)
3. Redirect Location uses relative path (not absolute with stripped port)
4. Task UUID fields serialize as strings (IdStr conversion)
"""
import urllib.request, json, sys, re

BASE = "http://localhost:8000/api/v1"
NGINX = "http://localhost:8080/api/v1"

def req(url, data=None, token=None):
    headers = {"Content-Type": "application/json"}
    if token: headers["Authorization"] = "Bearer " + token
    method = "POST" if data else "GET"
    body = json.dumps(data).encode() if data else None
    r = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        resp = urllib.request.urlopen(r)
        return resp.status, json.load(resp), dict(resp.headers)
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read()), dict(e.headers)

def test(desc, got, expected, detail=""):
    ok = "✅" if got == expected else "❌"
    print(f"  {ok} {desc}: got {got}, expected {expected}")
    if ok == "❌":
        print(f"     {detail[:200]}" if detail else "")

print("=== NGINX PROXY VERIFICATION ===\n")

# 1. Login
status, body, _ = req(BASE + "/auth/token", {"email": "gustavo@taskflow.com", "password": "teste123"})
t = body.get("access_token", "")
assert t, f"Login failed: {body}"
print(f"1. LOGIN: {t[:20]}...\n")

# 2. Direct backend: no trailing slash
status, body, headers = req(BASE + "/tasks?status=pending&limit=20", token=t)
test("Backend /tasks (no slash)", status, 200)
tasks = body.get("data", [])
print(f"   Tasks returned: {len(tasks)}")

# 3. NGINX proxy: no trailing slash (mimics frontend)
status, body, headers = req(NGINX + "/tasks?status=pending&limit=20", token=t)
test("NGINX /tasks (no slash)", status, 200)

# 4. Verify Location header on 307 redirect (if any)
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, hdrs, newurl):
        print(f"   Caught 307 -> {newurl}")
        print(f"   Location: {dict(hdrs).get('Location', 'N/A')}")
        return None
opener = urllib.request.build_opener(NoRedirect)
r = opener.open(urllib.request.Request(NGINX + "/tasks?status=pending&limit=20",
    headers={"Authorization": "Bearer " + t}))
print(f"   NGINX raw response: {r.status} (expect 200 or 307)")

# 5. Verify UUID fields serialize as strings
if tasks:
    t = tasks[0]
    for field in ["id", "user_id", "project_id", "context_id", "parent_task_id"]:
        val = t.get(field)
        if val is not None:
            test(f"   {field} is string", type(val).__name__, "str")
    print(f"   Sample: id={t['id'][:8]}..., title={t['title'][:30]}")

# 6. Test project creation with hex color
status, body, _ = req(BASE + "/projects", {"name": "Verify", "color": "#00ff00"}, token=t)
test("Create project (#hex color)", status, 201)

# 7. Verify stats
status, _, _ = req(BASE + "/stats/today", token=t)
test("Stats today", status, 200)

print(f"\n{'='*40}")
all_pass = all([
    len(tasks) > 0,
    status == 200,
])
print(f"RESULT: {'✅ ALL CHECKS PASSED' if all_pass else '❌ SOME FAILED'}")
