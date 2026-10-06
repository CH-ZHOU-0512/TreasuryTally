---
doc-id: system-architecture
title: 系统架构
status: active
authority-for:
  - component-boundaries
  - system-data-flow
  - dependency-direction
last-reviewed: 2026-10-06
---

# 系统架构

## 架构目标

让确定性核对独立于模型、页面和单一数据供应商运行。核心验收能力必须能从测试或命令行调用；Streamlit 和 LangChain 都只是适配层。

## 逻辑组件

```text
Streamlit UI
    │
    ├── Task Orchestrator ── AI Claim/Plan Adapter
    │          │
    │          ├── Report Service A/B Adapter
    │          └── Verification Engine
    │                    ├── RPC Evidence Adapter
    │                    ├── Blockscout MCP Adapter
    │                    └── Deterministic Rules
    │
    ├── Receipt Builder ── File Publisher/IPFS Adapter
    │
    └── Reputation Adapter ── Agent0 / ERC-8004

SQLite Repository stores tasks, attempts, findings and publication state.
```

## 推荐包结构

```text
src/trust_receipt/
├─ models/          # 领域对象和枚举
├─ services/        # 报表服务接口及演示实现
├─ chain/           # RPC、Blockscout、事件标准化
├─ verification/    # 过滤、去重、集合比较、汇总、规则
├─ agents/          # LangChain 提取和计划适配器
├─ receipts/        # 回执构建、哈希、重放
├─ reputation/      # Agent0/ERC-8004 适配器
├─ storage/         # SQLite repository
└─ orchestration/   # 用例编排，不包含 UI 逻辑
```

## 依赖方向

- `models` 不依赖 UI、数据库、LangChain 或 Web3 客户端。
- `verification` 只依赖领域模型和纯计算工具。
- `chain`、`services`、`reputation`、`storage` 实现端口，不反向控制领域规则。
- `agents` 只能产生经过校验的结构化候选，不直接写数据库或发布反馈。
- `orchestration` 组合各端口，`app` 只调用用例并展示状态。

## 模块与文件约束

- 模块按领域能力组织，一个模块只拥有一个主要变化原因。
- 核心领域模型和确定性规则不得依赖 Streamlit、LangChain、数据库实现或具体供应商 SDK。
- RPC、Blockscout、Agent0、ERC-8004、存储和模型调用分别通过端口与 adapter 隔离。
- 跨模块只传递已定义的领域模型或协议，不共享供应商原始响应、隐式全局状态或可变单例。
- 除 Markdown 和 `.tmp/` 下不提交的临时测试文件外，单个代码、脚本、配置或永久测试文件不得超过 1000 个物理行。
- 文件接近 1000 行时，按模型、协议、实现、错误映射或用例职责拆分；禁止缩短变量名、合并语句或压缩格式来规避限制。
- 拆分后依赖方向仍须由外层指向领域层，禁止循环依赖。

## 主数据流

1. 自然语言需求进入 AI 提取器，得到候选 `TaskSpec`。
2. 用户修改并确认后，系统规范化 JSON 并计算 `spec_hash`。
3. 报表服务返回 `ServiceSubmission`，原文、明细、版本和签名分别保存。
4. 参考适配器按固定范围读取链上事件，并报告分页完整性和来源。
5. 验收引擎标准化两侧事件，应用相同规则并进行集合和金额比较。
6. 结果变为 `VerificationRun` 和 `Finding[]`。
7. 回执构建器绑定任务、交付、计划、验证器版本和证据哈希。
8. 用户授权后，发布适配器上传脱敏回执；信誉适配器提交其 URI 和哈希。
9. 读回程序校验链上引用、文件哈希及确定性检查结果。

## 信任边界

- 服务提交是待验证声明，不能成为参考真值。
- Blockscout 是数据工具，不等同于被评价服务；其失败不能归咎于演示服务。
- RPC 返回是参考证据，但也可能超时、限流或发生重组。
- 模型输出是不可信结构化输入，必须校验字段、枚举和允许操作。
- SQLite 和本地文件是原型持久化，不是抗篡改存储。
- 链上哈希证明关联和完整性，不证明回执内容真实。

## 状态机

```text
DRAFT → CONFIRMED → REQUESTED → SUBMITTED → VERIFYING
                                      │
                 ┌────────────────────┼────────────────────┐
                 ▼                    ▼                    ▼
               PASS                 FAIL             INCONCLUSIVE
                                      │
                              RETRY_REQUESTED
                                      │
                              SUBMITTED(attempt=2)

terminal result → RECEIPT_CREATED → PUBLISHING → PUBLISHED → ONCHAIN_CONFIRMED
```

失败重试不得覆盖旧 attempt；发布失败也不得改变验收结论。

## 外部依赖

- Python 3.12 主环境：应用、测试和 Streamlit。
- 独立 Python 环境：Blockscout MCP Server，避免 MCP 版本约束污染主环境。
- EVM JSON-RPC：参考事件读取。
- Blockscout MCP：补充地址、交易和代币信息。
- OpenAI 兼容工具调用模型：主张和计划组织。
- Agent0/ERC-8004：服务身份和公开反馈关联。
- 公共文件存储/IPFS：完整回执链下保存。

当前连通性和实现状态不在本文维护，请查看 [STATUS.md](STATUS.md)。
