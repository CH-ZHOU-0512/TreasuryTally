---
doc-id: data-contracts
title: 数据契约与计算不变量
status: active
authority-for:
  - domain-objects
  - event-identity
  - amount-arithmetic
  - receipt-contract
last-reviewed: 2026-10-07
---

# 数据契约与计算不变量

本文描述概念契约。实现后，字段类型和必填项的机器权威应落入 `schemas/` 中的 JSON Schema；本文继续解释语义、不变量和兼容策略。

## 通用规则

- ID 使用不可变字符串，推荐 UUIDv7 或同等可排序标识。
- 时间使用带时区的 ISO 8601 UTC 字符串。
- EVM 地址存储时保留校验和形式，比较时使用规范化 20 字节值。
- 哈希使用带 `0x` 的十六进制字符串，并记录算法；默认 `keccak256` 或 `sha256`，不得混用而不标注。
- 金额使用代币最小单位的十进制整数字符串，展示值不是计算权威。
- 规范化哈希使用稳定字段顺序、UTF-8 和明确的 canonical JSON 算法。
- 当前 canonical JSON 规则为：JSON 对象键按 Unicode 字符串排序、无非必要空白、UTF-8 编码、数组保留顺序，
  且递归拒绝二进制浮点值；稳定哈希为带 `0x` 前缀的小写 `sha256`。
- 新增字段应向后兼容；破坏性变更必须提升顶层 schema 版本。
- M1 的 Pydantic 领域模型使用严格输入、`extra=forbid` 和冻结实例；适配器必须在进入领域层前完成类型转换。
- M1 地址边界只校验 `0x` 加 40 个十六进制字符并保留输入大小写；地址集合去重和比较使用小写比较键，EIP-55
  校验和转换属于后续标准化层，不由领域模型依赖 Web3 完成。
- M1 的 32 字节交易、区块和内容哈希使用 `0x` 加 64 个十六进制字符；哈希算法仍由字段语义或相邻算法字段确定。
- 所有 `*_base_units` 字段只接受无符号、无前导零的十进制整数字符串（零写作 `"0"`）；适配器内可短暂使用
  Python `int`，但不得用 `float`，进入领域模型时必须转为上述字符串。
- 时间字段必须包含时区且 UTC 偏移为零。

## TaskSpec

```yaml
schema_version: "1.0"
task_id: string
chain_id: integer
token_address: address
treasury_addresses: [address]       # 1..2
recipient_addresses: [address]      # 已确认集合
start_block: integer                # inclusive
end_block: integer                  # inclusive
exclusion_rules: [rule]
max_records: integer                # MVP 固定上限 200
confirmed_at: datetime
spec_hash: hash
```

不变量：

- `start_block <= end_block`。
- 地址集合去重后再计算指纹。
- `treasury_addresses` 必须包含 1..2 个地址；`recipient_addresses` 至少包含 1 个地址；两者分别按小写比较键去重。
- M1 唯一允许的排除规则类型为 `EXCLUDE_TREASURY_INTERNAL`；新增规则类型需要先修改本文并重新冻结契约。
- `max_records` 在 schema `1.0` 中固定为 `200`。
- 任务确认后除 `task_id` 外参与判断的字段不可变。
- 任何修改产生新的任务版本和新的 `spec_hash`。
- `spec_hash` 覆盖除 `spec_hash` 自身外的完整 canonical `TaskSpec`。

## TransferRecord

```yaml
chain_id: integer
token_address: address
transaction_hash: hash
log_index: integer
block_number: integer
block_hash: hash | null
from_address: address
to_address: address
amount_base_units: integer-string
token_decimals: integer
source: rpc | blockscout | service
```

事件身份键为：

```text
(chain_id, transaction_hash, log_index)
```

禁止只用交易哈希去重，因为一笔交易可以发出多个 `Transfer` 日志。

`source` 是事实来源标签：RPC、Blockscout 参考证据和服务自报记录必须保持可区分。模型不禁止多个记录拥有相同
事件键，因为重复项本身是必须被验收引擎识别的输入错误。

## ServiceSubmission

