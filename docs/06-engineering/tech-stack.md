# 技术栈与系统地图

> 文档负责人：后端技术专家 沈默｜最近更新：2026-09-01

## 技术栈总览

| 层次 | 技术选型 |
|------|----------|
| 后端 | Java 17、Spring Boot 3、SailRPC（基于 Dubbo 3 的内部框架）、MyBatis-Plus；部分新服务使用 Go 1.22 |
| 前端 | React 18、TypeScript 5、Vite、帆设计（SailDesign，基于 Ant Design 5 二次封装）、pnpm monorepo |
| 移动端 | Flutter 3（导购 App）、微信/钉钉小程序（Taro） |
| 数据 | MySQL 8（PolarDB）、Redis 7、Elasticsearch 8、RocketMQ 5、Flink、MaxCompute、Hologres |
| AI | 小帆 AI 助手：大模型网关（统一接入通义千问、DeepSeek 等）、向量检索（Milvus） |
| 基础设施 | 阿里云（华东 1 杭州主站 + 华北 2 北京灾备）、ACK（Kubernetes）、Terraform |
| 研发工具 | GitLab（自建）、GitLab CI、帆舟发布平台、SonarQube、Nexus、Harbor |
| 监控 | Prometheus + Grafana、夜莺告警、SLS 日志、Sentry、SkyWalking 链路追踪 |

## 核心服务（部分）

| 服务 | 说明 | 负责组 | Owner |
|------|------|--------|-------|
| member-service | 会员中心 | CRM 后端组 | 陆一凡 |
| points-service | 积分 | CRM 后端组 | 钱程 |
| coupon-service | 优惠券 | CRM 后端组 | 钱程 |
| marketing-flow | 营销自动化引擎 | CRM 后端组 | 沈默 |
| fanke-admin-web | 管理后台前端 | CRM 前端组 | 叶知秋 |
| bi-query-engine | BI 查询引擎 | 数据平台组 | 许蔓 |
| open-gateway | 开放平台网关 | 基础架构组 | 马骁 |
| sail-sso | 统一账号 | 基础架构组 | 马骁 |
| guide-app | 导购 App | 移动端组 | 罗伊 |

服务清单的权威来源是帆舟“服务目录”，每个服务都登记了 Owner、值班组、SLO 和告警群。

## 环境

| 环境 | 用途 | 数据 | 谁可以发布 |
|------|------|------|-----------|
| dev | 开发联调 | 假数据 | 所有研发，合并到 feature 分支自动部署 |
| test | 测试验证 | 假数据 | 测试工程师 / 研发 |
| staging（预发） | 上线前验证，连接生产中间件的隔离副本 | 脱敏的生产数据 | 有预发权限的研发 |
| prod（生产） | 正式环境 | 真实客户数据 | 有生产发布权限的研发，经帆舟审批 |
