"""Load Markdown docs, chunk them by heading, and index them with BM25 (jieba tokenizer)."""

from __future__ import annotations

import hashlib
import logging
import os
import re
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path

import warnings

warnings.filterwarnings("ignore", category=SyntaxWarning)
import jieba  # noqa: E402
from rank_bm25 import BM25Okapi  # noqa: E402

jieba.setLogLevel(logging.WARNING)

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
MAX_CHUNK_CHARS = 1200

# Tokens that carry no retrieval signal.
_STOPWORDS = set(
    "的 了 是 在 和 与 及 或 等 也 都 就 而 被 把 让 给 对 从 向 为 以 于 之 其 这 那 有 没有 不 吗 呢 吧 啊 哪 什么 怎么 如何 多少 多久 几 个 我 你 他 她 我们 你们 请 可以 需要 要 会 能 一个 如果 时候 哪些 谁".split()
)
_TOKEN_OK = re.compile(r"[\w\u4e00-\u9fff]")


def tokenize(text: str) -> list[str]:
    tokens = []
    for tok in jieba.lcut_for_search(text.lower()):
        tok = tok.strip()
        if not tok or tok in _STOPWORDS or not _TOKEN_OK.search(tok):
            continue
        tokens.append(tok)
    return tokens


@dataclass
class Chunk:
    id: int
    path: str  # repo-relative path, e.g. docs/02-onboarding/probation.md
    title: str  # document H1
    heading: str  # heading path inside the doc, e.g. "试用期期限"
    text: str

    @property
    def source(self) -> str:
        return f"{self.path}#{self.heading}" if self.heading else self.path

    def as_dict(self, score: float | None = None) -> dict:
        d = {"id": self.id, "path": self.path, "title": self.title, "heading": self.heading, "text": self.text}
        if score is not None:
            d["score"] = round(float(score), 4)
        return d


def _split_long(text: str, limit: int = MAX_CHUNK_CHARS) -> list[str]:
    if len(text) <= limit:
        return [text]
    parts, buf = [], ""
    for para in re.split(r"\n\s*\n", text):
        if buf and len(buf) + len(para) + 2 > limit:
            parts.append(buf.strip())
            buf = ""
        buf += para + "\n\n"
    if buf.strip():
        parts.append(buf.strip())
    return parts


def chunk_markdown(path: str, content: str) -> list[tuple[str, str, str]]:
    """Return (title, heading_path, text) tuples, one per heading section (H2/H3), long ones split."""
    title = ""
    stack: list[tuple[int, str]] = []
    sections: list[tuple[str, list[str]]] = []
    current_heading, current_lines = "", []
    in_code = False

    def flush():
        body = "\n".join(current_lines).strip()
        if body:
            sections.append((current_heading, [body]))

    for line in content.splitlines():
        if line.strip().startswith("```"):
            in_code = not in_code
        m = None if in_code else HEADING_RE.match(line)
        if m:
            level, text = len(m.group(1)), m.group(2).strip()
            if level == 1:
                if not title:
                    title = text
                    continue
            flush()
            current_lines = []
            while stack and stack[-1][0] >= level:
                stack.pop()
            stack.append((level, text))
            current_heading = " > ".join(h for _, h in stack)
            continue
        current_lines.append(line)
    flush()

    title = title or Path(path).stem
    out = []
    for heading, bodies in sections:
        for body in bodies:
            for piece in _split_long(body):
                out.append((title, heading, piece))
    return out


def _git_commit(root: Path) -> str | None:
    try:
        return subprocess.check_output(
            ["git", "-C", str(root), "rev-parse", "HEAD"], stderr=subprocess.DEVNULL, text=True
        ).strip()
    except Exception:
        return None


def _resolve_commit(root: Path) -> str | None:
    """Which git commit the bundled docs came from.

    Order: $KB_COMMIT, a KB_COMMIT file stamped by CI (used for `railway up` deploys),
    Railway's $RAILWAY_GIT_COMMIT_SHA (GitHub-sourced deploys), then the local git checkout."""
    if os.environ.get("KB_COMMIT"):
        return os.environ["KB_COMMIT"].strip()
    stamp = root / "KB_COMMIT"
    if stamp.is_file() and stamp.read_text().strip():
        return stamp.read_text().strip()
    return os.environ.get("RAILWAY_GIT_COMMIT_SHA") or _git_commit(root)


@dataclass
class KnowledgeBase:
    root: Path
    chunks: list[Chunk] = field(default_factory=list)
    docs: dict[str, str] = field(default_factory=dict)  # path -> title
    raw: dict[str, str] = field(default_factory=dict)  # path -> full markdown
    content_hash: str = ""
    commit: str | None = None
    loaded_at: float = 0.0
    _bm25: BM25Okapi | None = None

    @classmethod
    def load(cls, root: str | os.PathLike, docs_subdir: str = "docs") -> "KnowledgeBase":
        root = Path(root).resolve()
        docs_dir = root / docs_subdir
        if not docs_dir.is_dir():
            raise FileNotFoundError(f"docs directory not found: {docs_dir}")
        kb = cls(root=root)
        hasher = hashlib.sha256()
        corpus = []
        for f in sorted(docs_dir.rglob("*.md")):
            rel = f.relative_to(root).as_posix()
            content = f.read_text(encoding="utf-8")
            hasher.update(rel.encode() + b"\0" + content.encode())
            kb.raw[rel] = content
            pieces = chunk_markdown(rel, content)
            kb.docs[rel] = pieces[0][0] if pieces else f.stem
            for title, heading, text in pieces:
                chunk = Chunk(id=len(kb.chunks), path=rel, title=title, heading=heading, text=text)
                kb.chunks.append(chunk)
                # Title and heading are repeated to boost them in ranking.
                corpus.append(tokenize(f"{title} {heading} {heading} {text}"))
        if not kb.chunks:
            raise ValueError(f"no markdown content under {docs_dir}")
        kb._bm25 = BM25Okapi(corpus)
        kb.content_hash = hasher.hexdigest()[:16]
        kb.commit = _resolve_commit(root)
        kb.loaded_at = time.time()
        return kb

    def search(self, query: str, top_k: int = 5) -> list[tuple[Chunk, float]]:
        top_k = max(1, min(int(top_k), 20))
        q = tokenize(query)
        if not q:
            return []
        scores = self._bm25.get_scores(q)
        ranked = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        return [(self.chunks[i], scores[i]) for i in ranked[:top_k] if scores[i] > 0]

    def topics(self) -> list[dict]:
        groups: dict[str, list[dict]] = {}
        for path, title in self.docs.items():
            section = path.split("/")[1] if path.count("/") >= 2 else "root"
            groups.setdefault(section, []).append({"path": path, "title": title})
        return [{"section": k, "documents": v} for k, v in sorted(groups.items())]

    def get_document(self, path: str) -> str | None:
        path = path.strip().lstrip("/")
        if path in self.raw:
            return self.raw[path]
        if not path.startswith("docs/") and f"docs/{path}" in self.raw:
            return self.raw[f"docs/{path}"]
        return None

    def stats(self) -> dict:
        return {
            "docs": len(self.docs),
            "chunks": len(self.chunks),
            "content_hash": self.content_hash,
            "commit": self.commit,
            "loaded_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(self.loaded_at)),
        }
