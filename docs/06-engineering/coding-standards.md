# 代码规范

> 文档负责人：沈默（后端）、叶知秋（前端）、罗伊（移动端）｜最近更新：2026-08-25｜规范的变更需通过架构评审委员会

## 通用原则

1. **可读性优先**：代码是写给人看的。命名清晰胜过注释。
2. **小步提交**：一个 MR 只做一件事，代码改动建议不超过 400 行（不含自动生成代码和测试数据）。
3. **测试是代码的一部分**：新增业务逻辑必须有单元测试，核心服务行覆盖率不低于 **70%**，CI 门禁会检查增量覆盖率 ≥ 80%。
4. **安全默认**：禁止在代码、配置、日志中出现明文密钥、密码、Token；统一使用 KMS / 配置中心（Nacos 加密配置）。
5. **日志规范**：使用结构化日志（JSON），必须带 traceId；**禁止打印手机号、身份证号等个人信息明文**，需调用 `SailMask` 工具脱敏。

## 后端（Java）

- 遵循《阿里巴巴 Java 开发手册（嵩山版）》，并以 CI 中的 P3C 插件和 Checkstyle 为准。
- 包结构：`com.nebulasail.<产品>.<模块>.{api,application,domain,infrastructure}`（DDD 分层）。
- 接口定义放在独立的 `*-api` 模块，版本号遵循语义化版本，**不兼容变更必须升主版本并经架构评审**。
- 数据库：
  - 表名小写下划线，必须有 `id`、`gmt_create`、`gmt_modified`、`tenant_id` 字段
  - 禁止 `SELECT *`；单表数据超过 500 万行需评估分库分表
  - DDL 变更通过帆舟数据库变更工单，由 DBA 唐毅审核，禁止在代码中执行 DDL
- 异常：业务异常使用 `BizException(ErrorCode)`，错误码统一在 `error-codes` 仓库登记。

## 前端（TypeScript / React）

- ESLint + Prettier 配置使用公司共享包 `@sail/eslint-config`，提交前由 husky + lint-staged 自动检查。
- 组件优先使用 SailDesign；新增通用组件需先在“前端技术委员会”（叶知秋召集，每两周一次）评审。
- 状态管理使用 Zustand；服务端数据用 TanStack Query；禁止新增 Redux。
- 所有用户可见文案必须走 i18n（`t('key')`），不允许硬编码中文。

## 移动端（Flutter）

- 遵循 `flutter_lints` + 团队自定义规则，状态管理使用 Riverpod。
- 每次发版前必须通过真机兼容性测试（测试机柜覆盖 Top 20 机型）。

## 提交信息规范（Conventional Commits）

```
<type>(<scope>): <subject>

<body>

Refs: JIRA-1234
```

- `type`：feat / fix / refactor / perf / test / docs / chore / ci
- 必须关联 Jira 编号，CI 会检查。示例：`fix(points): 修复积分过期任务重复执行 Refs: CRM-4821`

## 代码扫描门禁

- SonarQube：新增代码不允许有 Blocker / Critical 问题。
- SAST（信息安全部维护规则）：高危漏洞阻断合并；误报可在 MR 中 @周子涵 申请豁免。
- 依赖扫描：禁止引入 GPL/AGPL 许可证的依赖（需法务杜明哲审批）。
