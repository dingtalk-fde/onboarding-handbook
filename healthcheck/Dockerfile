# Railway cron job: health + sync check of the MCP service. Build context = repo root.
FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY healthcheck/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY healthcheck/check.py .
CMD ["python", "check.py"]
