---
doc-id: data-contracts
title: 数据契约与计算不变量
status: active
authority-for:
  - domain-objects
  - event-identity
  - amount-arithmetic
  - receipt-contract
last-reviewed: 2026-10-06
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
- 新增字段应向后兼容；破坏性变更必须提升顶层 schema 版本。

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
- 任务确认后除 `task_id` 外参与判断的字段不可变。
- 任何修改产生新的任务版本和新的 `spec_hash`。

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

## VerificationResult

```yaml
run_id: string
task_id: string
submission_id: string
verifier_version: string
reference_sources: [source_descriptor]
reference_complete: boolean
calculated_total_base_units: integer-string | null
calculated_count: integer | null
findings: [Finding]
outcome: PASS | FAIL | INCONCLUSIVE
started_at: datetime
finished_at: datetime
```

判定顺序：

1. 参考数据不完整或关键元数据未知，结果为 `INCONCLUSIVE`。
2. 否则存在确认错误，结果为 `FAIL`。
3. 否则所有必需检查完成，结果为 `PASS`。

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
```

公开回执不得包含私钥、API 密钥、未授权个人信息或未脱敏的私有报告正文。

## 精确计算规则

- 所有加减在 `amount_base_units` 整数上完成。
- `decimals` 只影响显示格式；不得先转浮点数再汇总。
- 参考集合和交付集合在应用同一任务规则后进行比较。
- 分页完成条件由数据适配器显式报告；未知分页状态不能视为完整。
- 区块范围两端均包含在内。
- 超过 200 条相关事件时不抽样通过，返回需要分段的明确状态。
