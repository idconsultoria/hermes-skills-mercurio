"""fathom_api.py — cliente mínimo da API REST do Fathom (stdlib apenas).

Recriado em 27/10/2026 pelo Mercúrio: o módulo original sumiu do nó (a skill
`productivity/fathom` não existia mais) e o `phronesis_weekly.py` quebrava em
`from fathom_api import FathomClient`. Este shim cobre só o que o pipeline usa.

Uso:
    from fathom_api import FathomClient
    c = FathomClient()
    c.list_meetings(limit=50, include_summary=True, include_transcript=True,
                    include_action_items=True, created_after="2026-10-19T00:00:00Z")
"""
import json
import os
import time
import urllib.parse
import urllib.request
import urllib.error

API_BASE = "https://api.fathom.ai/external/v1"


def _api_key():
    home = os.environ.get("HERMES_HOME", "/data/data/com.termux/files/home/capitolium")
    path = os.path.join(home, ".secrets", "fathom.env")
    if os.path.exists(path):
        for line in open(path):
            line = line.strip()
            if line.startswith("FATHOM_API_KEY="):
                v = line.split("=", 1)[1].strip().strip('"').strip("'")
                if v:
                    return v
    v = os.environ.get("FATHOM_API_KEY")
    if v:
        return v
    raise RuntimeError("FATHOM_API_KEY não encontrada em .secrets/fathom.env")


class FathomClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or _api_key()

    def _get(self, path, params=None, max_attempts=4):
        url = f"{API_BASE}{path}"
        if params:
            clean = {k: v for k, v in params.items() if v is not None}
            url += "?" + urllib.parse.urlencode(clean)
        last = None
        for attempt in range(max_attempts):
            try:
                req = urllib.request.Request(url, headers={"X-Api-Key": self.api_key})
                with urllib.request.urlopen(req, timeout=90) as r:
                    return json.loads(r.read().decode())
            except urllib.error.HTTPError as e:
                last = f"HTTP {e.code}: {e.read().decode()[:200]}"
                if e.code in (401, 403, 404):
                    raise RuntimeError(f"Fathom API: {last}")
                time.sleep(min(2 ** attempt, 20))
            except Exception as e:
                last = str(e)
                time.sleep(min(2 ** attempt, 20))
        raise RuntimeError(f"Fathom API falhou: {last}")

    def list_meetings(self, limit=50, include_summary=False, include_transcript=False,
                      include_action_items=False, created_after=None, cursor=None,
                      recorded_by=None):
        params = {
            "limit": limit,
            "include_summary": str(bool(include_summary)).lower(),
            "include_transcript": str(bool(include_transcript)).lower(),
            "include_action_items": str(bool(include_action_items)).lower(),
            "created_after": created_after,
            "cursor": cursor,
        }
        if recorded_by:
            params["recorded_by[]"] = recorded_by
        return self._get("/meetings", params)

    def get_meeting(self, recording_id):
        return self._get(f"/meetings/{recording_id}", {"include_summary": "true",
                                                      "include_transcript": "true"})
