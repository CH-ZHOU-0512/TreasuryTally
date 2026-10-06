---
doc-id: project-status
title: 当前项目状态
status: active
authority-for:
  - current-status
  - active-work
  - known-blockers
last-reviewed: 2026-10-07
---

# 当前项目状态

更新时间：2026-10-07

## 当前阶段

M1 已完成：领域契约、Pydantic 模型、8 份 JSON Schema、契约测试和 12 份人工标注 fixtures
均已集成到 `codex/m1-integration`。M2 PR #1 已合并，远端合并提交为
`d9ac1108e9a21fe0073587d4f458848ed1ac8ecd`。M3 无 UI 纵向闭环及本地回执重放已在本地实现并验证。
M4 受限 AI 编排、供应商 adapter、离线对抗测试及一次真实 DeepSeek 结构化调用已完成，满足启动 M5 的前置条件。

## 已完成

- Python 3.12 主环境 `.venv` 已创建，`pip check` 通过。
- Agent0 SDK、LangChain、Streamlit、Web3.py、Pydantic、SQLAlchemy、Pytest、Ruff 已安装。
- Blockscout MCP 已在 `.venv-blockscout` 独立安装，CLI 和 `pip check` 通过。
- Streamlit 基础启动健康检查已通过。
- `agent0-py`、`erc-8004-contracts`、Blockscout `mcp-server` 已下载到 `references/`。
- ERC-8004 参考合约编译成功，79 项上游测试通过。
- 根目录、环境变量模板、依赖清单和锁定快照已建立。
- 开发前产品、架构、数据、测试、安全、运维和协作文档已建立。
- M0 外部集成规格、分阶段依赖门槛和代码文件规模约束已建立。
- Git 仓库已连接到 `https://github.com/CH-ZHOU-0512/xinjv`，默认分支为 `main`。
- 已创建 `pyproject.toml`、`src/trust_receipt/` 包和 `tests/external/`，包含 RPC、Blockscout MCP、
  Agent0 与 ERC-8004 的最小探针。
- 外部调用统一设置超时；只读操作最多重试两次；ERC-8004 写探针默认关闭且不自动重发未知交易。
- RPC 已在 Sepolia 读取固定历史区块和真实 WETH Transfer，保留整数金额及完整事件键。
- Blockscout MCP 已完成 initialize、16 项工具发现及同一笔 Sepolia 交易查询；客户端与服务端统一使用 MCP 1.26.0。
- 已创建团队控制的 Agent0 身份 `11155111:10691`，Agent0 SDK 1.7.1 可重复读取名称、owner 和 active 状态。
- 三个 ERC-8004 Registry 的链上 bytecode 与相互关联已核验；中性反馈交易已确认并从链上读回一致内容。
- 已建立 `codex/m1-integration` 与 `codex/m1-core-models` 分支，并从远端 `main` 合并提交
  `b44945b48bef8b77b9fe4633fd714de75a66d636` 开始 M1。
- 已冻结 `trust_receipt.models` 公共边界，覆盖任务、转账、服务交付、白名单计划、三态验证结果、回执及
  M1 fixture/manifest 模型。
- 核心金额在领域边界使用无符号十进制整数字符串；事件键保留 `chain_id + transaction_hash + log_index`；
  参考不完整或证据不足强制为 `INCONCLUSIVE`。
- fixture 布局固定为 `fixtures/m1/manifest.json` 与 `fixtures/m1/cases/`；8 个顶层 Schema 文件固定输出到
  `schemas/v1/`，导出脚本路径固定为 `scripts/export_schemas.py`。
- A 的 12 份 fixtures 与 B 的 8 份 Schema、导出脚本和契约测试已通过 PR 集成；3 处参考记录与来源描述符
  不一致已修正，来源标签现在可交叉核验。

## M2/M3 验证进展

- 已实现任务范围过滤、完整事件键去重、整数汇总、分页连续性校验和可定位 Finding。
- 首条纵向切片得到 `110000`、`FAIL` 和两项 Finding。
- 对抗性测试复现并修复了完整来源事件集合不一致、同一区块哈希冲突两类误判 PASS；两者现在返回 INCONCLUSIVE。
- 严格联调入口 `python -m pytest tests/verification/test_m1_fixtures.py --m1-fixtures fixtures/m1`
  已实际运行，12 份 fixtures 的金额、数量、三态结果、Finding、规则和事件键全部匹配。
