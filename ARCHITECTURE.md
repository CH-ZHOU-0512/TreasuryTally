---
doc-id: system-architecture
title: 系统架构
status: active
authority-for:
  - component-boundaries
  - system-data-flow
  - dependency-direction
last-reviewed: 2026-10-07
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

M8–M10 计划在现有端口外增加四个明确职责，不改变确定性引擎的权威：

```text
Task/Delivery Commitment Port ── EIP-712 signer + chain anchor adapter
Fund Flow Projection          ── TaskSpec + submission + evidence + findings
Receipt Verification Explorer ── public URI/hash/feedback → replay
Service History Projection    ── verified receipts → traceable facts
```

资金流投影只负责把已有领域事实转换为节点、边和颜色状态，不重新计算金额或结论。服务历史投影同样只聚合已验证回执，
不能成为新的信誉真值或覆盖原始回执。

M8 已实现承诺端口和资金流投影：`commitments` 负责 EIP-712 创建/恢复校验及只读 Registry 能力探针，`projections` 只从
已有 submission、reference evidence 与 Finding 生成视觉读模型。当前没有可用写入 adapter；`CommitmentAnchorPort` 只冻结
边界，页面必须显示 `NOT_SUBMITTED`。`DedicatedAnchorReader` 与 `contracts/CommitmentAnchor.sol` 是未接入页面的候选，
只读 adapter 校验 bytecode、交易、canonical block 与事件绑定，没有广播方法。

`services.upload` 严格解析原始 JSON 声明并私有留档，以独立 local-upload-intake 身份签名；这不认证原始作者。
`M8WorkspaceWorkflow` 在生成交付之前取得接单签名，进入 M5 持久化之前验证交付签名，随后将承诺和 reference evidence
追加到 `M8ArtifactStore`。恢复不重调 AI 或重新取链上快照，而是验证签名、receipt manifest 和确定性结果后重建图。
旧任务缺少快照时不伪造资金流；M5 和 M8 附加存储之间尚无跨事务提交，崩溃可能产生缺少附加快照的旧格式记录。

M9 不修改冻结的 `Receipt 1.0`：`ReceiptRevision` 以外置自哈希记录追加 parent/supersedes 关系，
`LocalRevisionStore` 一个 attempt 只创建一个文件。`ReceiptCommitmentVerifier` 是稳定适配端口；M8 承诺快照可用时，
M9 通过实际 EIP-712 校验给出 `VERIFIED`，缺少快照时保留 `UNVERIFIED` 而不阻塞 v1 回执重放。
`PublicReceiptResolver` 只能返回公开字节、内容哈希和公开关系，不允许回查 SQLite 私有工作区。
Service History Projection 仍属于 M10。

