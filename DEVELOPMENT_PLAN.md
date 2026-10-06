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
| M0 连通性验证 | 4h | RPC、Blockscout、Agent0、ERC-8004 最小探针 | 每项有实际返回，失败项有可替换 adapter 和记录 |
| M1 契约与样例 | 4h | Pydantic 模型、JSON Schema、12 份标注样例 | schema 校验通过，样例覆盖测试矩阵 |
| M2 确定性验收 | 8h | 标准化、分页、过滤、去重、集合对照、汇总、Finding | 立项案例得到 110000，核心单测通过 |
| M3 报表服务 | 4h | 服务 A/B、签名、故障注入、一次补交 | 能稳定重放正确与错误交付，attempt 不覆盖 |
| M4 AI 编排 | 5h | 主张提取、计划生成、白名单校验、补查建议 | 模型不可绕过结构校验或决定金额 |
| M5 Streamlit | 6h | 条件确认、执行进度、差异、补交/换源、回执预览 | 浏览器完整走通两条演示路径 |
| M6 公共回执 | 5h | JSON 回执、发布 adapter、ERC-8004 关联、读回 | 新会话可校验哈希并重放一项检查 |
| M7 验收封装 | 4h | 全量测试、README 运行说明、演示脚本 | MVP 完成标准逐项有证据 |

总预算：40 小时。

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

## 依赖门槛

开始外部联调前需要：

- `OPENAI_API_KEY`
- `BLOCKSCOUT_PRO_API_KEY`
- 可用的 `ETH_RPC_URL`
- 三个仅用于测试网的钱包，且具有少量测试币
- 测试代币或固定的历史样例地址
- 如使用 IPFS，配置 `PINATA_JWT`

缺少这些配置不阻塞 M1、M2、M3 的 fixture 驱动开发。

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
