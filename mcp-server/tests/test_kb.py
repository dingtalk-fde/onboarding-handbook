"""Chunking and retrieval tests (offline)."""

import pytest

from kb_mcp.kb import chunk_markdown, tokenize


def test_chunk_by_heading_with_path():
    md = "# 标题\n\n引言\n\n## 一级\n\n内容A\n\n### 二级\n\n内容B\n\n```\n# 代码里的井号不是标题\n```\n"
    chunks = chunk_markdown("docs/x.md", md)
    assert all(t == "标题" for t, _, _ in chunks)
    headings = [h for _, h, _ in chunks]
    assert headings == ["", "一级", "一级 > 二级"]
    assert "代码里的井号" in chunks[-1][2]


def test_long_sections_are_split():
    para = "这是一段比较长的文字。" * 40
    md = "# T\n\n## S\n\n" + "\n\n".join([para] * 6)
    chunks = chunk_markdown("docs/x.md", md)
    assert len(chunks) > 1
    assert all(len(text) <= 1300 for _, _, text in chunks)


def test_tokenize_chinese_and_stopwords():
    toks = tokenize("试用期多久？报销找谁审批")
    assert "试用期" in toks and "报销" in toks and "审批" in toks
    assert "多久" not in toks and "？" not in toks


def test_kb_loads_all_docs(kb):
    stats = kb.stats()
    assert stats["docs"] >= 25
    assert stats["chunks"] > stats["docs"]
    assert len(stats["content_hash"]) == 16
    sections = {t["section"] for t in kb.topics()}
    for s in ["01-org", "02-onboarding", "03-attendance-leave", "04-expenses-benefits",
              "05-it-access", "06-engineering", "07-communication", "08-security",
              "09-service-channels", "10-faq"]:
        assert s in sections


@pytest.mark.parametrize(
    "question,expected_path",
    [
        ("试用期多久", "docs/02-onboarding/probation.md"),
        ("报销审批链", "docs/04-expenses-benefits/reimbursement.md"),
        ("SailGate VPN 连不上", "docs/05-it-access/vpn-network.md"),
        ("P0 故障等级定义", "docs/06-engineering/oncall-incident.md"),
        ("出差住宿标准 一线城市", "docs/04-expenses-benefits/travel-policy.md"),
        ("周五可以发布生产吗 封网", "docs/06-engineering/ci-cd-release.md"),
        ("年假怎么折算", "docs/03-attendance-leave/leave-types.md"),
        ("数据分级 L4 绝密", "docs/08-security/data-classification.md"),
    ],
)
def test_retrieval_top3_contains_expected_doc(kb, question, expected_path):
    hits = kb.search(question, top_k=3)
    assert hits, question
    assert expected_path in [c.path for c, _ in hits]


def test_search_bounds_and_empty(kb):
    assert kb.search("   ") == []
    assert len(kb.search("审批", top_k=100)) <= 20
    assert len(kb.search("审批", top_k=0)) == 1


def test_get_document(kb):
    assert kb.get_document("docs/02-onboarding/probation.md").startswith("# 试用期与转正")
    assert kb.get_document("02-onboarding/probation.md") is not None
    assert kb.get_document("docs/nope.md") is None


def test_commit_resolution_order(tmp_path, monkeypatch):
    from kb_mcp.kb import _resolve_commit

    monkeypatch.delenv("KB_COMMIT", raising=False)
    monkeypatch.setenv("RAILWAY_GIT_COMMIT_SHA", "railwaysha")
    assert _resolve_commit(tmp_path) == "railwaysha"
    (tmp_path / "KB_COMMIT").write_text("stampedsha\n")
    assert _resolve_commit(tmp_path) == "stampedsha"
    monkeypatch.setenv("KB_COMMIT", "envsha")
    assert _resolve_commit(tmp_path) == "envsha"
