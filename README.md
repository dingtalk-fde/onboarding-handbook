# 星河云帆科技 · 新人入职手册（Onboarding Handbook）

> ⚠️ 本仓库中的公司“星河云帆科技（NebulaSail）”、人员、邮箱、电话、地址均为**虚构**，用于演示“制度文档知识库 + MCP 知识问答服务”。

欢迎加入星河云帆！这里汇集了新人入职需要知道的一切：组织架构、入职流程、考勤请假、报销福利、IT 与权限、研发规范、沟通文化、安全保密和办事渠道。

**不想翻文档？** 直接问 MCP 知识问答服务（见下方[知识问答 MCP](#知识问答-mcp)）。

## 目录

### 00 欢迎
- [公司简介](docs/00-welcome/company-overview.md) · [企业文化与价值观](docs/00-welcome/culture-values.md) · [常用术语表](docs/00-welcome/glossary.md)

### 01 组织架构与人
- [组织架构总览（汇报关系）](docs/01-org/org-chart.md)
- [部门职责说明](docs/01-org/departments.md)
- [人员通讯录（关键岗位）](docs/01-org/people-directory.md)
- [跨部门对接人](docs/01-org/interface-people.md)
- [管理层与决策机制](docs/01-org/leadership-decision.md)

### 02 入职与试用期
- [入职第一天清单](docs/02-onboarding/day-1-checklist.md) · [入职第一周](docs/02-onboarding/first-week.md)
- [30/60/90 天计划](docs/02-onboarding/30-60-90-plan.md) · [试用期与转正](docs/02-onboarding/probation.md) · [Buddy 与导师](docs/02-onboarding/buddy-mentor.md)

### 03 考勤与假期
- [工作时间与考勤](docs/03-attendance-leave/working-hours.md) · [假期类型与审批](docs/03-attendance-leave/leave-types.md) · [加班、调休与值班](docs/03-attendance-leave/overtime.md)

### 04 报销与福利
- [费用报销制度](docs/04-expenses-benefits/reimbursement.md) · [差旅标准](docs/04-expenses-benefits/travel-policy.md)
- [福利与保险](docs/04-expenses-benefits/benefits-insurance.md) · [补贴与津贴](docs/04-expenses-benefits/allowances.md)

### 05 IT 设备与权限
- [IT 设备申请](docs/05-it-access/equipment.md) · [办公账号与权限](docs/05-it-access/accounts-access.md) · [网络与 VPN](docs/05-it-access/vpn-network.md)
- [研发系统权限开通](docs/05-it-access/dev-access.md) · [IT 服务台与 SLA](docs/05-it-access/it-service-sla.md)

### 06 研发规范与流程
- [技术栈与系统地图](docs/06-engineering/tech-stack.md) · [代码规范](docs/06-engineering/coding-standards.md) · [Git 分支模型](docs/06-engineering/git-workflow.md)
- [代码评审](docs/06-engineering/code-review.md) · [CI/CD 与发布](docs/06-engineering/ci-cd-release.md) · [On-call 与故障处理](docs/06-engineering/oncall-incident.md)

### 07 会议与沟通
- [会议文化](docs/07-communication/meeting-culture.md) · [沟通规范](docs/07-communication/communication-norms.md) · [OKR 与绩效](docs/07-communication/okr-performance.md)

### 08 安全与保密
- [数据分级](docs/08-security/data-classification.md) · [保密协议与规定](docs/08-security/confidentiality-nda.md)
- [安全事件上报](docs/08-security/security-incident.md) · [设备与网络使用规范](docs/08-security/acceptable-use.md)

### 09 办事渠道
- [常用办事渠道与联系方式](docs/09-service-channels/contacts.md) · [行政服务指南](docs/09-service-channels/admin-services.md)

### 10 FAQ
- [综合篇](docs/10-faq/faq-general.md) · [研发篇](docs/10-faq/faq-engineering.md)

---

## 知识问答 MCP

`mcp-server/` 是一个基于本仓库 Markdown 的**检索增强问答（RAG）MCP 服务**：

- 协议：MCP **Streamable HTTP**（官方 Python SDK `mcp` / FastMCP），端点 `/mcp`；健康检查 `/health`
- 检索：按标题切块 → `jieba` 中文分词 → `rank_bm25`（BM25Okapi）
- 生成：DeepSeek（OpenAI 兼容 API），只依据检索到的片段作答并标注 `[n]` 出处；未配置 Key 时退化为返回原文片段
- 工具：`ask(question)`、`search(query, top_k)`、`list_topics()`、`get_document(path)`

**线上端点**：`https://onboarding-kb-mcp-production.up.railway.app/mcp`（健康检查 `/health`）

```json
{ "mcpServers": { "onboarding-handbook": { "url": "https://onboarding-kb-mcp-production.up.railway.app/mcp" } } }
```

详见 [mcp-server/README.md](mcp-server/README.md)。

## 仓库结构

```
docs/                 手册正文（Markdown，按主题分目录）
mcp-server/           MCP 问答服务（Python）+ 测试
healthcheck/          Railway 定时任务：健康与同步检查
Dockerfile            MCP 服务镜像（构建时打包 docs/）
.github/workflows/    CI（测试 + 镜像构建）与部署后验证
```

## 贡献

制度有更新？直接提 PR 修改 `docs/` 下的文件。合并到 `main` 后，CI 通过即自动部署，问答服务几分钟内同步到最新内容。
