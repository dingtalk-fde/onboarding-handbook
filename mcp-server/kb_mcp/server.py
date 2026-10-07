"""MCP server (Streamable HTTP) exposing the onboarding handbook as Q&A tools."""

from __future__ import annotations

import logging
import os
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from starlette.requests import Request
from starlette.responses import JSONResponse

from . import __version__
from .answer import answer as _answer
from .kb import KnowledgeBase

log = logging.getLogger("kb_mcp")

KB_ROOT = Path(os.environ.get("KB_ROOT", Path(__file__).resolve().parents[2]))
KB = KnowledgeBase.load(KB_ROOT)
log.warning("knowledge base loaded: %s", KB.stats())

mcp = FastMCP(
    name="onboarding-handbook",
    instructions=(
        "Real Niubility（FDE 模式的电商 AI Agent 公司）《新人入职手册》知识库。用 ask 直接提问获得带出处的答案；"
        "用 search 获取原文片段；用 list_topics / get_document 浏览手册。"
    ),
    host=os.environ.get("HOST", "0.0.0.0"),
    port=int(os.environ.get("PORT", "8000")),
    streamable_http_path="/mcp",
    stateless_http=True,
    json_response=True,
    # Public deployment behind Railway's proxy: Host header is the public domain.
    transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
)


@mcp.tool()
def ask(question: str) -> dict:
    """向新人入职手册提问（例如“试用期多久？”“报销找谁审批？”）。返回基于手册的答案和引用来源。"""
    return _answer(KB, question)


@mcp.tool()
def search(query: str, top_k: int = 5) -> dict:
    """在入职手册中做关键词检索（BM25 + 中文分词），返回最相关的原文片段及其文件路径。top_k 取值 1-20。"""
    hits = KB.search(query, top_k=top_k)
    return {"query": query, "results": [c.as_dict(score=s) for c, s in hits]}


@mcp.tool()
def list_topics() -> dict:
    """列出手册的所有章节和文档。"""
    return {"topics": KB.topics(), **KB.stats()}


@mcp.tool()
def get_document(path: str) -> dict:
    """按路径获取一篇手册文档的完整 Markdown，例如 docs/02-onboarding/probation.md。"""
    content = KB.get_document(path)
    if content is None:
        return {"error": f"document not found: {path}", "available": sorted(KB.docs)}
    return {"path": path, "content": content}


@mcp.custom_route("/health", methods=["GET"])
async def health(_: Request) -> JSONResponse:
    return JSONResponse(
        {
            "status": "ok",
            "service": "onboarding-handbook-mcp",
            "version": __version__,
            "kb": KB.stats(),
            "llm_configured": bool(os.environ.get("DEEPSEEK_API_KEY")),
            "mcp_endpoint": "/mcp",
        }
    )


@mcp.custom_route("/", methods=["GET"])
async def index(_: Request) -> JSONResponse:
    return JSONResponse(
        {
            "name": "onboarding-handbook-mcp",
            "mcp_endpoint": "/mcp (Streamable HTTP)",
            "health": "/health",
            "tools": ["ask", "search", "list_topics", "get_document"],
        }
    )


def main() -> None:
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
