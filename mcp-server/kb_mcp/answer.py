"""Grounded answer generation with DeepSeek (OpenAI-compatible API)."""

from __future__ import annotations

import os
from typing import Callable, Protocol

from .kb import Chunk, KnowledgeBase

SYSTEM_PROMPT = """你是“Real Niubility”（为电商客户提供垂直 AI Agent 的 FDE 公司）的新人入职助手。你只能依据下面提供的《新人入职手册》片段回答问题。
规则：
1. 只使用片段中的信息，不要编造人名、数字、流程；片段中没有答案时，明确说“手册中没有找到相关规定”，并建议联系对应的负责人或渠道（如果片段里有）。
2. 回答用简体中文，先给结论，再列关键细节（审批链、时限、金额、联系人等），简洁清楚。
3. 在引用信息的句子末尾标注来源编号，例如 [1]、[2]，编号对应片段编号。"""


class LLM(Protocol):
    def __call__(self, system: str, user: str) -> str: ...


def deepseek_llm() -> LLM | None:
    key = os.environ.get("DEEPSEEK_API_KEY")
    if not key:
        return None
    from openai import OpenAI

    client = OpenAI(
        api_key=key,
        base_url=os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
        timeout=float(os.environ.get("LLM_TIMEOUT", "60")),
    )
    model = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")

    def call(system: str, user: str) -> str:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            temperature=0.1,
            max_tokens=1024,
        )
        return (resp.choices[0].message.content or "").strip()

    return call


def build_context(hits: list[tuple[Chunk, float]]) -> str:
    blocks = []
    for n, (chunk, _score) in enumerate(hits, 1):
        blocks.append(f"[{n}] 来源：{chunk.source}（{chunk.title}）\n{chunk.text}")
    return "\n\n---\n\n".join(blocks)


def answer(kb: KnowledgeBase, question: str, top_k: int = 6, llm: LLM | None | Callable = "auto") -> dict:
    question = (question or "").strip()
    if not question:
        return {"answer": "请提供一个问题。", "sources": [], "mode": "empty"}
    hits = kb.search(question, top_k=top_k)
    sources = [
        {"ref": n, "path": c.path, "title": c.title, "heading": c.heading, "score": round(float(s), 3)}
        for n, (c, s) in enumerate(hits, 1)
    ]
    if not hits:
        return {
            "answer": "手册中没有找到相关内容。可以换个说法再问，或联系 HR 服务台（hr@nebulasail.example）。",
            "sources": [],
            "mode": "no_hits",
        }
    if llm == "auto":
        llm = deepseek_llm()
    if llm is None:
        # No model key configured: degrade to an extractive answer.
        best = hits[0][0]
        return {
            "answer": f"（未配置大模型，返回最相关的手册原文）\n\n{best.text}\n\n[1]",
            "sources": sources,
            "mode": "extractive",
        }
    user = f"手册片段：\n\n{build_context(hits)}\n\n问题：{question}"
    try:
        text = llm(SYSTEM_PROMPT, user)
        mode = "llm"
    except Exception as e:  # network / quota errors should not break the tool
        text = f"（大模型调用失败：{type(e).__name__}，返回最相关的手册原文）\n\n{hits[0][0].text}\n\n[1]"
        mode = "extractive_fallback"
    return {"answer": text, "sources": sources, "mode": mode}
