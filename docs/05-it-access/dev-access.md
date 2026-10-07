# 研发系统权限开通

> 文档负责人：SRE 组长 雷鸣 & 质量与效能部 孙蕾｜最近更新：2026-09-12｜所有研发权限通过 **帆舟 → 权限中心** 申请（登录 https://sailboat.nebulasail.example）

## 新人研发权限包

研发新人入职当天，直属上级会在帆舟为你申请“**研发新人权限包**”，包含以下权限，一般在**入职第 1–2 个工作日内**开通：

| 系统 | 默认权限 | 地址 |
|------|----------|------|
| GitLab | 所在团队 Group 的 Developer 权限 | https://gitlab.nebulasail.example |
| Jira / Confluence | 所在团队项目读写 | jira / wiki.nebulasail.example |
| 测试环境（dev / test） | K8s 命名空间只读 + 日志查看 | 通过帆舟访问 |
| 制品库（Nexus / Harbor） | 拉取 | nexus / harbor.nebulasail.example |
| Sentry、Grafana | 所在团队项目只读 | sentry / grafana.nebulasail.example |
| SonarQube | 查看 | sonar.nebulasail.example |

## 需要单独申请的权限

| 权限 | 审批链 | SLA | 说明 |
|------|--------|-----|------|
| 其他团队 GitLab 仓库 | 直属上级 → 仓库 Owner | 1 个工作日 | 只申请需要的仓库，不要申请整个 Group |
| GitLab Maintainer 权限 | 直属上级 → 部门负责人 | 1 个工作日 | 仅限模块 Owner |
| 预发环境（staging）发布权限 | 直属上级 → 孙蕾 | 1 个工作日 | 需通过“发布流程”考试 |
| **生产环境发布权限（帆舟）** | 直属上级 → 部门负责人 → 雷鸣 | 2 个工作日 | **转正后**才可申请；试用期内由导师代为发布 |
| 生产 K8s 只读 / 日志 | 直属上级 → 雷鸣 | 1 个工作日 | 用于 On-call 排查 |
| 堡垒机（生产服务器登录） | 直属上级 → 部门负责人 → 雷鸣 → 白冰 | 2 个工作日 | 临时权限最长 7 天 |
| 生产数据库只读查询（DMS） | 直属上级 → 数据所有者 → DBA 唐毅 → 白冰 | 2 个工作日 | 默认脱敏；查询明文需 L3 审批 |
| 数据仓库表权限 | 直属上级 → 表 Owner → 许蔓团队 | 1 个工作日 | 涉及 L3 数据需信息安全部加签 |
| 阿里云控制台（RAM 子账号） | 直属上级 → 雷鸣 → 白冰 | 2 个工作日 | 默认只读；写权限需按资源申请 |
| 外部 SaaS（GitHub 组织、npm 组织等） | 直属上级 → 白冰 | 2 个工作日 | 公司 GitHub 组织仅用于开源项目 |

> SLA 指审批人处理时间，从提交到开通。超过 SLA 未处理，可在帆舟点击“催办”，或在钉钉群“SRE 服务台”找当周值班 SRE。

## 本地开发环境

1. 安装 Homebrew，然后运行一键脚本：`curl -fsSL https://gitlab.nebulasail.example/devtools/bootstrap/raw/main/setup.sh | bash`（需开启 SailGate）。脚本会安装 JDK 17、Node 20、Flutter、Docker Desktop（公司已购买商业授权）、kubectl、公司 CLI 工具 `sail`。
2. 配置 GitLab SSH Key：使用 `ssh-keygen -t ed25519 -C "你的邮箱"`，公钥添加到 GitLab，**私钥禁止上传到任何地方**。
3. Git 提交身份必须使用公司邮箱：`git config --global user.email "名.姓@nebulasail.example"`。
4. Maven / npm 私有源配置：运行 `sail dev init`，会自动写入 `~/.m2/settings.xml` 与 `~/.npmrc`。

## 权限回收

- 转岗：原团队 GitLab、生产权限在转岗当天自动回收。
- 生产相关权限每季度复核一次，连续 90 天未使用的权限自动回收。
