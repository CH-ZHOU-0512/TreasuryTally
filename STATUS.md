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

开发前准备。环境与上游参考已就绪，文档治理已建立，业务代码尚未开始。

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

## 尚未开始

- `src/trust_receipt/` Python 包。
- Pydantic 领域模型和 JSON Schema。
- 12 份人工标注 fixtures。
- 确定性验收引擎。
- 报表服务 A/B。
- LangChain 编排。
- Streamlit 产品页面。
- SQLite repository。
- 公共回执发布与 ERC-8004 接入。

## 外部配置待办

- 提供 `OPENAI_API_KEY`。
- 提供 `BLOCKSCOUT_PRO_API_KEY`。
- 提供可用的 `ETH_RPC_URL`。
- 核实 Sepolia 上的 Agent0/ERC-8004 Registry 合约地址和 ABI 来源。
- 确认测试 ERC-20、已知 Transfer 交易与小区块范围。
- 创建三个只用于测试网的钱包并准备少量测试币。
- 确认用于演示的 ERC-20 代币及历史/自造交易数据。
- 如使用 Pinata，提供 `PINATA_JWT`。

## 已知问题

- Docker Desktop 4.79.0 当前无法启动，自动升级在管理员阶段失败。Blockscout MCP 本地 Python 运行方案已绕过该问题，Docker 不阻塞 MVP。
- ERC-8004 上游参考仓库存在 npm peer dependency 冲突，安装需 `--legacy-peer-deps`。
- 上游 npm 审计报告 35 个依赖漏洞；该仓库当前仅作参考和合约测试，没有执行自动修复。
- 当前尚未配置文档或测试 CI；进入业务开发后再按实际命令建立检查流程。

## 下一步

先执行 [DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md) 的 M0 外部连通性验证；详细检查项见 [INTEGRATIONS.md](INTEGRATIONS.md)。M0 受外部配置阻塞时，可并行进入 M1 和第一条 fixture 驱动的确定性纵向切片，但不得把 mock 结果记为 M0 完成。

## 状态更新规则

- 这里只记录当前事实、下一步和实际阻塞。
- 完成某阶段时更新本文件，不在多个设计文档重复维护进度。
- 每项“已完成”必须能对应文件、命令输出、测试记录或外部交易。
