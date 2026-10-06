---
doc-id: architecture-decisions
title: 架构与产品决定
status: active
authority-for:
  - accepted-decisions
  - decision-rationale
last-reviewed: 2026-10-06
---

# 架构与产品决定

本文记录会影响多个模块、数据契约、安全边界或交付范围的已接受决定。状态变更必须保留原记录并追加替代决定。

## ADR-001：采用严格限定的单链 MVP

- 状态：Accepted
- 日期：2026-10-06

决定：首版只支持一条 EVM 测试链、一种 ERC-20、最多两个资金账户、固定区块范围和最多 200 条相关事件。

理由：40 小时原型需要优先验证“任务约束下的交付验收”是否成立，而不是验证跨链基础设施。

后果：超出范围必须分段或明确拒绝，不能抽样后声称全量通过。

## ADR-002：确定性程序拥有最终计算权

- 状态：Accepted
- 日期：2026-10-06

决定：AI 只负责提取主张、生成受限计划、提出补查和解释结果；事件集合、过滤、去重、金额和最终状态由版本化程序计算。

理由：模型输出不稳定，不适合作为财务金额和可复现回执的权威来源。

后果：模型措辞可以变化，确定性输入对应的金额和 Finding 必须一致。

## ADR-003：采用 PASS / FAIL / INCONCLUSIVE 三态结果

- 状态：Accepted
- 日期：2026-10-06

决定：数据不足、分页未知或参考节点失败时返回 `INCONCLUSIVE`。

理由：无法验证不等于服务失败，二态结果会制造不可靠的负面信誉。

后果：只有证据充分的 `FAIL` 才能形成负面反馈候选。

## ADR-004：事件身份使用 chain、交易哈希和日志索引

- 状态：Accepted
- 日期：2026-10-06

决定：ERC-20 转账的最小身份键是 `(chain_id, transaction_hash, log_index)`。

理由：同一交易可以发出多个 `Transfer` 事件，只用交易哈希会错误去重。

## ADR-005：完整回执链下保存，链上保存关联与完整性

- 状态：Accepted
- 日期：2026-10-06

决定：版本化 JSON 回执保存在链下公共存储，ERC-8004 关联服务、结果、URI 和内容哈希。

理由：完整证据体积大且可能需要脱敏；链上适合提供稳定关联和完整性检查，不自动证明内容真实。

## ADR-006：Blockscout MCP 使用隔离 Python 环境

- 状态：Accepted
- 日期：2026-10-06

决定：Blockscout MCP 固定运行在 `.venv-blockscout`，主应用运行在 `.venv`。

理由：Blockscout MCP 对 `mcp` 版本有独立约束，和主应用 LangChain MCP 依赖混装可能产生冲突。

后果：本地运行需要两个进程，但 Docker Desktop 故障不再阻塞开发。

## ADR-007：原型使用预配置服务，不建设开放市场

- 状态：Accepted
- 日期：2026-10-06

决定：团队控制服务 A/B，并明确标注故障注入。Agent0 用于身份和反馈接入，不在首版实现开放服务交易市场。

理由：评价逻辑必须先在可控数据中验证，且不能把人为错误归因于真实第三方项目。

## 新增决定模板

```markdown
## ADR-NNN：标题

- 状态：Proposed | Accepted | Superseded
- 日期：YYYY-MM-DD
- 替代：ADR-NNN（如适用）

决定：

理由：

后果：
```
