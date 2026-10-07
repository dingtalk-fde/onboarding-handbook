# onboarding-handbook MCP 服务

基于仓库 `docs/` 下 Markdown 制度文档的知识问答 MCP 服务。

## 线上地址

- MCP（Streamable HTTP）：`https://onboarding-kb-mcp-production.up.railway.app/mcp`
- 健康检查：`https://onboarding-kb-mcp-production.up.railway.app/health`

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

Streamable HTTP 端点：`https://onboarding-kb-mcp-production.up.railway.app/mcp`

Cursor / Claude Desktop 等（`mcp.json`）：

```json
{
  "mcpServers": {
    "onboarding-handbook": { "url": "https://onboarding-kb-mcp-production.up.railway.app/mcp" }
  }
}
```

仅支持 stdio 的客户端可借助 `mcp-remote`：`npx mcp-remote https://onboarding-kb-mcp-production.up.railway.app/mcp`。

用 curl 直接调用：

```bash
URL=https://onboarding-kb-mcp-production.up.railway.app/mcp
H='-H Content-Type:application/json -H Accept:application/json,text/event-stream'
curl -s $URL $H -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"curl","version":"1"}}}'
curl -s $URL $H -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"ask","arguments":{"question":"试用期多久？"}}}'
```

## 部署（Railway）

项目 `onboarding-kb-mcp`，两个服务都以本 GitHub 仓库为源（服务设置通过 Railway 控制台 / API 配置，不使用 config-as-code 文件）：

| 服务 | 构建 | 运行 | 关键设置 |
|------|------|------|----------|
| `onboarding-kb-mcp` | 根目录 `Dockerfile` | 常驻，`python -m kb_mcp.server` | 健康检查 `/health`；变量 `DEEPSEEK_API_KEY`、`DEEPSEEK_MODEL`、`PORT=8000`；GitHub autodeploy（main） |
| `kb-healthcheck` | `healthcheck/Dockerfile` | **Cron `*/15 * * * *`**，运行 `check.py` 后退出 | 变量 `MCP_URL`、`GITHUB_REPO`、`SYNC_GRACE_MINUTES`；重启策略 NEVER |

`check.py` 检查：`/health` 正常且文档数达标 → MCP `initialize` + `tools/list` + `tools/call search` → 服务加载的 KB commit 与 GitHub `main` 最新 commit 一致（push 后 30 分钟内视为 PENDING-DEPLOY）。输出一行 `RESULT OK` / `RESULT FAIL`，失败时退出码非零。

CI/CD（`.github/workflows/ci.yml`，名称 “CI/CD”）：
- 触发：`pull_request`、push 到 `main`、手动 `workflow_dispatch`
- `test`：pytest（分块/检索/回答 + 启动真实服务的 MCP 客户端冒烟测试）
- `docker-build`：构建两个镜像，容器内跑一遍 healthcheck
- `deploy`（仅 push 到 main，且前两个 job 通过）：**push 到 main 即自动部署**。用仓库 Secret `RAILWAY_TOKEN`（Railway 项目 token，onboarding-kb-mcp / production，已配置）执行 `railway up --ci` 部署 `onboarding-kb-mcp` 和 `kb-healthcheck` 两个服务（构建前写入 `KB_COMMIT` 标记本次 commit），然后轮询 `/health` 直到线上 commit 等于本次提交，再跑一次完整的健康/MCP/同步检查。任何一步失败，job 变红。
- 不需要手动部署；Railway 侧未安装 GitHub App，因此部署完全由这个 job 触发（测试不过就不会部署）。如果 Secret 被删除，job 会打印提示并跳过部署，此时 `kb-healthcheck` 会在 push 30 分钟后报 “stale KB”。

`.github/workflows/post-deploy.yml`：手动或 `deployment_status` 触发，对公网端点运行同样的检查。
