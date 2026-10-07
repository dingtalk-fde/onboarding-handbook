# onboarding-handbook MCP 服务

基于仓库 `docs/` 下 Markdown 制度文档的知识问答 MCP 服务。

## 架构

```
docs/*.md ──按标题切块──► chunks ──jieba 分词──► BM25 索引（内存）
                                                  │
MCP 客户端 ──Streamable HTTP /mcp──► ask(question) ─┼─► top-k 片段 ──► DeepSeek（只依据片段作答，标注 [n]）
                                   search(query)  ─┘
```

- 开源组件：[MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)（FastMCP，Streamable HTTP）、[rank_bm25](https://github.com/dorianbrown/rank_bm25)、[jieba](https://github.com/fxsjy/jieba)、[openai-python](https://github.com/openai/openai-python)（调用 DeepSeek 的 OpenAI 兼容接口）。
- 知识库在**镜像构建时打包**：每次 push 到 main 都会构建出与该 commit 完全一致的知识库；`/health` 返回所加载的 commit（Railway 注入的 `RAILWAY_GIT_COMMIT_SHA`）和内容哈希，供定时任务比对是否与 GitHub main 同步。
- 无状态（`stateless_http`），可水平扩展；冷启动建索引 < 1 秒。

## 工具

| 工具 | 参数 | 返回 |
|------|------|------|
| `ask` | `question` | `{answer, sources[{ref,path,title,heading,score}], mode}`，`mode` 为 `llm` / `extractive` / `extractive_fallback` |
| `search` | `query`, `top_k`(1–20, 默认 5) | `{results[{path,title,heading,text,score}]}` |
| `list_topics` | — | 章节 → 文档列表，及知识库统计 |
| `get_document` | `path` | 文档完整 Markdown |

## 环境变量

| 变量 | 说明 | 默认 |
|------|------|------|
| `DEEPSEEK_API_KEY` | DeepSeek API Key（**只配置在部署平台，不要提交到仓库**） | 无（退化为原文检索） |
| `DEEPSEEK_MODEL` | 模型名 | `deepseek-chat` |
| `DEEPSEEK_BASE_URL` | API 地址 | `https://api.deepseek.com` |
| `PORT` / `HOST` | 监听地址 | `8000` / `0.0.0.0` |
| `KB_ROOT` | 包含 `docs/` 的目录 | 仓库根目录 |

## 本地运行与测试

```bash
cd mcp-server
pip install -r requirements-dev.txt
python -m pytest -v                       # 离线测试；设置 DEEPSEEK_API_KEY 后额外运行真实模型测试
DEEPSEEK_API_KEY=sk-... python -m kb_mcp.server   # http://localhost:8000/mcp
```

## 接入 MCP 客户端

Streamable HTTP 端点：`https://<your-domain>/mcp`

Cursor / Claude Desktop 等（`mcp.json`）：

```json
{
  "mcpServers": {
    "onboarding-handbook": { "url": "https://<your-domain>/mcp" }
  }
}
```

仅支持 stdio 的客户端可借助 `mcp-remote`：`npx mcp-remote https://<your-domain>/mcp`。

用 curl 直接调用：

```bash
URL=https://<your-domain>/mcp
H='-H Content-Type:application/json -H Accept:application/json,text/event-stream'
curl -s $URL $H -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"curl","version":"1"}}}'
curl -s $URL $H -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"ask","arguments":{"question":"试用期多久？"}}}'
```

## 部署（Railway）

- 服务 `onboarding-kb-mcp`：GitHub 仓库源，根目录 `Dockerfile` + `railway.toml`，健康检查 `/health`，开启 GitHub autodeploy + **Wait for CI**。
- 定时服务 `kb-healthcheck`：同一仓库，配置文件 `healthcheck/railway.toml`，cron `*/15 * * * *`，运行 `healthcheck/check.py`（检查 `/health`、MCP initialize + tools/list + tools/call search、以及加载的 commit 与 GitHub main 是否一致），失败时非零退出。
