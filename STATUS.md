---
doc-id: project-status
title: 当前项目状态
status: active
authority-for:
  - current-status
  - active-work
  - known-blockers
last-reviewed: 2026-10-06
---

# 当前项目状态

更新时间：2026-10-06

## 当前阶段

M1 主负责人阶段已完成：领域契约、Pydantic 核心模型、fixture 布局和 Schema 命名已冻结并通过本地验证。
AI 同事 A、B 已按用户确认开始并行工作，交付尚未集成到本分支。
独立分支 `codex/m2-verification` 已实现纯函数验收核心，草稿 PR #1 等待 M1 样例联调。

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

## M2 分支验证进展

- 已实现任务范围过滤、完整事件键去重、整数汇总、分页连续性校验和可定位 Finding。
- 首条纵向切片得到 `110000`、`FAIL` 和两项 Finding。
- 对抗性测试复现并修复了完整来源事件集合不一致、同一区块哈希冲突两类误判 PASS；两者现在返回 INCONCLUSIVE。
- 本分支全量测试 59 项通过，6 项明确跳过（5 项外部配置缺失，1 项 M1 样例尚未集成）；Ruff 与 pip check 通过。
- 已提供严格联调入口：`python -m pytest tests/verification/test_m1_fixtures.py --m1-fixtures fixtures/m1`。
  显式指定目录却缺少 manifest 时会失败，已实际验证；尚未声称 12 份样例通过。Schema 校验仍由 B 的契约测试负责。

## 待集成或尚未开始

- JSON Schema 与契约测试。
- 12 份人工标注 fixtures。
- 确定性验收引擎与 12 份样例、真实读取 adapter 的联调。
- 报表服务 A/B。
- LangChain 编排。
- Streamlit 产品页面。
- SQLite repository。
- 公共回执发布与 ERC-8004 接入。

## 后续阶段外部配置待办

- 提供 `OPENAI_API_KEY`。
- 如使用 Pinata，提供 `PINATA_JWT`。

## 已知问题

- Docker Desktop 4.79.0 当前无法启动，自动升级在管理员阶段失败。Blockscout MCP 本地 Python 运行方案已绕过该问题，Docker 不阻塞 MVP。
- ERC-8004 上游参考仓库存在 npm peer dependency 冲突，安装需 `--legacy-peer-deps`。
- 上游 npm 审计报告 35 个依赖漏洞；该仓库当前仅作参考和合约测试，没有执行自动修复。
- 当前尚未配置文档或测试 CI；进入业务开发后再按实际命令建立检查流程。

## 下一步

按 [M1_HANDOFF.md](M1_HANDOFF.md) 审查并集成 A/B 的交付，随后运行严格的 M1/M2 样例联调入口，
确认所有差异后再推进草稿 PR #1。M1/M2 尚未整体验收完成。

## 状态更新规则

- 这里只记录当前事实、下一步和实际阻塞。
- 完成某阶段时更新本文件，不在多个设计文档重复维护进度。
- 每项“已完成”必须能对应文件、命令输出、测试记录或外部交易。
