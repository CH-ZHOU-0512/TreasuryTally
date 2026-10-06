---
doc-id: development-plan
title: MVP 开发计划
status: active
authority-for:
  - implementation-sequence
  - milestone-exit-criteria
  - scope-degradation-order
last-reviewed: 2026-10-06
---

# MVP 开发计划

## 实施原则

先完成不依赖网页和模型的确定性纵向切片，再接 AI 编排、交互页面和公共信誉。每个阶段都必须产生可测试交付物，不用演示文案代替真实调用。

## 里程碑

| 阶段 | 预算 | 交付物 | 退出条件 |
|---|---:|---|---|
| M0 连通性验证 | 4h | RPC、Blockscout、Agent0、ERC-8004 外部测试探针 | 四项均有真实返回；写链已确认并读回；失败项有错误映射、降级 adapter 和脱敏记录 |
| M1 契约与样例 | 4h | Pydantic 模型、JSON Schema、12 份标注样例 | schema 校验通过，样例覆盖测试矩阵 |
| M2 确定性验收 | 8h | 标准化、分页、过滤、去重、集合对照、汇总、Finding | 立项案例得到 110000，核心单测通过 |
| M3 报表服务 | 4h | 服务 A/B、签名、故障注入、一次补交 | 能稳定重放正确与错误交付，attempt 不覆盖 |
| M4 AI 编排 | 5h | 主张提取、计划生成、白名单校验、补查建议 | 模型不可绕过结构校验或决定金额 |
| M5 Streamlit | 6h | 条件确认、执行进度、差异、补交/换源、回执预览 | 浏览器完整走通两条演示路径 |
| M6 公共回执 | 5h | JSON 回执、发布 adapter、ERC-8004 关联、读回 | 新会话可校验哈希并重放一项检查 |
| M7 验收封装 | 4h | 全量测试、README 运行说明、演示脚本 | MVP 完成标准逐项有证据 |

总预算：40 小时。

M1 采用主负责人统一契约、两位 AI 分别负责 fixtures 与 Schema/测试的并行方式；启动条件、分支和
文件所有权见 [M1_HANDOFF.md](M1_HANDOFF.md)。该文档只规定协作，不改变本计划的范围或退出条件。

## M0 连通性验证

M0 只证明关键外部能力真实可用，不实现产品页面或验收业务。详细端点、资产、探针和降级约定以 [INTEGRATIONS.md](INTEGRATIONS.md) 为准。

执行顺序：

1. 固定 Sepolia、RPC、测试 ERC-20、已知 Transfer、Agent0/ERC-8004 部署地址和三个测试钱包公钥。
2. 建立 `tests/external/`，在 `pyproject.toml` 注册 `external` marker 和 Ruff/pytest 基础配置。
3. RPC 探针确认 chain ID、区块读取、`eth_getLogs` 和 Transfer 字段解析。
4. Blockscout MCP 探针完成 initialize、工具发现，并查询同一交易或地址。
5. Agent0 探针读取或创建一个团队控制的演示服务身份，并验证稳定 ID。
6. ERC-8004 探针对受控演示服务提交中性测试反馈，等待确认并读回。
7. 验证无效凭据、超时、空结果和未知分页不会被映射成成功或服务失败。
8. 将脱敏实测结果写入 `INTEGRATIONS.md`，总体进度写入 `STATUS.md`。

M0 完成条件：

- `pytest -m external -v` 明确执行四类真实探针，不能用 mock 或自动跳过代替。
- RPC 至少返回一条真实 ERC-20 Transfer；Blockscout MCP 返回可映射的结构化数据。
- Agent0 至少读取一个团队控制的服务身份。
- ERC-8004 至少有一笔确认交易，并从链上读回一致记录。
- 所有实际请求均有超时；只读幂等请求最多重试两次；状态未知的写请求不得自动重发。
- 不在 Git、日志或测试输出中保存私钥、认证头或完整环境变量。
- 每个失败模式都有领域错误和降级决策；证据不足统一进入 `INCONCLUSIVE` 路径。

## 第一纵向切片

输入：

- 一份已确认 `TaskSpec`。
- 一份带故障的 `ServiceSubmission`。
- 一组人工确认的链上 `TransferRecord` fixture。

处理：

- 识别 30000 内部互转。
- 找到漏计的 20000 对外拨款。
- 从服务声称的 120000 得到正确结果 110000。

输出：

- `VerificationResult=FAIL`。
- 两项可复现 Finding。
- 一个本地 JSON Receipt。

这一切片不依赖 LangChain、Streamlit、Blockscout 网络或链上写入。

## 推荐开发顺序

1. 建立 `src/trust_receipt` 包和测试目录。
2. 实现领域枚举及 Pydantic 模型。
3. 编写 JSON Schema 和 fixtures。
4. 写纯函数验收引擎及单元测试。
5. 写 RPC 事件适配器和分页完整性测试。
6. 写 Blockscout MCP 适配器及契约测试。
7. 写 SQLite repository 和 attempt 状态机。
8. 实现服务 A/B 与故障注入。
9. 生成和重放本地回执。
10. 接入 LangChain 结构化提取。
11. 完成 Streamlit 主流程。
12. 接公共存储和 ERC-8004。

## 分阶段依赖门槛

M0 外部连通性需要：

- `BLOCKSCOUT_PRO_API_KEY` 和可用的 `ETH_RPC_URL`。
- Agent0/ERC-8004 测试网部署地址和 ABI 来源。
- 三个仅用于测试网的钱包，其中执行写入的钱包具有少量 Sepolia ETH。
- 测试 ERC-20 地址、已知 Transfer 交易和小区块范围。

M4 AI 编排需要 `OPENAI_API_KEY` 和固定模型名；它们不阻塞 M0—M3。

M6 公共发布需要 `PINATA_JWT` 或等价公共文件存储；它不阻塞本地回执。

缺少外部配置时，M0 只能标记为部分完成；但不阻塞 M1、M2、M3 的 fixture 驱动开发。

## 时间不足时的降级顺序

1. IPFS 改为本地或公开静态文件发布 adapter。
2. ERC-8004 写入保留真实接口，演示使用已准备交易或模拟 adapter。
3. Agent0 动态服务发现改为两个预配置服务。
4. AI 定向补查简化为有限决策树。

不得降级：金额精度、完整分页、事件身份键、三态结论、每次交付留档、回执可重放。

## 变更控制

- 新功能必须先判断是否属于 [PRODUCT.md](PRODUCT.md) 的 MVP。
- 跨模块或破坏契约的改变记录到 [DECISIONS.md](DECISIONS.md)。
- 实际完成情况只更新 [STATUS.md](STATUS.md)，不把本计划变成每日流水账。
