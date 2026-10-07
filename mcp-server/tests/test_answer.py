"""Answer generation tests. Offline tests use a fake LLM; live tests call DeepSeek."""

import os

import pytest

from kb_mcp.answer import answer


def test_answer_passes_grounded_context_to_llm(kb):
    seen = {}

    def fake_llm(system, user):
        seen["system"], seen["user"] = system, user
        return "试用期为 6 个月 [1]"

    out = answer(kb, "试用期多久？", llm=fake_llm)
    assert out["mode"] == "llm"
    assert out["answer"] == "试用期为 6 个月 [1]"
    assert "只能依据" in seen["system"]
    assert "[1] 来源：docs/02-onboarding/probation.md" in seen["user"]
    assert out["sources"][0]["path"] == "docs/02-onboarding/probation.md"
    assert [s["ref"] for s in out["sources"]] == list(range(1, len(out["sources"]) + 1))


def test_answer_extractive_without_llm(kb):
    out = answer(kb, "报销审批链", llm=None)
    assert out["mode"] == "extractive"
    assert "郑可" in out["answer"]


def test_answer_llm_failure_falls_back(kb):
    def broken(system, user):
        raise TimeoutError("boom")

    out = answer(kb, "试用期多久", llm=broken)
    assert out["mode"] == "extractive_fallback"
    assert out["sources"]


def test_answer_empty_and_no_hits(kb):
    assert answer(kb, "  ", llm=None)["mode"] == "empty"
    assert answer(kb, "？？？", llm=None)["mode"] == "no_hits"


@pytest.mark.live
@pytest.mark.skipif(not os.environ.get("DEEPSEEK_API_KEY"), reason="DEEPSEEK_API_KEY not set")
@pytest.mark.parametrize(
    "question,must_contain",
    [("试用期多久？", "6"), ("报销 2000 元以下找谁审批？", "郑可")],
)
def test_live_deepseek_answer(kb, question, must_contain):
    out = answer(kb, question)
    assert out["mode"] == "llm", out
    assert must_contain in out["answer"]
    assert "[" in out["answer"]  # cites sources
