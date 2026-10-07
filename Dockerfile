# MCP knowledge Q&A service. The handbook (docs/) is bundled into the image at build time,
# so every push to main produces an image whose KB matches that commit exactly.
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 KB_ROOT=/app
WORKDIR /app
COPY mcp-server/requirements.txt mcp-server/requirements.txt
RUN pip install --no-cache-dir -r mcp-server/requirements.txt
COPY docs docs
# KB_COMMIT is stamped by the CI deploy job (railway up); README.md keeps the glob non-empty.
COPY README.md KB_COMMIT* ./
COPY mcp-server mcp-server
WORKDIR /app/mcp-server
# Warm jieba's dictionary cache so cold starts are fast.
RUN python -c "import jieba; jieba.initialize()" && python -c "from kb_mcp.kb import KnowledgeBase; print(KnowledgeBase.load('/app').stats())"
EXPOSE 8000
CMD ["python", "-m", "kb_mcp.server"]
