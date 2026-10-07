# 代码与 Prompt 规范

> 文档负责人：沈默（平台/后端）、叶知秋（前端）、许蔓（Prompt 与评测）｜最近更新：2026-10-01｜规范的变更需通过架构评审委员会

## 通用原则

1. **可读性优先**：代码是写给人看的。命名清晰胜过注释。
2. **小步提交**：一个 MR 只做一件事，代码改动建议不超过 400 行（不含自动生成代码、评测数据）。
3. **测试是代码的一部分**：工具（Tool）代码必须有单元测试，NAP 核心组件行覆盖率不低于 **70%**，CI 检查增量覆盖率 ≥ 80%。
4. **安全默认**：禁止在代码、配置、Prompt、日志中出现明文密钥、电商平台 AppSecret、Access Token；统一使用 KMS。
5. **日志规范**：结构化日志（JSON），必须带 traceId 和 tenant_id；**禁止打印消费者姓名、手机号、收货地址明文**，需调用 `RnMask` 脱敏。

## Python（NAP 与客户项目）

- 格式化与检查：`ruff` + `ruff format`，类型检查 `mypy --strict`（平台仓库）；配置统一使用 `rn-python-config`。
- 依赖管理用 `uv`，锁定版本提交 `uv.lock`。
- 工具（Tool）定义：每个工具必须声明 **输入 Schema、权限级别（只读 / 写 / 资金类）、超时、幂等键**；写操作和资金类工具（退款、改价、发券）必须支持 HITL 审核开关。
- 调用电商平台 API 必须通过 `nap-connectors`，禁止在客户项目里直接调用平台接口（统一处理限流、签名、审计）。
- 数据库：表必须有 `id`、`created_at`、`updated_at`、`tenant_id`；DDL 走 Launchpad 数据库变更工单，由 DBA 唐毅审核。

## 前端（TypeScript / React，客户控制台）

- ESLint + Prettier 使用公司共享包 `@rn/eslint-config`，husky + lint-staged 提交前检查。
- 组件基于 Ant Design 5；状态管理 Zustand，服务端数据用 TanStack Query。
- 所有用户可见文案走 i18n，不允许硬编码。

## Prompt 规范

- **Prompt 即代码**：放在仓库 `prompts/` 目录，用 Markdown + 变量模板，禁止只在控制台修改线上 Prompt。
- 每个 Prompt 文件头部写明：用途、适用渠道（天猫/京东/抖音/拼多多）、依赖的工具、对应评测集、负责人。
- 必须包含的护栏（Guardrail）：
  - 不承诺超出店铺政策的赔付（如“假一赔十”“无理由退款”），不编造发货时间和库存
  - 遵守平台客服规则（禁止引导站外交易、禁止索要好评、禁止辱骂/诱导）
  - 不输出消费者隐私信息，不泄露其他客户/店铺的数据
  - 无法确定时转人工，而不是猜测
- 每次 Prompt 变更必须跑 NEval 回归评测并在 MR 中附报告链接；新发现的 Badcase 必须先加入评测集。
- 修改模型（换模型或升级版本）视同 Prompt 变更，同样需要回归评测。

## 提交信息规范（Conventional Commits）

```
<type>(<scope>): <subject>

<body>

Refs: <JIRA-KEY>-123
```

- `type`：feat / fix / refactor / perf / test / docs / chore / ci / **prompt** / **eval**
- 必须关联 Jira 编号，CI 会检查。示例：`prompt(after-sales): 补充临期食品退换说明 Refs: LYF-231`

## 代码扫描门禁

- SonarQube：新增代码不允许有 Blocker / Critical 问题。
- SAST 与密钥扫描（信息安全组维护规则）：高危漏洞或疑似密钥阻断合并；误报可在 MR 中 @周子涵 申请豁免。
- 依赖扫描：禁止引入 GPL/AGPL 许可证的依赖（需法务杜明哲审批）。
