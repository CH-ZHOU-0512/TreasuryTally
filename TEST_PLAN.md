---
doc-id: test-plan
title: 测试与验收计划
status: active
authority-for:
  - test-matrix
  - quality-gates
  - acceptance-evidence
last-reviewed: 2026-10-07
---

# 测试与验收计划

## 测试目标

证明系统能在限定范围内完整、精确、可重复地核对报表，并能把供应商错误、基础设施故障和证据不足区分开。

## 测试层级

### 单元测试

- 地址和哈希规范化。
- 区块范围边界。
- 内部互转排除。
- `tx_hash + log_index` 去重。
- 最小单位整数加减与展示格式。
- 交付集合和参考集合差集。
- 三态结果判定。
- canonical JSON 与稳定哈希。
- attempt 不可覆盖。

### 契约测试

- RPC `eth_getLogs` 请求、返回和错误映射。
- Blockscout MCP 工具参数和分页终止条件。
- Agent0 身份读取和服务标识。
- ERC-8004 提交、receipt 和读回字段。
- IPFS/文件发布后的内容哈希一致性。

外部契约测试默认可跳过，但必须有明确 marker 和跳过原因，不能悄悄通过。

外部测试执行规则：

- 统一使用 `external` marker，文件放在 `tests/external/`。
- 普通本地测试可以排除 `external`；M0 验收命令必须执行它，缺少配置时明确失败或报告阻塞，不得自动伪装成通过。
- 单次外部请求默认超时 30 秒，单个探针总时限 120 秒；供应商明确要求更长时间时需在集成记录中说明。
- 只读幂等请求最多自动重试两次，并采用退避；交易广播响应不确定时不得自动重发。
- 外部测试输出只保留脱敏摘要、公开地址、交易哈希、区块和错误分类，不打印密钥、认证头或环境变量全集。
- Mock 测试只能验证 adapter 行为，不能作为“外部能力已实测”的证据。
- OpenAI 与 DeepSeek 模型探针分别要求 API key 和固定模型名；缺少任一项时必须以 `external` skip 原因明确报告阻塞。

### 集成测试

- TaskSpec → 服务交付 → 验收 → SQLite 保存。
- 首次 FAIL → 一次补交 → PASS，两个 attempt 都可读取。
- 服务 A FAIL → 切换服务 B → 新交付单独记录。
- 参考节点故障 → `INCONCLUSIVE`，不产生负面反馈。
- 回执创建 → 发布 → 链上提交 → 确认状态。

### 端到端测试

- 正确报告直接通过。
- 120000 报告包含 30000 内部互转并漏掉 20000，正确总额为 110000。
- 全新进程只读取公共回执，校验哈希并复现至少一项确定性检查。
- Streamlit 页面在任务确认前不提供执行入口，首次 FAIL 后可完成唯一一次补交或换源，并同时保留两个 attempt。
- 真实 DeepSeek、Sepolia RPC 与 Blockscout 组合探针必须完成候选生成、A `FAIL`、B `PASS`、两个 `SAMPLED` 补充诊断、
  无 AI 产物校验错误和两个独立回执。
- 同一工作区 ID 在 Streamlit 进程重启后必须恢复已确认任务及两个 attempt，不重新生成历史 AI 文本。
- 桌面宽屏可并排显示编辑与指标；760px 及以下强制单列，长地址、Finding、回执 JSON 和主要按钮不产生不可操作的水平溢出。
- M7 无凭据演示必须完成服务 A `FAIL`、切换服务 B `PASS`、两个 attempt 留档、两份回执独立重放及新进程路径恢复；
  输出必须显式标注 `publication_mode=not-executed`，不得冒充 M6 外部验收。

### M8–M10 计划验收

- M8：上传固定错误报表后，资金流图必须把匹配、漏报、内部互转、重复和证据不足映射到稳定文本/图标状态；每条边能下钻到
  完整事件键和证据引用，图的颜色不能是唯一信息载体。
- M8：任务、接单和交付签名被篡改、签名者不属于服务或链上锚定读回不一致时必须拒绝；提交未知时保持 `SUBMITTED`，
  不得自动重发。
- M9：首次 FAIL 自动形成只包含已确认 Finding 的返工包；第二次 PASS 与首次结果并排存在，父回执和 supersedes 链可重放。
- M9：独立验证入口从 URI、receipt hash、task hash 或 feedback transaction 进入时得到一致对象关系；缺失任何必要证据返回
  `INCONCLUSIVE`，不能显示绿色有效。
- M10：服务历史全部计数可由引用回执重算；任务类型隔离；`INCONCLUSIVE` 不增加失败数；任一指标都能下钻到来源回执。
- 可用性：首次访问只出现一句价值说明、三步主流程和一个主按钮；固定演示不依赖口头解释即可走通
  `FAIL → 返工 → PASS → 发布 → 验证`。

## 人工标注数据集

至少 12 份：

| 类型 | 最少数量 |
|---|---:|
| 完全正确 | 2 |
| 漏项 | 2 |
| 重复事件 | 2 |
| 内部互转误计 | 2 |
| 区块范围错误 | 1 |
| decimals/单位错误 | 1 |
| 多错误组合，开发期间隐藏 | 1 |
| 证据不足 | 1 |

每份 fixture 包含输入、期望结果、期望 Finding 和人工核验说明。故障注入必须与真实供应商数据明确隔离。

## AI 测试

- 对歧义任务必须提出确认，不得自行补全关键地址或区块。
- 输出必须通过 Pydantic 校验。
- 未知工具、过滤器或检查类型必须被拒绝。
- Prompt injection 文本不得取得文件、Shell、数据库或写链权限。
- 同一确定性输入允许解释措辞不同，但验证结果和金额必须一致。
- 任务候选缺失字段列表必须与空字段精确一致；存在缺失或歧义时不得确认任务。
- 计划中的查询、过滤、聚合和检查必须完整命中白名单，参数必须来自已确认任务。
- 补查建议只能使用封闭动作枚举；解释必须覆盖相同 Finding ID 和证据引用。
- OpenAI-compatible/DeepSeek adapter 的离线 mock 只证明协议映射，不计作真实模型调用。

## 质量门槛

- 核心纯函数单元测试全部通过。
- 12 份标注样例的确定性期望全部匹配。
- 对金额、分页和结果状态的测试不得使用宽松断言。
- Ruff 检查通过。
- `pip check` 无破损依赖。
- 涉及外部系统的能力必须报告“已实测”或“未实测”，不能用 mock 结果代替实测声明。
- GitHub Actions 的普通质量门运行 `not external` 测试、Ruff、`pip check`、Schema 重生成检查、1000 物理行限制和
  无凭据 MVP 演示；治理文档 metadata 与链接检查包含在契约测试中。外部探针没有显式密钥时保持跳过，不得以 mock 或
  空配置标记为外部成功。

## 标准命令

```powershell
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m pip check
```

后续引入 marker 后建议：

```powershell
.\.venv\Scripts\python.exe -m pytest -m "not external"
.\.venv\Scripts\python.exe -m pytest -m external
```

M0 验收使用：

```powershell
.\.venv\Scripts\python.exe -m pytest -m external -v
```

## 验收记录

测试执行结果写入 CI 日志或发布检查记录；当前进度摘要写入 [STATUS.md](STATUS.md)。不要在本文复制瞬时通过数量。
