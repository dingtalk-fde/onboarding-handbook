# 研发系统与客户环境权限开通

> 文档负责人：SRE 组长 雷鸣 & 信息安全负责人 白冰｜最近更新：2026-10-01｜内部研发权限通过 **Launchpad → 权限中心** 申请（https://launchpad.realniubility.example）

## 新人研发权限包

技术岗新人入职当天，直属上级会在 Launchpad 申请“**研发新人权限包**”，一般在**入职第 1–2 个工作日内**开通：

| 系统 | 默认权限 | 地址 |
|------|----------|------|
| GitLab | 所在团队 Group 的 Developer 权限 | https://gitlab.realniubility.example |
| NAP 测试环境 | 创建 Agent、使用示例店铺数据（脱敏 / 合成数据） | https://nap-test.realniubility.example |
| NEval 评测中心 | 查看评测集、发起评测（测试环境） | https://neval.realniubility.example |
| Jira / Confluence | 所在团队项目读写 | jira / wiki.realniubility.example |
| 模型网关（测试额度） | 每人每天 200 元模型调用额度，仅限测试环境 | 通过 NAP 调用 |
| Sentry、Grafana | 所在团队项目只读 | sentry / grafana.realniubility.example |

## 需要单独申请的权限

| 权限 | 审批链 | SLA | 说明 |
|------|--------|-----|------|
| 其他团队 / 其他客户项目的 GitLab 仓库 | 直属上级 → 仓库 Owner | 1 个工作日 | 每个客户一个 Group，只申请所参与的客户 |
| NAP 生产环境（某客户租户）配置权限 | 直属上级 → FDE 组长 → 雷鸣 | 1 个工作日 | 按客户租户授权；**需已通过客户数据安全考试** |
| 生产发布权限（Launchpad） | 直属上级 → 部门负责人 → 雷鸣 | 2 个工作日 | **转正后**才可申请；试用期内由导师代为发布 |
| 客户真实数据（脱敏后）用于构建评测集 | 项目 FDE 负责人 → 许蔓 → 白冰 | 2 个工作日 | 必须在客户 DPA 授权范围内 |
| **聚石塔 / 京东云鼎 / 抖音电商云 / 多多云** 环境 | 直属上级 → 雷鸣 → 白冰 | 2 个工作日 | 平台订单数据只能在这些环境内处理，操作全程审计 |
| 电商平台开放 API 应用凭证（AppKey / Secret） | 项目 FDE 负责人 → 马骁 → 白冰 | 2 个工作日 | 凭证存放在 KMS，**禁止明文出现在代码、Prompt 或聊天中** |
| 生产数据库只读查询（DMS） | 直属上级 → DBA 唐毅 → 白冰 | 2 个工作日 | 默认脱敏 |
| 堡垒机（生产服务器登录） | 直属上级 → 雷鸣 → 白冰 | 2 个工作日 | 临时权限最长 7 天 |
| 阿里云控制台（RAM 子账号） | 直属上级 → 雷鸣 → 白冰 | 2 个工作日 | 默认只读 |
| 外部模型供应商控制台 | 直属上级 → 云欢 → 白冰 | 3 个工作日 | 一般不开通，统一走模型网关 |

> SLA 指审批人处理时间。超过 SLA 未处理，可在 Launchpad 点击“催办”，或在钉钉群“SRE 服务台”找当周值班 SRE。

## 本地开发环境

1. 安装 Homebrew，然后运行一键脚本：`curl -fsSL https://gitlab.realniubility.example/devtools/bootstrap/raw/main/setup.sh | bash`（需开启 NiuGate）。脚本会安装 Python 3.12、uv、Node 20、Docker Desktop、kubectl，以及公司 CLI 工具 `rn`。
2. 运行 `rn dev init` 配置私有 PyPI / npm 源，并登录 NAP 测试环境。
3. 运行 `rn agent new --template cs-basic` 生成一个客服 Agent 模板工程，`rn eval run` 在本地跑评测。
4. 配置 GitLab SSH Key：`ssh-keygen -t ed25519 -C "你的邮箱"`，公钥添加到 GitLab，**私钥禁止上传到任何地方**。
5. Git 提交身份必须使用公司邮箱：`git config --global user.email "名.姓@realniubility.example"`。

## 权限回收

- 离开客户项目：项目 FDE 负责人在 Launchpad 提交“项目成员变更”，该客户的 GitLab、租户、平台云环境权限当天回收。
- 客户合同终止：所有客户相关权限与凭证由 SRE 和信息安全组统一回收，客户数据按 DPA 约定删除并出具删除证明。
- 生产相关权限每季度复核，连续 90 天未使用自动回收。
