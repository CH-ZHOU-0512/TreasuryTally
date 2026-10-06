---
doc-id: project-readme
title: 信据 Agent 项目入口
status: active
authority-for:
  - documentation-routing
  - repository-entrypoint
last-reviewed: 2026-10-06
---

# 信据 Agent

信据 Agent 用于验收外部服务交付的链上拨款报表。系统将已确认的委托条件固定成机器可读任务，读取独立链上证据，对报表执行确定性核对，并生成能够说明“哪里不符合约定、如何复现”的验收回执。

首版是约 40 小时开发窗口内的可运行原型，不是完整交易市场或通用会计系统。

## 文档导航

| 需要了解 | 权威文档 |
|---|---|
| 产品目标、范围、非目标和验收标准 | [PRODUCT.md](PRODUCT.md) |
| 系统组成、边界和数据流 | [ARCHITECTURE.md](ARCHITECTURE.md) |
| 核心对象、字段与计算不变量 | [DATA_CONTRACTS.md](DATA_CONTRACTS.md) |
| 开发顺序、里程碑和降级策略 | [DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md) |
| 测试矩阵与质量门槛 | [TEST_PLAN.md](TEST_PLAN.md) |
| 密钥、隐私和威胁边界 | [SECURITY.md](SECURITY.md) |
| 安装、启动、故障恢复 | [OPERATIONS.md](OPERATIONS.md) |
| 已作出的架构与产品决定 | [DECISIONS.md](DECISIONS.md) |
| 当前真实进展和待办 | [STATUS.md](STATUS.md) |
| 文档权威、生命周期和更新规则 | [DOCS_GOVERNANCE.md](DOCS_GOVERNANCE.md) |
| 人工和 AI 开发协作规则 | [CONTRIBUTING.md](CONTRIBUTING.md)、[AGENTS.md](AGENTS.md) |
| 原始立项背景 | [立项.md](立项.md) |

## 快速开始

```powershell
cd D:\HACKTHON
Copy-Item .env.example .env
.\.venv\Scripts\Activate.ps1
```

填写 `.env` 中的必要配置后，后续应用入口预定为：

```powershell
streamlit run app\streamlit_app.py
```

当前业务代码尚未实现，实际进展请查看 [STATUS.md](STATUS.md)。不要把上述预定命令误认为当前已经存在的功能。

## 仓库边界

- `src/`：核心业务代码。
- `app/`：Streamlit 页面入口。
- `tests/`：单元、集成和端到端测试。
- `fixtures/`：人工标注的演示与测试数据。
- `schemas/`：可机器校验的 JSON Schema。
- `receipts/`：生成的公开回执；私密内容放在 `receipts/private/`。
- `data/`：本地数据库和运行数据，不提交版本库。
- `references/`：上游项目的只读参考副本，不属于本项目代码和文档权威体系。

## 核心原则

1. 确定性程序负责金额、集合和范围判断，AI 不拥有最终计算权。
2. 证据不足必须返回 `INCONCLUSIVE`，不能伪装成通过或失败。
3. 任务确认后必须固定范围并计算指纹，不能在执行中静默改变。
4. 每次服务交付分别留档，后一次成功不能覆盖前一次失败。
5. 公开前必须脱敏并获得授权；提交交易不等于链上确认。
