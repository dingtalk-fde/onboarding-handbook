"""Scheduled health + sync check for the onboarding-handbook MCP service (runs as a Railway cron job).

Checks:
  1. GET {MCP_URL}/health returns status=ok with a sane doc count
  2. MCP initialize + tools/list + tools/call search over Streamable HTTP
  3. Sync: the KB commit the server loaded == latest commit on GitHub main
     (a mismatch younger than SYNC_GRACE_MINUTES is reported as PENDING-DEPLOY, not a failure)
Prints one clear OK/FAIL summary line and exits non-zero on failure.
"""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone

import httpx

MCP_URL = os.environ.get("MCP_URL", "").rstrip("/")
GITHUB_REPO = os.environ.get("GITHUB_REPO", "dingtalk-fde/onboarding-handbook")
GITHUB_BRANCH = os.environ.get("GITHUB_BRANCH", "main")
MIN_DOCS = int(os.environ.get("MIN_DOCS", "25"))
SYNC_GRACE_MINUTES = int(os.environ.get("SYNC_GRACE_MINUTES", "30"))
TIMEOUT = float(os.environ.get("CHECK_TIMEOUT", "20"))


def log(msg: str) -> None:
    print(f"[{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}] {msg}", flush=True)


def rpc(client: httpx.Client, method: str, params: dict | None, rid: int | None, session: str | None) -> dict:
    headers = {"Accept": "application/json, text/event-stream", "Content-Type": "application/json"}
    if session:
        headers["Mcp-Session-Id"] = session
    body = {"jsonrpc": "2.0", "method": method}
    if params is not None:
        body["params"] = params
    if rid is not None:
        body["id"] = rid
    r = client.post(f"{MCP_URL}/mcp", json=body, headers=headers)
    r.raise_for_status()
    if rid is None:
        return {"_session": r.headers.get("mcp-session-id")}
    text = r.text
    if r.headers.get("content-type", "").startswith("text/event-stream"):
        text = next(line[5:].strip() for line in text.splitlines() if line.startswith("data:"))
    data = json.loads(text)
    if "error" in data:
        raise RuntimeError(f"{method} error: {data['error']}")
    data["_session"] = r.headers.get("mcp-session-id") or session
    return data


def check_health(client: httpx.Client) -> dict:
    r = client.get(f"{MCP_URL}/health")
    r.raise_for_status()
    body = r.json()
    assert body.get("status") == "ok", f"status={body.get('status')}"
    docs = body["kb"]["docs"]
    assert docs >= MIN_DOCS, f"only {docs} docs loaded (< {MIN_DOCS})"
    log(f"health ok: docs={docs} chunks={body['kb']['chunks']} commit={body['kb']['commit']} llm={body.get('llm_configured')}")
    return body


def check_mcp(client: httpx.Client) -> None:
    t0 = time.monotonic()
    init = rpc(client, "initialize", {
        "protocolVersion": "2025-06-18",
        "capabilities": {},
        "clientInfo": {"name": "kb-healthcheck", "version": "1.0"},
    }, 1, None)
    session = init["_session"]
    rpc(client, "notifications/initialized", None, None, session)
    tools = rpc(client, "tools/list", {}, 2, session)["result"]["tools"]
    names = {t["name"] for t in tools}
    assert {"ask", "search"} <= names, f"tools missing: {names}"
    res = rpc(client, "tools/call", {"name": "search", "arguments": {"query": "试用期多久", "top_k": 1}}, 3, session)
    payload = json.loads(res["result"]["content"][0]["text"])
    top = payload["results"][0]["path"]
    assert top.endswith("probation.md"), f"unexpected top hit {top}"
    log(f"mcp ok: server={init['result']['serverInfo']['name']} tools={sorted(names)} search_top={top} ({(time.monotonic()-t0)*1000:.0f} ms)")


def latest_commit(client: httpx.Client) -> tuple[str, datetime]:
    """Latest commit (sha, commit time) on the branch. Uses the public Atom feed (no API rate limit),
    falling back to the REST API."""
    import re

    try:
        r = client.get(f"https://github.com/{GITHUB_REPO}/commits/{GITHUB_BRANCH}.atom",
                       headers={"Accept": "application/atom+xml"})
        r.raise_for_status()
        entry = r.text.split("<entry>", 1)[1]
        sha = re.search(r"Commit/([0-9a-f]{40})", entry).group(1)
        updated = re.search(r"<updated>([^<]+)</updated>", entry).group(1)
        return sha, datetime.fromisoformat(updated.replace("Z", "+00:00"))
    except Exception as e:
        log(f"atom feed unavailable ({type(e).__name__}), falling back to REST API")
    headers = {"Accept": "application/vnd.github+json"}
    if os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {os.environ['GITHUB_TOKEN']}"
    r = client.get(f"https://api.github.com/repos/{GITHUB_REPO}/commits/{GITHUB_BRANCH}", headers=headers)
    r.raise_for_status()
    data = r.json()
    return data["sha"], datetime.fromisoformat(data["commit"]["committer"]["date"].replace("Z", "+00:00"))


def check_sync(client: httpx.Client, loaded_commit: str | None) -> str:
    latest_sha, committed = latest_commit(client)
    age_min = (datetime.now(timezone.utc) - committed).total_seconds() / 60
    if loaded_commit and loaded_commit == latest_sha:
        log(f"sync ok: server is on {GITHUB_BRANCH}@{latest_sha[:7]}")
        return "IN-SYNC"
    if age_min < SYNC_GRACE_MINUTES:
        log(f"sync pending: server={str(loaded_commit)[:7]} latest={latest_sha[:7]} pushed {age_min:.0f} min ago (grace {SYNC_GRACE_MINUTES} min)")
        return "PENDING-DEPLOY"
    raise AssertionError(f"stale KB: server={str(loaded_commit)[:7]} latest={latest_sha[:7]} pushed {age_min:.0f} min ago")


def main() -> int:
    if not MCP_URL:
        log("FAIL config: MCP_URL is not set")
        return 2
    failures, sync = [], "UNKNOWN"
    with httpx.Client(timeout=TIMEOUT, follow_redirects=True) as client:
        health = None
        for name, fn in (("health", lambda: check_health(client)), ("mcp", lambda: check_mcp(client))):
            try:
                out = fn()
                if name == "health":
                    health = out
            except Exception as e:
                failures.append(f"{name}: {type(e).__name__}: {e}")
        try:
            sync = check_sync(client, (health or {}).get("kb", {}).get("commit"))
        except Exception as e:
            failures.append(f"sync: {type(e).__name__}: {e}")
    if failures:
        log(f"RESULT FAIL url={MCP_URL} sync={sync} :: " + " | ".join(failures))
        return 1
    log(f"RESULT OK url={MCP_URL} sync={sync}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
