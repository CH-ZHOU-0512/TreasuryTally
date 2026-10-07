---
doc-id: security-policy
title: 安全、隐私与密钥规则
status: active
authority-for:
  - secret-handling
  - privacy-boundary
  - security-invariants
last-reviewed: 2026-10-07
---

# 安全、隐私与密钥规则

## 原型安全边界

本项目处理外部报告、链上地址、API 密钥和测试网签名。原型不应持有主网资金控制权，不提供托管、支付或自动转账能力。

## 密钥规则

- 只使用 `.env` 或运行环境注入密钥；`.env` 已被 `.gitignore` 排除。
- `OPENAI_API_KEY` 与 `DEEPSEEK_API_KEY` 必须分别配合固定的 `OPENAI_MODEL`、`DEEPSEEK_MODEL`；不得把供应商密钥
  放入 prompt、fixture、回执或测试快照。
- `.env.example` 只能包含变量名和无敏感示例。
- `SERVICE_A_PRIVATE_KEY`、`SERVICE_B_PRIVATE_KEY`、`REVIEWER_PRIVATE_KEY` 必须是测试网专用钱包。
- 团队控制报表服务使用测试钱包对 canonical `report_hash` 签名；repository 接收前必须恢复并比对预配置签名者地址。
  自动化测试只在运行时生成临时无资产账户，不得把测试或真实私钥提交到仓库。
- ERC-8004 写探针还必须显式设置 `M0_ENABLE_WRITES=true`；默认值为 `false`，未知提交状态禁止自动重发。
- M6 产品写入另由 `M6_ENABLE_WRITES=true` 显式开启；页面还必须分别取得公开文件与 ERC-8004 写入授权。匿名访问不赋予写权限。
- `AGENT0_SERVICE_ID` 必须配合公开的 `AGENT0_EXPECTED_OWNER` 校验，避免向非团队控制身份写入测试反馈。
- 禁止使用持有主网资产的钱包、个人常用钱包或复用助记词。
- 不在日志、异常、截图、回执、测试 fixture 或模型 prompt 中输出密钥。
- 如果密钥出现在提交或日志中，按已泄露处理并立即轮换。对话中出现的测试供应商密钥默认也应轮换；但项目所有者
  明确授权继续使用时，只能写入被 Git 忽略的本机 `.env`，不得复制到受版本控制文件、日志、fixture、回执或模型 prompt。

## 数据分类

| 数据 | 分类 | 处理方式 |
|---|---|---|
| 公共链上事件 | public | 可引用并保留来源 |
| 脱敏验收回执 | public-after-approval | 用户授权后发布 |
| 原始服务报告 | restricted | 默认本地保存，公开前审查 |
| 组织标签和排除规则 | restricted | 仅发布必要部分 |
| API 密钥、私钥、JWT | secret | 只存在安全运行环境 |
| 模型输入输出 | internal | 不默认作为公开证据 |

## 主要威胁与控制

### 恶意或错误报告

控制：所有服务交付视为不可信；解析有大小和记录数上限；确定性规则对照独立来源。

### Prompt injection

控制：报告文本不能扩展工具权限；模型只返回受限 schema；模型端口不持有任意 Shell、文件、SQL、repository、发布、
Python 或写链工具。未知操作、额外字段、任务参数漂移以及结果金额/状态漂移在确定性边界拒绝。

### 伪造或重复事件

控制：检查 chain、token、区块、交易哈希、log index；按事件身份键去重；必要时保存 block hash。

### 数据源不完整

控制：分页完整性显式建模；超时、限流、重组或来源冲突返回 `INCONCLUSIVE`。

### 回执泄露隐私

控制：公开版和私有证据分离；公开前展示待发布内容并取得授权；使用内容哈希关联，不默认发布原始报告。

### 错误链上信誉

控制：只有证据充分的 `FAIL` 可以进入负面反馈候选；写链前显示服务、任务范围、回执哈希和网络；确认后才显示成功。

### M8–M10 承诺与公开验证

- 任务承诺只包含任务哈希、公开身份、时间和必要公共引用；受限组织标签、原始报告、模型输入和凭据不得进入签名明文或链上事件。
- EIP-712 domain 必须绑定 chain ID、验证合约或明确的应用域和版本，防止跨链、跨环境与跨用途重放。
- 服务接单和交付签名必须分别校验 task hash、report hash、attempt、service ID 与签名者授权关系。
- 匿名演示入口只能发起只读验收和准备待授权对象；不得调用服务器 Reviewer 钱包替匿名用户自动确认任务、发布或写链。
- 公开验证页只读取公开回执和公共链上数据，不得通过 task hash 枚举私有报告、SQLite 工作区或未授权返工内容。
- M10 历史投影只显示可追溯事实，不输出永久黑名单；`INCONCLUSIVE` 不计入负面信誉。

## 日志要求

- 允许记录任务 ID、步骤、耗时、状态码和脱敏错误。
- 地址默认可显示缩略形式；需要完整地址时明确标记其为链上公共数据。
- 禁止记录请求头、环境变量全集、私钥、JWT 和完整模型认证信息。
- 外部响应正文仅在必要时保存，并采用大小限制和访问边界。
- `APP_REQUIRE_LIVE` 只控制生产能力开关，不包含凭据；DeepSeek、RPC 与 Blockscout 凭据仍只通过受限 `.env` 注入，禁止进入
  镜像、仓库、页面或日志。
- `PINATA_JWT` 与 `REVIEWER_PRIVATE_KEY` 只能由 `.env` 注入 publisher/reputation adapter；公共回执扫描禁止
  `private_key`、`signature`、`jwt`、`authorization`、`api_key`、`secret` 和原始 `report_text` 字段。
- HTTPS fallback 公共目录只允许应用容器写、Nginx 容器只读，文件名必须内容寻址且只创建不覆盖；公网路径仅允许 GET/HEAD、
  禁止目录列表，并不得与 `receipts/private/` 共用目录或挂载权限。
- Streamlit 需要内联启动脚本和运行时样式；生产反向代理仅在公开的 `/trust-receipt/` 路径放开
  `script-src/style-src 'unsafe-inline'`，其余站点继续使用更严格的全局 CSP，并保留 HSTS、同源 frame、MIME 嗅探防护和权限策略。

## 依赖与供应链

- 主应用使用 `requirements.txt` 声明范围，`requirements.lock.txt` 保存当前解析结果。
- Blockscout MCP 运行在 `.venv-blockscout` 隔离环境。
- `references/` 是上游参考副本，不在其中运行自动依赖修复。
- 依赖升级必须运行单元测试、契约测试和 `pip check`。
- ERC-8004 参考仓库当前上游 npm 审计报告包含漏洞；在其仅作为测试参考时不得误报为主应用运行依赖。

## 漏洞处理

发现潜在漏洞时，先保存最小复现、受影响边界和证据，不在公开问题中提交真实密钥或未脱敏数据。原型未配置正式披露邮箱，问题先由项目维护者在私有渠道处理。