```yaml
schema_version: "1.0"
submission_id: string
task_id: string
service_id: string
service_version: string
attempt: integer                    # 从 1 开始，MVP 最大 2
claimed_total_base_units: integer-string
claimed_count: integer
transfers: [TransferRecord]
report_text: string
created_at: datetime
report_hash: hash
signature: string | null
```

原始文件必须先保存和哈希，再进行解析。解析产物不能替代原始交付。

不变量：

- `attempt` 只能为 1 或 2。
- `transfers` 最多 200 条，且其中每条记录的 `source` 必须为 `service`。
- `claimed_count` 为非负整数；不得根据 `transfers` 长度静默改写服务声明。
- `report_hash` 覆盖除 `report_hash` 与 `signature` 外的完整 canonical `ServiceSubmission`；签名绑定
  `report_hash`，当前团队控制 adapter 使用 EVM personal-sign 消息恢复签名者地址。

## VerificationPlan

```yaml
schema_version: "1.0"
plan_id: string
task_id: string
claims: [claim]
queries: [approved_query]
filters: [approved_filter]
aggregation_rules: [approved_rule]
checks: [approved_check]
plan_version: string
```

所有操作必须来自代码定义的白名单。模型生成的未知操作导致计划校验失败，不得降级为任意代码执行。

M1 冻结的白名单枚举为：

- claim：`CLAIMED_TOTAL`、`CLAIMED_COUNT`、`TRANSFER_SET`。
- query：`FETCH_ERC20_TRANSFERS`。
- filter：`TOKEN_ADDRESS`、`BLOCK_RANGE`、`TREASURY_DIRECTION`、`EXCLUDE_INTERNAL_TRANSFER`、`RECIPIENT_SET`。
- aggregation：`SUM_BASE_UNITS`、`COUNT_TRANSFERS`。
- check：`COMPARE_EVENT_SET`、`COMPARE_TOTAL`、`DETECT_DUPLICATES`、`VALIDATE_SCOPE`、`VALIDATE_TOKEN_DECIMALS`。

每项计划操作包含稳定字符串 ID、枚举类型和 JSON 参数对象；未知类型或额外字段必须被拒绝。
`claims`、`queries`、`filters`、`aggregation_rules` 和 `checks` 在已形成的计划中都至少包含一项。

## M4 受限 AI 中间产物

M4 的模型输出是待校验候选，不是已确认任务、参考证据或验收结论。所有模型使用严格输入、`extra=forbid`
和冻结实例；供应商原始响应不得跨过 adapter 进入核心编排。

### TaskSpecCandidate

```yaml
schema_version: "1.0"
candidate_id: string
chain_id: integer | null
token_address: address | null
treasury_addresses: [address] | null
recipient_addresses: [address] | null
start_block: integer | null
end_block: integer | null
exclusion_rules: [rule] | null
max_records: 200
ambiguities: [clarification_issue]
missing_fields: [task_field]
clarification_questions: [string]
```

`missing_fields` 必须与值为 `null` 的必填任务字段精确一致；地址数量、范围顺序和排除规则仍受 `TaskSpec`
同等约束。存在缺失或歧义时必须给出确认问题，且不得生成 `TaskSpec`。只有无缺失、无歧义的候选才能由确定性代码
注入 `task_id`、`confirmed_at`，计算 `spec_hash` 并形成已确认任务；模型不得提供或覆盖这些字段。

### ClaimExtraction

```yaml
schema_version: "1.0"
report_id: string
claims: [claim]
ambiguities: [clarification_issue]
clarification_questions: [string]
source_summary: string
```

主张类型仍只允许 `CLAIMED_TOTAL`、`CLAIMED_COUNT` 和 `TRANSFER_SET`。总额必须是规范十进制整数字符串，
数量必须是非负整数，转账集合必须是 JSON 数组；重复 `claim_id`、重复主张类型或未知类型直接拒绝，冲突主张必须转为
歧义。存在歧义时不得生成执行计划。

### FollowUpAdvice 与 ResultExplanation

