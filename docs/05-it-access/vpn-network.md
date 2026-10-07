# 网络与 VPN（SailGate）

> 文档负责人：IT 支持部 江涛 & 信息安全部 白冰｜最近更新：2026-08-15

## 办公网络

| Wi-Fi 名称 | 用途 | 认证方式 |
|-----------|------|----------|
| NebulaSail-Office | 员工办公 | SailID 账号 + 密码（802.1X），仅限公司管理的设备 |
| NebulaSail-Guest | 访客、个人手机 | 前台或钉钉“访客登记”获取当天密码，**不能访问内网** |
| NebulaSail-Lab | 测试设备、IoT 调试 | 由孙蕾团队按设备 MAC 地址授权 |

## SailGate 零信任 VPN

公司所有内网系统（GitLab、Jira、Confluence、测试环境、监控、帆舟等）都需要通过 **SailGate** 访问，**在公司 Wi-Fi 下也需要开启**。

- **安装**：公司电脑已预装；如需重装，从 IT 自助门户 https://it.nebulasail.example 下载。
- **登录**：使用 SailID + MFA，登录有效期 12 小时。
- **设备合规检查**：SailGate 会检查系统版本、磁盘加密、EDR 状态，不合规的设备会被拒绝连接，并提示修复步骤。
- **手机端**：可在手机上安装 SailGate App 访问 Confluence 和钉钉内的内网页面；手机端**不能**访问 GitLab 和生产系统。

## 生产网络

- 生产环境（阿里云 VPC）**不能**通过 SailGate 直接访问，必须通过**堡垒机（JumpServer）**登录，所有操作全程录屏审计。
- 堡垒机权限申请见[研发系统权限开通](dev-access.md)。

## 常见问题

| 问题 | 解决方法 |
|------|----------|
| SailGate 提示“设备不合规” | 按提示更新系统、开启 FileVault；仍不行找 IT 服务台 |
| 连上 VPN 但打不开 GitLab | 检查是否已申请 GitLab 权限；执行 `nslookup gitlab.nebulasail.example` 确认解析到 10.x 地址 |
| 出差在酒店连不上 | 部分酒店网络屏蔽 UDP，切换 SailGate 设置中的“TCP 模式” |
| 海外出差 | 提前 3 天在钉钉提交“境外访问申请”，信息安全部审批后开通境外接入点 |

IT 服务台 7×24 小时紧急电话：**0571-8888-8000**（仅限 VPN 完全无法使用且影响生产处理的紧急情况）。
