# 技术栈与系统地图

> 文档负责人：平台架构师 沈默｜最近更新：2026-10-01

## 技术栈总览

| 层次 | 技术选型 |
|------|----------|
| Agent 运行时（NAP） | Python 3.12、FastAPI、自研编排引擎（状态机 + 工具调用），部分高并发组件用 Go 1.22 |
| 大模型 | 通过**模型网关**统一接入：通义千问、DeepSeek、豆包；按场景路由（客服用低延迟模型，内容生成用强模型） |
| RAG / 知识库 | Elasticsearch 8（BM25）+ Milvus（向量）混合检索，bge 系列 Embedding，重排模型 |
| 评测 | NEval：评测集管理、LLM-as-judge、人工评测工作台、回归报告 |
| 电商连接器 | 淘宝开放平台（TOP）、京东宙斯、抖店开放平台、拼多多开放平台；千牛 / 京麦 / 飞鸽客服接入 |
| 数据 | PostgreSQL 16（RDS）、Redis 7、RocketMQ 5、OSS；经营分析 Agent 使用 Hologres |
| 前端 | 客户控制台：React 18 + TypeScript + Ant Design 5 |
| 基础设施 | 阿里云 ACK（Kubernetes）+ **聚石塔**；京东云鼎、抖音电商云、多多云按客户渠道部署；Terraform |
| 研发工具 | GitLab（自建）、GitLab CI、Launchpad 发布平台、SonarQube、Harbor |
| 监控 | Prometheus + Grafana、夜莺告警、SLS 日志、Sentry、Langfuse（Agent 调用链与 Token 成本） |

## NAP 核心组件

| 组件 | 说明 | Owner |
|------|------|-------|
| nap-runtime | Agent 编排、会话记忆、工具调用、HITL 审核流 | 沈默 |
| nap-gateway | 模型网关：路由、脱敏、审计、限流、成本统计 | 马骁 |
| nap-connectors | 四大电商平台连接器与客服工作台接入 | 马骁团队 |
| nap-kb | 知识库与 RAG（商品资料、售后政策、FAQ） | 马骁团队 |
| neval | 评测中心 | 许蔓 |
| nap-console | 客户控制台（Agent 配置、效果看板、人工接管） | 叶知秋（FDE 兼任前端 Owner） |
| launchpad | 发布平台（代码、Prompt、知识库统一发布与回滚） | 高远 |

## 环境

| 环境 | 用途 | 数据 | 谁可以发布 |
|------|------|------|-----------|
| dev | 开发联调 | 合成数据 | 所有研发 |
| test | 评测与验收 | 合成数据 + 经授权脱敏的客户样本 | FDE / 测试 |
| staging（每个客户一个租户） | 上线前客户验收（UAT） | 客户授权的脱敏数据或客户测试店铺 | 有预发权限的 FDE |
| prod（每个客户一个租户，按渠道部署在聚石塔 / 云鼎等） | 正式环境 | 客户真实数据 | 有生产发布权限的 FDE，经 Launchpad 审批 |

## 客户隔离

- 每个客户在 NAP 中是独立租户：独立的知识库索引、Prompt 配置、工具凭证和日志。
- 淘宝/天猫客户的订单与消费者数据只在聚石塔内的租户中处理，不出聚石塔；京东、抖音、拼多多同理。
- 跨客户的评测集、Prompt 片段复用前，必须去除客户标识并经白冰审核。