补查动作只允许 `NO_ACTION`、`REFRESH_REFERENCE_EVIDENCE`、`CROSS_CHECK_REFERENCE_SOURCE`、
`CONFIRM_TASK_SCOPE`、`REQUEST_RESUBMISSION`、`SWITCH_SERVICE` 和 `MANUAL_REVIEW`。建议只表达下一步，不包含
Shell、文件、SQL、Python、数据库写入、发布或写链调用。

结果解释必须逐字绑定确定性 `VerificationResult` 的 `outcome`、`calculated_total_base_units`、
`calculated_count` 和 Finding ID；模型只能解释，不能改写金额、数量、Finding 或三态结论。

## Finding

允许的首版类型：

- `MISSING_TRANSFER`
- `EXTRA_TRANSFER`
- `DUPLICATE_TRANSFER`
- `EXCLUDED_INTERNAL_TRANSFER`
- `OUT_OF_RANGE`
- `WRONG_TOKEN`
- `WRONG_DIRECTION`
- `AMOUNT_MISMATCH`
- `DECIMAL_ERROR`
- `INSUFFICIENT_EVIDENCE`

每项 Finding 至少包含：

```yaml
finding_id: string
finding_type: enum
severity: info | warning | error
expected: object | null
actual: object | null
violated_rule: string
evidence_refs: [string]
explanation: string
status: confirmed | hypothesis
```

只有 `confirmed` 且证据充分的错误才能导致 `FAIL`；`hypothesis` 只能触发补查或人工确认。
`evidence_refs` 至少包含一个稳定引用。

## VerificationResult

```yaml
run_id: string
task_id: string
submission_id: string
verifier_version: string
reference_sources: [source_descriptor]
reference_complete: boolean
evidence_sufficient: boolean
calculated_total_base_units: integer-string | null
calculated_count: integer | null
findings: [Finding]
outcome: PASS | FAIL | INCONCLUSIVE
inconclusive_reason: string | null
started_at: datetime
finished_at: datetime
```

判定顺序：

1. `reference_complete=false` 或 `evidence_sufficient=false` 时结果为 `INCONCLUSIVE`，并要求非空
   `inconclusive_reason`；此时金额和数量可以为空。
2. 否则存在确认错误，结果为 `FAIL`。
3. 否则所有必需检查完成，结果为 `PASS`。

`PASS` 和 `FAIL` 要求参考完整、证据充分、金额与数量非空且 `inconclusive_reason=null`。只有
`status=confirmed` 且 `severity=error` 的 Finding 属于确认错误；hypothesis 不得单独导致 `FAIL`。
`reference_sources` 只能包含 `rpc` 或 `blockscout`；`reference_complete=true` 要求每个来源描述符也标记完整。

## Receipt

```yaml
receipt_version: "1.0"
receipt_id: string
task_spec: TaskSpec
service_identity: object
submission_hash: hash
verification_plan: VerificationPlan
verification_result: VerificationResult
evidence_manifest: [evidence_descriptor]
created_at: datetime
receipt_hash: hash
publication:
  authorized: boolean
  uri: string | null
  content_hash: hash | null
  transaction_hash: hash | null
  chain_status: NOT_SUBMITTED | SUBMITTED | CONFIRMED | FAILED
  chain_id: integer | null
  reviewer_address: address | null
  transaction_nonce: integer | null
  feedback_index: integer | null
  block_number: integer | null
  error_code: string | null
  error_message: string | null
```

公开回执不得包含私钥、API 密钥、未授权个人信息或未脱敏的私有报告正文。

公开上传对象是 `authorized=true`、尚未绑定 URI 的不可变回执快照。上传后以实际下载字节的 SHA-256 作为
`publication.content_hash`，重新下载并验证一致后，本地发布状态才绑定 URI 与内容哈希。这样避免让文件自带的 URI/内容哈希
形成循环哈希，同时公共文件本身仍可独立校验 `receipt_hash` 并重放确定性结论。

