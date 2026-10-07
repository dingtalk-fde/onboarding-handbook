"""End-to-end smoke test: start the real server and talk to it with the official MCP client."""

import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import anyio
import httpx
import pytest
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

SERVER_DIR = Path(__file__).resolve().parents[1]


def _free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="module")
def server_url():
    external = os.environ.get("MCP_TEST_URL")  # e.g. a deployed instance
    if external:
        yield external.rstrip("/")
        return
    port = _free_port()
    env = {**os.environ, "PORT": str(port), "HOST": "127.0.0.1"}
    proc = subprocess.Popen([sys.executable, "-m", "kb_mcp.server"], cwd=SERVER_DIR, env=env,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    base = f"http://127.0.0.1:{port}"
    for _ in range(100):
        try:
            if httpx.get(base + "/health", timeout=1).status_code == 200:
                break
        except httpx.HTTPError:
            time.sleep(0.2)
    else:
        proc.kill()
        raise RuntimeError(proc.stdout.read().decode())
    yield base
    proc.terminate()
    proc.wait(10)


def test_health(server_url):
    r = httpx.get(server_url + "/health", timeout=10)
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["kb"]["docs"] >= 25
    assert body["mcp_endpoint"] == "/mcp"


async def _session_calls(url, calls):
    async with streamablehttp_client(url + "/mcp") as (read, write, _):
        async with ClientSession(read, write) as session:
            init = await session.initialize()
            tools = await session.list_tools()
            results = {}
            for name, args in calls:
                res = await session.call_tool(name, args)
                assert not res.isError, res
                results[name] = json.loads(res.content[0].text)
            return init, tools, results


def test_mcp_initialize_list_search(server_url):
    init, tools, results = anyio.run(
        _session_calls, server_url,
        [("search", {"query": "试用期多久", "top_k": 3}), ("list_topics", {})],
    )
    assert init.serverInfo.name == "onboarding-handbook"
    names = {t.name for t in tools.tools}
    assert {"ask", "search", "list_topics", "get_document"} <= names
    assert results["search"]["results"][0]["path"] == "docs/02-onboarding/probation.md"
    assert results["list_topics"]["docs"] >= 25


def test_mcp_ask(server_url):
    _, _, results = anyio.run(_session_calls, server_url, [("ask", {"question": "试用期多久？"})])
    out = results["ask"]
    assert out["sources"] and out["sources"][0]["path"].endswith("probation.md")
    if os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("MCP_TEST_URL"):
        assert out["mode"] == "llm", out
        assert "6" in out["answer"]
    else:
        assert out["mode"] == "extractive"