- 全量测试 97 项通过、5 项因外部配置缺失而跳过；fixture Schema 校验、Ruff 与 pip check 均通过。
- 已实现拒绝 `float` 的 canonical JSON、SHA-256 稳定哈希及 TaskSpec、ServiceSubmission、Receipt 校验函数。
- 已实现团队控制服务 A/B 端口、EVM 签名恢复校验和独立故障注入元数据，模拟故障不混入参考来源。
- 已实现 SQLite task/attempt/verification 分表留档与状态机；attempt 只追加，最多一次补交，签名失败不消耗 attempt。
- 无 UI 编排已跑通首次遗漏导致 `FAIL`、同服务补交或切换服务后 `PASS`，两个 attempt 均可分别读取。
- 已实现 ReceiptBuilder、本地只创建不覆盖的 JSON 存储和独立进程重放；FAIL/PASS attempt 分别生成不同哈希，
  重放会校验回执哈希、任务哈希、对象链接并重新推导三态结果。
- 已增加最小 GitHub Actions 配置：普通 CI 执行非 external pytest、Ruff、pip check；外部探针不伪装成功。
- 当前全量本地测试为 107 项通过、5 项因外部配置缺失而明确跳过；Ruff 与 pip check 通过。

## M4 AI 编排进展

- 已实现 `TaskSpecCandidate`、`ClaimExtraction`、`FollowUpAdvice` 和 `ResultExplanation` 严格 Pydantic 契约，
  并新增 4 份可重复生成的 JSON Schema；缺失字段、歧义、重复主张类型和非规范金额在候选边界拒绝。
- 已实现无工具 `StructuredOutputPort`、`RestrictedAIService`、LangChain OpenAI adapter 与 DeepSeek
  OpenAI-compatible Responses adapter；核心 models、verification、storage 和 receipts 不依赖供应商 SDK。
- 任务 ID、确认时间和 `spec_hash` 只由确定性代码生成；VerificationPlan 必须完整命中白名单并逐项绑定已确认任务。
- 补查建议仅允许封闭动作枚举；结果解释必须保持确定性 outcome、金额、数量、Finding ID 和证据引用。
- 离线测试覆盖 prompt injection、未知操作、参数漂移、缺失检查、歧义任务、冲突主张以及金额/结论篡改。
- `deepseek-flash` 真实 external 探针已返回并通过 schema 校验；一次性凭据已从本机删除，后续运行需新凭据。
- OpenAI external 探针因缺少 `OPENAI_API_KEY` 和固定 `OPENAI_MODEL` 明确阻塞，没有用 mock 冒充实测。
- 删除临时凭据后的全量质量门为 128 项通过、7 项 external 因当前配置缺失而明确跳过；DeepSeek 探针另有此前
  单独执行的 1 项真实通过记录。Ruff、pip check、12 份 Schema 重生成检查和 1000 行限制均通过。

## 待集成或尚未开始

- 确定性验收引擎与真实读取 adapter 的产品流程联调。
- Streamlit 产品页面。
- 公共回执发布与 ERC-8004 接入。

## 后续阶段外部配置待办

- 提供 `OPENAI_API_KEY`。
- 提供固定 `OPENAI_MODEL`；若继续使用 DeepSeek，重新生成并仅在本机配置 `DEEPSEEK_API_KEY` 与固定
  `DEEPSEEK_MODEL`。
- 如使用 Pinata，提供 `PINATA_JWT`。

## 已知问题

- Docker Desktop 4.79.0 当前无法启动，自动升级在管理员阶段失败。Blockscout MCP 本地 Python 运行方案已绕过该问题，Docker 不阻塞 MVP。
- ERC-8004 上游参考仓库存在 npm peer dependency 冲突，安装需 `--legacy-peer-deps`。
- 上游 npm 审计报告 35 个依赖漏洞；该仓库当前仅作参考和合约测试，没有执行自动修复。
- GitHub Actions 仅覆盖无需密钥的本地质量门；真实 external 探针仍需显式配置后单独执行。

## 下一步

启动 M5：实现 Streamlit 条件确认、执行进度、差异、补交/换源与回执预览，并接通现有确定性流程和 M4 受限 AI
用例；继续保持领域、验证、存储和供应商 adapter 解耦。

## 状态更新规则

- 这里只记录当前事实、下一步和实际阻塞。
- 完成某阶段时更新本文件，不在多个设计文档重复维护进度。
- 每项“已完成”必须能对应文件、命令输出、测试记录或外部交易。