链上状态不把广播等同于确认：`NOT_SUBMITTED` 可表示已公开但未写链；`SUBMITTED` 必须记录 chain、Reviewer 和 nonce，
交易哈希在广播结果未知时可以为空；`CONFIRMED` 还必须包含交易哈希、feedback index 和区块，并已从 `NewFeedback` 事件读回
服务 ID、Reviewer、URI、内容哈希及结果标签；`FAILED` 必须记录脱敏错误码。`SUBMITTED` 的未知写入禁止自动重发。
`FAILED` 只有在用户核对原因并显式授权后才能清除交易字段回到 `NOT_SUBMITTED`；该恢复路径不得接受
`TRANSACTION_UNKNOWN`。

`receipt_hash` 覆盖除 `receipt_hash` 自身外的完整 canonical `Receipt`。publication 状态变化会产生新的回执内容和
新哈希，不得沿用旧哈希。

## Attempt 持久化不变量

- SQLite 分别保存 `TaskSpec`、每个 `ServiceSubmission`/故障注入元数据和每个 `VerificationResult`。
- `(task_id, attempt)` 与 `submission_id` 唯一；attempt 只能追加，禁止 UPSERT 或覆盖。
- attempt 从 1 连续增长到 2；只有第一次结果为 `FAIL` 或 `INCONCLUSIVE` 时才能请求第二次。
- 故障注入元数据只描述团队控制模拟行为，不属于服务声明或 RPC/Blockscout 参考事实。

## M1 fixture 契约

M1 人工标注数据放在：

```text
fixtures/m1/
├─ manifest.json
└─ cases/
   └─ <fixture_id>.json
```

`fixture_id` 和文件名必须一致，使用小写 kebab-case。每个 case 的顶层结构固定为：

```yaml
fixture_version: "1.0"
fixture_id: string
title: string
tags: [string]
task_spec: TaskSpec
submission: ServiceSubmission
reference:
  sources: [source_descriptor]
  reference_complete: boolean
  evidence_sufficient: boolean
  transfers: [TransferRecord]       # source 只能为 rpc 或 blockscout
  insufficiency_reason: string | null
expected:
  outcome: PASS | FAIL | INCONCLUSIVE
  calculated_total_base_units: integer-string | null
  calculated_count: integer | null
  findings: [expected_finding]
human_review:
  summary: string
  calculation: string
  reviewer: string
  verified_at: datetime
```

`expected_finding` 固定记录 `finding_type`、`severity`、`status`、`violated_rule` 和关联的三段式
`event_keys`。`INCONCLUSIVE` case 必须在 reference 中说明证据不足原因，不能用服务错误冒充。
`manifest.json` 使用 `FixtureManifest`，包含 `fixture_version` 和 12 个 `FixtureManifestEntry`；entry 固定记录
`fixture_id`、相对 `file`、`title`、`tags` 与 `expected_outcome`。

## M1 JSON Schema 命名

Schema version 为 `1.0`，稳定输出目录和文件名为：

```text
schemas/v1/task_spec.schema.json
schemas/v1/transfer_record.schema.json
schemas/v1/service_submission.schema.json
schemas/v1/verification_plan.schema.json
schemas/v1/verification_result.schema.json
schemas/v1/receipt.schema.json
schemas/v1/fixture_case.schema.json
schemas/v1/fixture_manifest.schema.json
schemas/v1/task_spec_candidate.schema.json
schemas/v1/claim_extraction.schema.json
schemas/v1/follow_up_advice.schema.json
schemas/v1/result_explanation.schema.json
```

每个文件的 `$id` 使用 `urn:xinjv:schema:1.0:<kebab-name>`，标题使用对应 Pydantic 公共类名。生成入口预留为
`scripts/export_schemas.py`；前八份为冻结的 M1 顶层契约，后四份为 M4 受限 AI 中间产物。重复生成不得产生差异。

## 精确计算规则

- 所有加减在 `amount_base_units` 整数上完成。
- `decimals` 只影响显示格式；不得先转浮点数再汇总。
- 参考集合和交付集合在应用同一任务规则后进行比较。
- 分页完成条件由数据适配器显式报告；未知分页状态不能视为完整。
- 区块范围两端均包含在内。
- 超过 200 条相关事件时不抽样通过，返回需要分段的明确状态。