M3 中服务端口只接收已确认 `TaskSpec` 与 attempt 编号；团队控制 adapter 负责生成并签名
`ServiceSubmission`。故障注入状态保存在独立 `ReportDelivery.fault_injection` 元数据中，不写入参考证据，也不伪装为
第三方生产数据。编排层先校验 canonical report hash 和 EVM 签名，再允许交付进入 repository。

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
├─ m9/              # 确定性返工、外置版本链、对比与公开重放
├─ storage/         # SQLite repository
└─ orchestration/   # 用例编排，不包含 UI 逻辑
```

## 依赖方向

- `models` 不依赖 UI、数据库、LangChain 或 Web3 客户端。
- `verification` 只依赖领域模型和纯计算工具。
- `chain`、`services`、`reputation`、`storage` 实现端口，不反向控制领域规则。
- `agents` 只能产生经过校验的结构化候选，不直接写数据库或发布反馈。
- `orchestration` 组合各端口，`app` 只调用用例并展示状态。

M4 的 `agents` 包分成三层：供应商无关的严格 Pydantic 中间产物、只暴露“按指定 schema 生成结构”的
`StructuredOutputPort`，以及 LangChain/OpenAI-compatible adapter。`RestrictedAIService` 不持有 repository、Shell、
文件、发布或写链端口。TaskSpec 的身份、确认时间和哈希由确定性代码注入；VerificationPlan 的操作集合和参数必须逐项
绑定已确认任务；建议与解释必须复用 `VerificationResult` 的三态、金额、数量、Finding ID 和证据引用。

M5 页面通过 `M5Workflow` 用例组合上述端口。页面不直接调用供应商 SDK、SQLite 表或验证内部函数；任务未确认时不暴露
执行入口，AI 主张/计划校验在交付持久化前完成，失败会撤销未完成请求且不消耗 attempt。解释或补查输出被拒绝时，已保存的
确定性结果仍可展示，但被拒绝的 AI 文本不会替代结果。离线 fixture adapter 是明确标注的演示路径，仍须经过相同 Pydantic、
白名单、签名、持久化、验证和回执边界。真实证据路径由 `RpcReferenceEvidenceProvider` 分页读取完整区块范围并检查确认数；
Blockscout 只做可选抽样诊断，不能把失败的 RPC 提升为完整证据。页面以工作区 ID 隔离 SQLite 和私有回执，重启后从两者恢复
已确认任务与完成的 attempt，不重新生成历史 AI 文本。

M6 通过独立 `ContentPublisher` 与 `M6Workflow` 接入页面。公开上传前从私有回执构造不含报告正文、签名和凭据字段的授权快照；
publisher 返回 URI 后必须重新下载并按实际字节做 SHA-256 核验。SQLite 使用只追加 `publication_events` 保存每次状态快照。
ERC-8004 adapter 在写入前核对 Sepolia chain ID、受控 service owner、Reviewer、余额和 pending nonce；每次只广播一次，随后只按
已保存的 nonce/交易哈希读回，禁止把未知状态自动重发。交易 Gas 使用同参数链上估算值并增加 20%（至少 50,000）缓冲，
不使用无法覆盖动态字符串成本的固定上限。

生产 publisher 优先 Pinata/IPFS；未配置 JWT 时可使用内容寻址 HTTPS 目录。后者由应用容器只写公共目录、Nginx 只读公开，
仍执行公网下载哈希核验，但不把 HTTPS 文件表述为 IPFS 固定内容。

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

M8–M10 在此基础上追加：

10. 用户确认任务后生成任务承诺；服务身份对接单和报告哈希签名，链上锚定 adapter 的选择以真实接口探针为前置条件。
11. 资金流投影把参考事件、服务声明和 Finding 映射为稳定视觉语义，点击边可回到完整事件键和浏览器链接。
12. 首次失败生成返工包；第二次交付与首次交付并排留档，并通过父回执/替代关系形成版本链。
13. 独立验证入口从公开 URI、回执哈希、任务哈希或反馈交易恢复对象关系并重放确定性结论。
14. 服务历史投影按任务类型聚合可验证事实，供下一次人工选择服务使用。

本地回执存储使用只创建、不覆盖的 JSON 文件。独立重放入口重新校验 `receipt_hash`、嵌套 `spec_hash`、任务链接，
并仅根据参考完整性、证据充分性和 confirmed error 重新推导 PASS/FAIL/INCONCLUSIVE；它不依赖原聊天历史、UI、
数据库连接或模型服务。

canonical JSON 使用 UTF-8、按键名排序、无空白 JSON 表示，明确拒绝 `float`；当前稳定哈希算法为 SHA-256，输出
`0x` 加 64 位小写十六进制。`TaskSpec`、`ServiceSubmission` 和 `Receipt` 分别排除自身哈希字段；交付哈希还排除
签名字段，避免循环依赖。

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

terminal result → RECEIPT_CREATED → PUBLISHING → PUBLISHED(NOT_SUBMITTED)
                                               → SUBMITTED → CONFIRMED | FAILED
```

失败重试不得覆盖旧 attempt；发布失败也不得改变验收结论。

SQLite 将任务、交付 attempt 和验证结果放在三张独立表中。`(task_id, attempt)` 与 `submission_id` 都是唯一键，
只允许 INSERT，不提供覆盖更新；第二次交付必须在第一次得到 `FAIL` 或 `INCONCLUSIVE` 后显式请求，第三次请求被拒绝。

## 外部依赖

- Python 3.12 主环境：应用、测试和 Streamlit。
- 独立 Python 环境：Blockscout MCP Server，避免 MCP 版本约束污染主环境。
- EVM JSON-RPC：参考事件读取。
- Blockscout MCP：补充地址、交易和代币信息。
- OpenAI 或 DeepSeek 的兼容结构化输出模型：主张和计划组织；应用不向模型开放可执行工具。
- Agent0/ERC-8004：服务身份和公开反馈关联。
- 公共文件存储/IPFS：完整回执链下保存。

当前连通性和实现状态不在本文维护，请查看 [STATUS.md](STATUS.md)。

## 页面适配边界

Streamlit 定位为链上报表验收工具，而不是开发工作台。首屏只保留一句价值说明、“上传报表 → 确认范围 → 链上核验”三步和
当前唯一主操作；Agent、RPC、Blockscout、哈希、Registry 与状态机细节进入默认折叠的验证依据区。结果页先展示三态、声称金额、
链上有效金额、差异和资金流图，再展示 Finding、返工和发布动作。

页面使用宽布局，但关键内容以卡片和可换行字段呈现，不依赖宽表格。桌面端允许资金流与问题列表并排；760px 及以下强制
折叠为单列，按钮占满可用宽度，长哈希与 JSON 可换行或横向滚动。资金流颜色不能是唯一语义，还必须配合图标、文本和
可访问标签。响应式样式和可视化投影 adapter 只属于 `app/`，不会进入领域层。
