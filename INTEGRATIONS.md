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

本文是 RPC、Blockscout、Agent0、ERC-8004 和结构化模型供应商外部集成的权威入口。它记录需要核实的端点、公开合约与资产、最小探针、成功条件和降级策略。总体进度仍由 [STATUS.md](STATUS.md) 负责，密钥规则由 [SECURITY.md](SECURITY.md) 负责。

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
| 网络 | Sepolia | 已验证 | RPC `eth_chainId` |
| Chain ID | `11155111` | 已验证 | RPC 返回 `11155111` |
| RPC 端点 | 公共 Sepolia RPC，来自 `ETH_RPC_URL` | 已验证 | 无密钥公共端点；请求超时 30 秒 |
| Blockscout MCP | `http://127.0.0.1:8000` | 本地 CLI 已验证，HTTP 工具调用待实测 | M0 探针 |
| 测试 ERC-20 | Sepolia WETH `0x7b79…7f9` | 已验证 | block `11855664` 的真实 Transfer |
| Identity Registry | `0x8004A818…4BD9e` | 已验证 | 上游部署记录、链上 proxy bytecode、owner/tokenURI 读回 |
| Reputation Registry | `0x8004B663…88713` | 已验证 | 上游部署记录、链上 proxy bytecode、Identity Registry 关联 |
| Validation Registry | `0x8004Cb1B…B4272` | 已验证 | 上游部署记录、链上 proxy bytecode、Identity Registry 关联 |

合约地址不得凭记忆填写。核实时至少比对官方部署来源、chain ID 和链上 bytecode；来源不一致时保持待定。

本地上游参考 `agent0-py` 1.7.1、`erc-8004-contracts/scripts/addresses.ts` 与官方仓库部署记录一致。
2026-10-06 已通过 Sepolia RPC 读取三个地址的 proxy bytecode，并验证 Reputation/Validation Registry
均关联上述 Identity Registry。公开地址保存在本地 `.env`，`.env.example` 仍只保留变量名。

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
| RPC | chain ID、区块、Transfer logs | 区块号、交易哈希、log index | 错误网络、超时、空结果 | 已实测通过 |
| Blockscout MCP | initialize、tools、交易或地址查询 | 工具名、脱敏结果摘要、分页状态 | 缺少密钥、限流、服务不可达 | 已实测通过；发现 16 项工具并读回同一交易 |
| Agent0 | 读取或创建受控身份 | 服务 ID、所有者、公网交易或读结果 | 网络或 Registry 错配 | 已实测通过；受控 ID `11155111:10691` |
| ERC-8004 | 写入、receipt、读回 | 交易哈希、区块、读回摘要 | 余额不足、revert、未知提交状态 | 已实测通过；中性反馈已确认并读回 |

## M4 结构化模型供应商

用途：把自然语言任务和服务报告组织成严格候选，并生成白名单计划、受限补查建议与结果解释。模型不拥有金额、
Finding、三态结论、数据库、发布或写链权限。

- OpenAI：要求 `OPENAI_API_KEY` 与非空 `OPENAI_MODEL`；通过 LangChain `ChatOpenAI` 请求严格 JSON Schema 输出。
- DeepSeek：要求 `DEEPSEEK_API_KEY` 与非空 `DEEPSEEK_MODEL`；使用官方 `https://api.deepseek.com` 的
  OpenAI-compatible Responses API 和 JSON Schema 输出。
- 两者统一 30 秒默认超时、只读请求最多重试两次；原始响应必须立即进入 Pydantic 与确定性白名单校验。
- 外部测试分别位于 `tests/external/test_openai_ai_probe.py` 和 `test_deepseek_ai_probe.py`，统一使用 `external` marker。
- 缺少 key 或固定模型名时报告阻塞；离线 mock 只能验证 adapter 映射和安全边界，不能宣称供应商已实测。

2026-10-07 已使用固定 `deepseek-flash` 完成一次真实结构化调用，返回的 `TaskSpecCandidate` 通过严格 Pydantic
校验；该次临时凭据随后已从本地环境删除，不在 Git、日志或文档中保留。OpenAI 真实调用仍因缺少
`OPENAI_API_KEY` 和 `OPENAI_MODEL` 阻塞。后续再次运行 DeepSeek 探针需要新生成并仅在本机配置的凭据。

失败降级：结构化输出为空、截断、schema 不符、未知操作或与确定性结果冲突时拒绝该候选，保留用户确认或纯确定性流程；
不得自动采用模型猜测，也不得把模型失败映射成服务负面信誉。

## 2026-10-06 脱敏执行记录

- 创建 `pyproject.toml`、`src/trust_receipt/` adapter 和 `tests/external/` 探针骨架。
- 离线测试验证配置阻塞、区块范围校验、只读请求最多重试两次、RPC 超时/错链、Blockscout
  认证/限流/分页未知，以及写入失败状态分类；
  这些测试不计作外部连通证据。
- 首次执行 `pytest -m external -v` 时因没有 `.env`，5 项均明确报告配置阻塞；未计作连通成功。
- 随后通过公共 RPC 固定 Sepolia WETH 的 block `11855664`、交易
  `0x0442…4b6f`、log index `128`，RPC 真实 Transfer 探针通过。过程中发现并修正 Web3.py 7
  十六进制值缺少 `0x` 前缀的兼容问题。
- 创建团队控制的 Agent0 身份 `11155111:10691`；注册交易 `0xb9ed…3384`，最终资料更新交易
  `0x22fb…b460`。Agent0 SDK 1.7.1 已从链上读回名称、active 状态和 owner。
- 第二个团队控制测试钱包对该身份提交值为 `0` 的中性反馈，交易 `0xd84f…9f53` 在 block
  `11855595` 确认；SDK 读回 feedback index `1`、Reviewer、值和两个测试标签一致，且未撤销。
- 三个 Registry 的链上 bytecode 与 Identity Registry 关联已核验。
- Blockscout MCP 0.19.0 已通过本地认证 HTTP Server 完成 initialize、16 项工具发现和同一笔交易查询。
  主环境 MCP 客户端固定为 1.26.0，与服务端依赖一致；访问本机端点时禁用系统代理继承。
- 当前记录只包含公开地址、区块和缩略交易哈希；不包含端点密钥、认证头、钱包私钥或环境变量全集。
- M0 四项真实外部探针均已通过；密钥只保存在被 Git 忽略的本地 `.env` 中。

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
