# 新人常见问题（FAQ）——研发 / FDE 篇

**Q：入职后多久能拿到 GitLab 和 NAP 权限？**
A：直属上级会在入职当天在 Launchpad 申请“研发新人权限包”（GitLab、NAP 测试环境、NEval、Jira），一般 1–2 个工作日开通。客户租户和聚石塔等环境权限需要先通过客户数据安全考试，按项目申请。

**Q：代码怎么提交？分支怎么命名？**
A：从 `main` 拉 `feature/<Jira号>-<简述>` 或 `fix/...` 分支（每个客户一个 Jira 项目，如 `LYF-212`，平台用 `NAP-`），提交信息用 Conventional Commits 并带 Jira 编号（如 `prompt(after-sales): 补充临期食品退换说明 Refs: LYF-231`），推送后提 MR 到 `main`，禁止直接推 main，合并方式 Squash and merge。Prompt 也放在仓库 `prompts/` 目录里提交，不能只在控制台改。详见[Git 分支模型](../06-engineering/git-workflow.md)。

**Q：Code Review 规范是什么？需要几个人 Approve？**
A：核心仓库（NAP 运行时、模型网关、连接器、租户隔离、退款/改价等资金类工具）需要 **2 个** Approve，其中至少 1 个是模块 Owner 或组长；客户项目仓库需要 **1 个**。Reviewer 1 个工作日内首次反馈；评论用 `[必须]` `[建议]` `[疑问]` `[nit]` 前缀；Prompt 变更必须附 NEval 回归报告，Reviewer 要检查 Guardrail 没被削弱、Prompt 注入风险。详见[代码评审规范](../06-engineering/code-review.md)。

**Q：什么是评测门禁？**
A：任何 Prompt、模型、工具变更都要跑 NEval 回归评测：总通过率不低于线上基线，**安全与合规用例必须 100% 通过**，工具调用正确率 ≥ 95%，客服 P95 延迟 ≤ 3 秒。详见[CI/CD 与评测门禁](../06-engineering/ci-cd-release.md)。

**Q：试用期可以发布生产吗？**
A：不可以自己发布。生产发布权限需**转正后**申请（直属上级 → 部门负责人 → 雷鸣）；试用期内由导师代为在 Launchpad 发布。

**Q：什么时候可以发布？**
A：常规窗口周二、周四 14:00–17:00；周五 18:00 到周一 10:00 和节假日前一天 18:00 起封网；双十一（10/20–11/12）、618 等客户大促期间封网。客户自己的冻结期以客户为准。

**Q：一个客户项目从 PoC 到上线怎么走？**
A：商机评估 → Discovery（1–2 周，到现场梳理流程和指标）→ PoC（2–4 周，用双方确认的评测集验收）→ 签 SOW 和 DPA → 交付实施（4–8 周，UAT + 评测门禁 + 灰度）→ 持续运营（周报、Badcase 3 个工作日闭环）。详见[FDE 客户交付流程](../06-engineering/fde-delivery-process.md)。

**Q：可以用外部 AI 工具或直接调大模型 API 吗？**
A：不能把公司代码、Prompt 和 L2 及以上数据输入未经批准的外部 AI 工具，请用内部 NiuCopilot；Agent 调用模型必须经过模型网关（自动脱敏和审计），消费者个人信息不得原文发给模型，客户数据默认不得用于训练。

**Q：淘宝/天猫的订单数据可以拉到我们自己的服务器上处理吗？**
A：不可以。淘宝/天猫订单和消费者数据必须在**聚石塔**内处理，京东在京东云鼎，抖音在抖音电商云，拼多多在多多云。

**Q：什么是 P0 故障？**
A：多个客户 Agent 全面不可用、任何客户数据/消费者信息泄露、Agent 大面积违规承诺或错误资金操作。值班人 5 分钟内响应，在“故障作战室”@当周 IC，先止血（切人工、回滚、切模型）。详见[On-call 与故障处理](../06-engineering/oncall-incident.md)。

**Q：不小心把平台 AppSecret 或密钥提交到 GitLab 了怎么办？**
A：立即找 SRE 值班轮换该密钥（平台 AppSecret 需在开放平台重置），并上报 security@realniubility.example。只删除提交记录不够。

**Q：架构评审什么时候开？**
A：每周三 15:00–16:00，召集人沈默，议题提前一天在 Confluence“架构评审”空间提交。
