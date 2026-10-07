import sys
from pathlib import Path

import pytest

SERVER_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SERVER_DIR.parent
sys.path.insert(0, str(SERVER_DIR))


@pytest.fixture(scope="session")
def kb():
    from kb_mcp.kb import KnowledgeBase

    return KnowledgeBase.load(REPO_ROOT)
