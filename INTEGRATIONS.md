---
doc-id: external-integrations
title: 外部集成与 M0 连通性规格
status: active
authority-for:
  - external-integration-contracts
  - external-probe-acceptance
  - external-fallback-policy
last-reviewed: 2026-10-06
---

# 外部集成与 M0 连通性规格

本文是 RPC、Blockscout、Agent0 和 ERC-8004 外部集成的权威入口。它记录需要核实的端点、公开合约与资产、最小探针、成功条件和降级策略。总体进度仍由 [STATUS.md](STATUS.md) 负责，密钥规则由 [SECURITY.md](SECURITY.md) 负责。

## 共同约束

- MVP 网络固定为 Sepolia，预期 `chain_id=11155111`；探针必须实际读取并比对，不能只信配置值。
- 外部返回均视为不可信输入，必须经过类型、网络、地址和范围校验。
- 单次请求默认超时 30 秒；只读幂等请求最多重试两次并采用退避。
- 写交易返回不确定时先按地址和 nonce 查询，不得自动重复广播。
- 探针位于 `tests/external/`，统一使用 pytest `external` marker。
- 临时响应和诊断文件只能进入 `.tmp/`，不得提交，也不得成为正式运行依赖。
- 只保存脱敏证据；API Key、私钥、认证头和环境变量全集不得进入日志、fixture、Markdown 或 Git。
- Mock 可以验证 adapter，但不能作为外部能力已连通的证明。

## 已知公共配置

| 项目 | 预期值 | 状态 | 核实证据 |
|---|---|---|---|
| 网络 | Sepolia | 待实测 | RPC `eth_chainId` |
| Chain ID | `11155111` | 待实测 | RPC 返回 |
| RPC 端点 | 来自 `ETH_RPC_URL` | 待配置 | 不记录完整 URL 中的密钥 |
| Blockscout MCP | `http://127.0.0.1:8000` | 本地 CLI 已验证，HTTP 工具调用待实测 | M0 探针 |
| 测试 ERC-20 | `TEST_TOKEN_ADDRESS` | 待选择 | 官方或可信来源与已知交易 |
| Identity Registry | `ERC8004_IDENTITY_REGISTRY_ADDRESS` | 待核实 | 官方部署记录和链上 bytecode |
| Reputation Registry | `ERC8004_REPUTATION_REGISTRY_ADDRESS` | 待核实 | 官方部署记录和链上 bytecode |
| Validation Registry | `ERC8004_VALIDATION_REGISTRY_ADDRESS` | 待核实 | 官方部署记录和链上 bytecode |

合约地址不得凭记忆填写。核实时至少比对官方部署来源、chain ID 和链上 bytecode；来源不一致时保持待定。

## EVM RPC

用途：提供与报表服务相互独立的参考链上事件。

最小探针：

1. 调用 `eth_chainId` 并确认 `11155111`。
2. 获取最新区块及一个固定历史区块。
3. 在已知小区块范围对测试代币调用 `eth_getLogs`。
4. 解析至少一条 ERC-20 `Transfer` 的交易哈希、日志索引、区块、from、to 和整数金额。
5. 读取代币 `decimals`，但不将金额转换为浮点数计算。
6. 验证错误 RPC、超时和空结果能被区分。

成功条件：获得至少一条真实 Transfer，并构造事件键 `(chain_id, transaction_hash, log_index)`。

失败降级：RPC 数据不完整、网络不符、重组风险未知或查询失败时，验收证据标记不完整并进入 `INCONCLUSIVE`；Blockscout 不能单独掩盖参考节点失败。

## Blockscout MCP

用途：补充地址、交易、代币和分页信息，不作为被评价服务，也不单独承担参考真值。

运行端点：来自 `BLOCKSCOUT_MCP_URL`，默认 `http://127.0.0.1:8000`。

最小探针：

1. 启动本地 MCP Server，完成 initialize 和工具发现。
2. 执行一个无需业务假设的基础读取。
3. 查询与 RPC 探针相同的交易或地址。
4. 记录字段映射、分页游标、终止条件、限流和认证错误。
5. 测量一次正常调用耗时，不记录认证信息。

成功条件：返回可映射到领域模型的结构化结果，并能明确判断分页是否完整。

失败降级：切换为 RPC-only adapter 并记录缺少补充数据；若任务依赖 Blockscout 独有信息，则进入 `INCONCLUSIVE`。

## Agent0

用途：提供团队控制的演示服务身份和后续服务发现接口。

最小探针：

1. 初始化 Python SDK 并确认使用的网络和 Registry 配置。
2. 读取或创建一个团队控制的演示服务身份。
3. 读取服务 ID、所有者和可用的服务元数据。
4. 确认服务 A/B 能由稳定 ID 引用。
5. 记录 SDK 版本、调用方式和失败类型。

成功条件：至少一个受控服务身份可重复读取，且不会与真实第三方服务混淆。

失败降级：MVP 使用本地预配置服务 ID；不得宣称已完成开放服务发现。

## ERC-8004

用途：把受控服务、反馈提交者、验收结果与公开回执 URI/哈希关联。

最小探针：

1. 核实测试网 Registry 地址、ABI 和链上 bytecode。
2. 检查 Reviewer 测试钱包的 chain ID、余额和 nonce。
3. 仅对团队控制的演示服务提交中性、明确标注为测试的反馈。
4. 保存公开交易哈希，区分 `NOT_SUBMITTED`、`SUBMITTED`、`CONFIRMED`、`FAILED`。
5. 等待 receipt 后从链上读回并比对服务 ID、提交者和反馈内容。
6. 模拟超时或未知提交状态，确认不会自动重复广播。

成功条件：至少一笔测试交易确认，并从链上读回一致记录。

失败降级：保留本地回执与 publication adapter 状态，不显示为已上链；不得向真实第三方服务写入负面测试反馈。

## M0 执行矩阵

| 探针 | 真实调用 | 成功证据 | 必测失败 | 当前状态 |
|---|---|---|---|---|
| RPC | chain ID、区块、Transfer logs | 区块号、交易哈希、log index | 错误网络、超时、空结果 | 待执行 |
| Blockscout MCP | initialize、tools、交易或地址查询 | 工具名、脱敏结果摘要、分页状态 | 缺少密钥、限流、服务不可达 | 待执行 |
| Agent0 | 读取或创建受控身份 | 服务 ID、所有者、公网交易或读结果 | 网络或 Registry 错配 | 待执行 |
| ERC-8004 | 写入、receipt、读回 | 交易哈希、区块、读回摘要 | 余额不足、revert、未知提交状态 | 待执行 |

执行结果更新规则：

- 只把实际观察到的行为改为“已验证”。
- 失败也要记录错误类别和可复现命令，但不得记录秘密值。
- 详细原始响应放在 `.tmp/` 并在验证后清理；可提交内容只保留必要的脱敏摘要。
- M0 全部完成后，在 [STATUS.md](STATUS.md) 更新总体阶段；架构或范围变化追加到 [DECISIONS.md](DECISIONS.md)。

## M0 验收命令

```powershell
.\.venv\Scripts\python.exe -m pytest -m external -v
```

如果缺少密钥、测试币、合约地址或已知测试资产，该命令应明确报告阻塞项。跳过或 mock 通过不能视为 M0 完成。
