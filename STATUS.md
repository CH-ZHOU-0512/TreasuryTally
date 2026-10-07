---
doc-id: project-status
title: 当前项目状态
status: active
authority-for:
  - current-status
  - active-work
  - known-blockers
last-reviewed: 2026-10-07
---

# 当前项目状态

更新时间：2026-10-07

## 当前阶段

M1 已完成：领域契约、Pydantic 模型、8 份 JSON Schema、契约测试和 12 份人工标注 fixtures
均已集成到 `codex/m1-integration`。M2 PR #1 已合并，远端合并提交为
`d9ac1108e9a21fe0073587d4f458848ed1ac8ecd`。M3 无 UI 纵向闭环及本地回执重放已在本地实现并验证。
M4 受限 AI 编排、供应商 adapter、离线对抗测试及真实 DeepSeek 结构化调用已完成。M5 Streamlit 产品页面、
fixture 路径与真实 DeepSeek + Sepolia RPC + Blockscout 产品闭环均已完成；桌面、移动端和进程重启恢复均已做真实浏览器检查。
M5 已部署至广州 Linux 服务器的隔离容器，并通过现有 HTTPS 反向代理公开访问。M6 公共回执发布与 ERC-8004 关联均已
完成真实 Sepolia 产品闭环：公共内容哈希、链上反馈、事件读回和 SQLite 终态一致。M7 验收封装与本地收尾已完成；
`codex/m1-integration` 已同步远端 M2 合并历史并进入 `main`，最终主线 CI 已通过。M8 资金流投影、EIP-712 承诺、前端主流程
重构与 Validation Registry 只读探针已合并并部署到广州应用；专用锚仍只是未部署候选，M9–M10 独立分支仍在并行开发。

## 已完成

- Python 3.12 主环境 `.venv` 已创建，`pip check` 通过。
- Agent0 SDK、LangChain、Streamlit、Web3.py、Pydantic、SQLAlchemy、Pytest、Ruff 已安装。
- Blockscout MCP 已在 `.venv-blockscout` 独立安装，CLI 和 `pip check` 通过。
- Streamlit 基础启动健康检查已通过。
- `agent0-py`、`erc-8004-contracts`、Blockscout `mcp-server` 已下载到 `references/`。
- ERC-8004 参考合约编译成功，79 项上游测试通过。
- 根目录、环境变量模板、依赖清单和锁定快照已建立。
- 开发前产品、架构、数据、测试、安全、运维和协作文档已建立。
- M0 外部集成规格、分阶段依赖门槛和代码文件规模约束已建立。
- Git 仓库已连接到 `https://github.com/CH-ZHOU-0512/xinjv`，默认分支为 `main`。
- 已创建 `pyproject.toml`、`src/trust_receipt/` 包和 `tests/external/`，包含 RPC、Blockscout MCP、
  Agent0 与 ERC-8004 的最小探针。
- 外部调用统一设置超时；只读操作最多重试两次；ERC-8004 写探针默认关闭且不自动重发未知交易。
- RPC 已在 Sepolia 读取固定历史区块和真实 WETH Transfer，保留整数金额及完整事件键。
- Blockscout MCP 已完成 initialize、16 项工具发现及同一笔 Sepolia 交易查询；客户端与服务端统一使用 MCP 1.26.0。
- 已创建团队控制的 Agent0 身份 `11155111:10691`，Agent0 SDK 1.7.1 可重复读取名称、owner 和 active 状态。
- 三个 ERC-8004 Registry 的链上 bytecode 与相互关联已核验；中性反馈交易已确认并从链上读回一致内容。
- 已建立 `codex/m1-integration` 与 `codex/m1-core-models` 分支，并从远端 `main` 合并提交
  `b44945b48bef8b77b9fe4633fd714de75a66d636` 开始 M1。
- 已冻结 `trust_receipt.models` 公共边界，覆盖任务、转账、服务交付、白名单计划、三态验证结果、回执及
  M1 fixture/manifest 模型。
- 核心金额在领域边界使用无符号十进制整数字符串；事件键保留 `chain_id + transaction_hash + log_index`；
  参考不完整或证据不足强制为 `INCONCLUSIVE`。
- fixture 布局固定为 `fixtures/m1/manifest.json` 与 `fixtures/m1/cases/`；8 个顶层 Schema 文件固定输出到
  `schemas/v1/`，导出脚本路径固定为 `scripts/export_schemas.py`。
- A 的 12 份 fixtures 与 B 的 8 份 Schema、导出脚本和契约测试已通过 PR 集成；3 处参考记录与来源描述符
  不一致已修正，来源标签现在可交叉核验。

## M2/M3 验证进展

- 已实现任务范围过滤、完整事件键去重、整数汇总、分页连续性校验和可定位 Finding。
- 首条纵向切片得到 `110000`、`FAIL` 和两项 Finding。
- 对抗性测试复现并修复了完整来源事件集合不一致、同一区块哈希冲突两类误判 PASS；两者现在返回 INCONCLUSIVE。
- 严格联调入口 `python -m pytest tests/verification/test_m1_fixtures.py --m1-fixtures fixtures/m1`
  已实际运行，12 份 fixtures 的金额、数量、三态结果、Finding、规则和事件键全部匹配。
- 全量测试 97 项通过、5 项因外部配置缺失而跳过；fixture Schema 校验、Ruff 与 pip check 均通过。
- 已实现拒绝 `float` 的 canonical JSON、SHA-256 稳定哈希及 TaskSpec、ServiceSubmission、Receipt 校验函数。
- 已实现团队控制服务 A/B 端口、EVM 签名恢复校验和独立故障注入元数据，模拟故障不混入参考来源。
- 已实现 SQLite task/attempt/verification 分表留档与状态机；attempt 只追加，最多一次补交，签名失败不消耗 attempt。
- 无 UI 编排已跑通首次遗漏导致 `FAIL`、同服务补交或切换服务后 `PASS`，两个 attempt 均可分别读取。
- 已实现 ReceiptBuilder、本地只创建不覆盖的 JSON 存储和独立进程重放；FAIL/PASS attempt 分别生成不同哈希，
  重放会校验回执哈希、任务哈希、对象链接并重新推导三态结果。
- 已增加最小 GitHub Actions 配置：普通 CI 执行非 external pytest、Ruff、pip check；外部探针不伪装成功。
- 当前全量本地测试为 107 项通过、5 项因外部配置缺失而明确跳过；Ruff 与 pip check 通过。

## M4 AI 编排进展

- 已实现 `TaskSpecCandidate`、`ClaimExtraction`、`FollowUpAdvice` 和 `ResultExplanation` 严格 Pydantic 契约，
  并新增 4 份可重复生成的 JSON Schema；缺失字段、歧义、重复主张类型和非规范金额在候选边界拒绝。
- 已实现无工具 `StructuredOutputPort`、`RestrictedAIService`、LangChain OpenAI adapter 与 DeepSeek
  OpenAI-compatible Responses adapter；核心 models、verification、storage 和 receipts 不依赖供应商 SDK。
- 任务 ID、确认时间和 `spec_hash` 只由确定性代码生成；VerificationPlan 必须完整命中白名单并逐项绑定已确认任务。
- 补查建议仅允许封闭动作枚举；结果解释必须保持确定性 outcome、金额、数量、Finding ID 和证据引用。
- 离线测试覆盖 prompt injection、未知操作、参数漂移、缺失检查、歧义任务、冲突主张以及金额/结论篡改。
- `deepseek-flash` 真实 external 探针已返回并通过 schema 校验；凭据仅保存在被 Git 忽略的本机 `.env`。
- OpenAI external 探针因缺少 `OPENAI_API_KEY` 和固定 `OPENAI_MODEL` 明确阻塞，没有用 mock 冒充实测。
- 删除临时凭据后的全量质量门为 128 项通过、7 项 external 因当前配置缺失而明确跳过；DeepSeek 探针另有此前
  单独执行的 1 项真实通过记录。Ruff、pip check、12 份 Schema 重生成检查和 1000 行限制均通过。

## M5 Streamlit 页面进展

- 已实现自然语言任务入口、候选缺失/歧义展示、可修改字段、显式确认与不可变 `spec_hash`；任务未确认前页面不提供执行入口。
- 页面只调用 `M5Workflow` 与稳定端口，不直接依赖供应商 SDK、SQLite 表或验证内部实现；AI 主张/计划校验失败会撤销请求且
  不消耗 attempt。
- 已串联团队控制服务 A/B、确定性三态验证、金额、Finding、受限解释/补查、本地回执预览，以及一次补交或换源；attempt 1/2
  分别展示和留档，后一次不会覆盖前一次。
- 缺少模型密钥时默认使用明确标注的离线 fixture 演示，不冒充真实模型调用；OpenAI/DeepSeek 选项会显示缺少 key/固定模型名
  的配置阻塞。
- 页面明确区分服务交付 `SUBMITTED` 与公共发布 `NOT_SUBMITTED`；M5 不执行公开上传、ERC-8004 写入或 M6 发布动作。
- 桌面 1440×1000 浏览器检查确认任务编辑采用双列；移动 390×844 检查确认关键水平容器折叠为单列、页面
  `scrollWidth=innerWidth=390`，长地址、Finding、attempt、回执与按钮均可读可操作。
- M5 AppTest 实际走通未确认拒绝、attempt 1 `FAIL`、attempt 2 `PASS`，两个结果同时保留；M5 收尾复核的
  非 external 质量门为 140 项通过、8 项 external 明确排除，Ruff、pip check 和 1000 行限制均通过。
- 已实现真实 `RpcReferenceEvidenceProvider`：校验 chain ID 与确认数、连续分页读取完整区块范围、保留整数与完整事件键；
  RPC 失败、缺页或未确认范围返回 `INCONCLUSIVE`。Blockscout 仅作可选补充抽样，未配置时明确显示 RPC-only。
- 真实组合 external 探针已使用 DeepSeek、Sepolia RPC 与 Blockscout 跑通候选生成、服务 A 漏项 `FAIL`、切换服务 B
  `PASS`、合法受限 AI 产物和两个独立回执；目标区块读取 1 页、6 条 RPC 原始事件，Blockscout 对真实交易完成补充抽样。
- 真实浏览器复跑得到同样的 `FAIL → PASS`，两个 attempt 均展示 RPC `COMPLETE` 与 Blockscout `SAMPLED`；重启 Streamlit
  后输入相同工作区 ID，可从 SQLite 与私有回执恢复已确认任务及两个 attempt，历史 AI 文本不会重新生成。
- 已新增不包含 `.env`、PEM、私有回执和本地数据的容器构建文件；生产容器以非 root 用户运行，SQLite 与私有回执挂载到
  宿主机持久化目录，应用端口不直接发布到公网。
- 广州服务器入口为 `https://creatoros.top/trust-receipt/`，使用 HTTPS；IP 明文入口只执行 HTTPS 重定向。
  Basic Auth 已从仓库和服务器反向代理配置移除；匿名页面与健康检查返回 `200`，WebSocket 握手成功，既有 IP 重定向不受影响。
- 部署服务器已真实调用 DeepSeek 并得到 schema 合法候选，真实 Sepolia RPC 读回固定交易与整数金额。该地域无法直连
  `api.blockscout.com`，现已通过团队 Vercel 中继与自定义域名恢复 Blockscout 补充抽样。
- 生产 Compose 已固定 `APP_REQUIRE_LIVE=true`，线上页面只提供 DeepSeek 真实模型和真实 Sepolia RPC；容器内复验得到
  `deepseek_schema_ok=True`、`rpc_real_ok=True`，且浏览器真实点击已返回由 DeepSeek 生成的缺失字段与澄清问题。
- M5 页面已重构为可用的验收工作台，包含运行信号、结构化步骤、任务摘要、attempt 结果卡和移动端布局；生产反向代理的
  Streamlit 路径级 CSP 已修复。桌面与 390×844 生产浏览器检查通过，移动端 `scrollWidth=innerWidth=390`。
- 固定上游、只转发 GET/POST 且要求 Blockscout Pro Bearer key 的中继已部署至 Vercel，并绑定
  `https://blockscout-relay.creatoros.top`。广州容器实测配置端点 `200`、真实交易端点 `200`、MCP 工具和分页完整性通过；
  产品证据诊断为 RPC `COMPLETE`、Blockscout `SAMPLED`，抽样 1 条记录。
- M5 最终交接复核确认生产应用容器为 `healthy`，Blockscout 容器持续运行，容器内健康端点返回 `ok`。公开入口的
  Basic Auth 已按产品要求移除并完成匿名访问验证。本地同名远端分支尚未同步。

## M6 公共回执与 ERC-8004 进展

- 已实现 `ContentPublisher` 端口、Pinata/IPFS adapter 与隔离目录离线 adapter。公开快照在上传前拒绝私钥、签名、JWT、
  Authorization、API key、secret 和原始报告正文等字段；上传后必须从 gateway 下载精确字节并核对 SHA-256。
- Pinata adapter 已按官方 v3 multipart 协议固定 `network=public`，JWT 只进入 Bearer header。缺少 JWT 时生产使用同一端口下的
  内容寻址 HTTPS fallback：应用只创建公共文件，Nginx 只读公开，并执行相同的公网下载哈希核验；不冒充 IPFS 固定。
- SQLite 新增只追加 `publication_events`，保存 `NOT_SUBMITTED / SUBMITTED / CONFIRMED / FAILED` 全部快照；进程重启按
  receipt ID 恢复最新状态，旧状态不覆盖。
- ERC-8004 产品 adapter 在写入前核对 Sepolia chain ID、受控 service owner、Reviewer、余额和 pending nonce；直接绑定公共
  URI 与内容 SHA-256。广播只执行一次，超时仍以已签名交易哈希和 nonce 保持 `SUBMITTED`，随后只允许读回，不自动重发。
- 链上确认必须从 `NewFeedback` 事件读回 service、Reviewer、URI、哈希和结果标签一致后才进入 `CONFIRMED`；确定性失败可在
  用户再次授权后从 `FAILED` 恢复为 `NOT_SUBMITTED`，`TRANSACTION_UNKNOWN` 禁止走该恢复路径。
- Streamlit 已接入两次独立授权：先授权公开脱敏 JSON，再授权 Sepolia 写入；页面分别展示公共 URI、内容哈希、nonce、交易哈希、
  feedback index、区块和脱敏错误。新会话可只读公共 JSON，在独立进程校验哈希并重放确定性三态检查。
- M6 HTTPS publisher 已部署到广州服务器；生产应用容器为 `healthy`，匿名页面与健康端点返回 `200`，WebSocket 握手成功，
  应用端口仍仅在 Docker 网络暴露。公共路径只允许 GET/HEAD，POST 实测返回 `403`。
- 已用真实 DeepSeek + Sepolia RPC + Blockscout 生成一份 `PASS` 回执并公开至
  `https://creatoros.top/trust-receipt/public/3b922f5825fe7127c0fa5da6c3664a2e93e7381db49579cc992d85b4292fa26e-receipt-e593dcc8-dc29-4db9-829c-31802a7de630.json`；
  公网下载返回 `200 application/json`，精确字节 SHA-256 为 `0x3b922f…a26e`，独立进程复核 receipt/task/link 与三态重放均有效。
  SQLite 已保存授权发布事件。
- Reviewer 专用测试钱包、0.1 Sepolia ETH、service `11155111:10691` owner 与两份 Registry 合约均已完成真实预检。首次交易
  `0xd8e556abeecdd5cee7b77865cdca5d145770a8dc135cbaee47dd8a03405d5f2d` 仅广播一次并确定性回执失败；诊断确认固定
  350,000 Gas 上限不足（实际消耗 345,000，同调用只读回放成功）。状态已落库为 `FAILED`，未自动重发。
- ERC-8004 adapter 已改为链上估算 Gas 后增加 20%（至少 50,000）缓冲并部署。用户再次明确授权后，系统从 `FAILED`
  恢复并仅广播 nonce 1：交易 `0xbf09156a706ca8a49b18606083cacd2f2d844684a0af60e65602c6167374dad9`
  已在区块 11860021 确认，feedback index 为 1，Gas 732,373 / 895,600。
- 独立进程已复核交易成功、数据库 `CONFIRMED`、Service ID、Reviewer、PASS 值、双标签、公共 URI、内容哈希、nonce、区块和
  feedback index 全部一致；公网重新下载哈希亦一致。生产应用健康，持久化 `M6_ENABLE_WRITES=false` 已恢复。

## M7 验收封装进展

- 新增无凭据演示入口 `scripts/run_mvp_demo.py`：真实执行离线 fixture 的服务 A `FAIL`、切换服务 B `PASS`、两个 attempt
  追加留档、两份回执独立重放及进程恢复；输出显式标记 `publication_mode=not-executed`，不冒充 M6 外部验收。
- README 与运维手册已补齐一条命令演示和完整质量门；CI 新增 Schema 漂移、1000 物理行限制及演示执行。
- 新增治理测试，机械校验根目录 Markdown metadata、`doc-id` 唯一性和本地链接；修正旧文档中已过期的 CI、Blockscout、
  Pinata fallback 与 M6 页面说明。
- 完整 `pytest` 在临时注入公开 Agent0/ERC 读参数并启动隔离 Blockscout MCP 后为 158 项通过、1 项跳过；唯一跳过项是
  非 MVP 必需且未配置的 OpenAI 探针。非 external 门为 151 项通过；Ruff、主/Blockscout 环境 `pip check`、12 份 Schema
  漂移检查、1000 行限制和无凭据演示均通过。
- 生产匿名页面与健康端点返回 `200`，无 Basic Auth header；公共回执返回 `200` 且 SHA-256 仍为 `0x3b922f…a26e`。
  应用容器 `healthy`，持久化 `M6_ENABLE_WRITES=false`。

## 待外部配置验证

- Pinata/IPFS 是优先 adapter，但当前缺少 `PINATA_JWT`；MVP 已按计划使用真实 HTTPS 公共文件 fallback 完成发布验收。

## 后续阶段外部配置待办

- 可选配置 `OPENAI_API_KEY` 与固定 `OPENAI_MODEL`；MVP 生产路径使用已实测 DeepSeek，不受此项阻塞。
- 可选配置 `PINATA_JWT` 以验证 IPFS pinning adapter；MVP 已使用真实 HTTPS 内容寻址公共发布完成验收。

## 已知问题

- Docker Desktop 4.79.0 当前无法启动，自动升级在管理员阶段失败。Blockscout MCP 本地 Python 运行方案已绕过该问题，Docker 不阻塞 MVP。
- ERC-8004 上游参考仓库存在 npm peer dependency 冲突，安装需 `--legacy-peer-deps`。
- 上游 npm 审计报告 35 个依赖漏洞；该仓库当前仅作参考和合约测试，没有执行自动修复。
- GitHub Actions 仅覆盖无需密钥的本地质量门；真实 external 探针仍需显式配置后单独执行。
- Pytest 当前有一条来自第三方 `websockets.legacy` 的弃用 warning；不影响测试结果，后续依赖升级时处理。
- 广州机房仍无法直接连接 Blockscout Pro API；加密 DNS 能得到正确地址，但目标 SNI/TLS 被重置。生产已通过受认证的
  Vercel 中继解决，RPC 仍是完整性权威源，Blockscout 继续只承担补充抽样。

## 下一步

M8 分支完成本地功能补齐与质量门后提交交接，主负责人审查合并并与 M9/M10 组件集成。
专用最小锚只交付未部署候选；真实部署、生产接入与写链仍需额外审查和明确授权。

## M8 开发分支进展

- 页面已重构为黑金 12px 卡片主题和“上传报表 → 确认范围 → 链上核验”主流程，结果优先展示服务声称、链上有效金额、
  精确差异、资金流与 Finding；RPC、签名、Registry 和原始 JSON 默认折叠。
- `FundFlowProjection` 从已有 submission、reference evidence 与 Finding 投影匹配、漏报、链上未找到、内部互转、重复和
  证据不足；每条边保留完整事件键、双方来源引用与 Finding ID，不反向计算 outcome。
- `TaskCommitment` 与 `DeliveryCommitment` 使用 EIP-712；服务接单和交付分别签名，篡改 task/service/attempt/report hash
  或错误签名者会被拒绝。三个 M8 Schema 已加入稳定导出。
- Sepolia 只读探针已真实读取 Validation Registry 的 bytecode、Identity Registry 关联与 service `11155111:10691` 请求列表。
  当前接口不适合作为 requester 通用任务锚，因此未广播交易，页面明确显示 `NOT_SUBMITTED`。
- 非 external 全量门为 158 项通过、9 项排除；M8 Sepolia 只读 external 探针单独 1 项通过。Ruff、pip check、15 份 Schema
  漂移、1000 行限制与无凭据 MVP 演示均通过。真实浏览器走通首次 FAIL 资金流，390×844 下无页面水平溢出。

## M8–M10 计划范围

### M8 补齐与视觉收敛

- 严格 UTF-8 JSON 上传现在是实际核验对象，不再仅作为提示词。原始字节内容寻址私有留档，原金额/count/事件声明不改写；
  本地 intake 签名明确不认证原作者。固定错误报表 FAIL、补交完整报表 PASS、第三次提交拒绝的路径已通过测试。
- 接单在交付生成前签名，绑定完整 task commitment digest、spec hash 和微秒时间戳。M8 SQLite artifacts 只追加保存承诺与
  reference evidence，重启恢复须验证签名、receipt manifest 并重放同一确定性结果；篡改证据拒绝恢复，缺少旧快照不伪造图。
- SVG 有向账户图与事件明细保留双方原始记录；字段不一致、范围错误不再误标成“链上未找到”。12 个冻结 fixture 的投影矩阵通过。
- `.streamlit/config.toml` 与页面 CSS 统一深色，移除说明文字原生 60% 透明度和大面积白底。正文/辅助/说明文字与三个背景
  对比度均超过 7:1；普通卡片/指标/折叠区不描边，状态装饰统一中性灰，强调靠结论层级、行动含义和独立金额分组。
- `CommitmentAnchor.sol` 候选与只读 `DedicatedAnchorReader` 已提供；Solidity 0.8.30 编译和 loopback 开发链 1337 模拟执行通过，
  覆盖 requester 命名空间防占位、服务授权、只追加两次交付与事件读回。没有真实部署、没有 Sepolia 写链，也未接入生产页面。
- 实际上传文件的浏览器路径已走通 FAIL → 补交 → PASS；进程重启后通过原 workspace ID 恢复两份签名、证据与图。
  真实 Sepolia Validation Registry 只读探针单独 1 项通过（进程内补充公开 Registry 地址与 agent ID，未修改 `.env`）。
- 专用锚候选不等于独立安全审查通过；真实委托方/外部服务作者认证、专用锚部署和外部写入验收仍未完成，不能称全量链上闭环。
- 根据用户后续视觉要求：添加本地静态区块/节点/链式连接背景、炭黑层次与轻微材质光影；金色集中在主操作，强调用字号、
  字重与独立分组。运行参数只保留折叠区，不再重复为三张气泡；流程序号只保留顶部一套。原 TR 占位与 favicon 已换为
  用户最新提供的透明 PNG Logo，原图无修改。390px 输入页实测无水平溢出、无大块白底；说明文字 opacity=1。
- 字号按用户要求收敛到 `12/14/16/20/24px` 五级角色 token，自定义 HTML 与原生组件共用；页面标题、结论和关键金额不再使用
  32px/约 29px。SVG 固定 720px 画布，窄屏局部滚动，避免容器缩放改变 12px 节点文字。
  `FRONTEND_SPEC.md` 清理字体、描边、状态配色、材质和旧 TR 占位的矛盾表述；纳入用户五张 H5 参考图的组件取舍。
  `TEST_PLAN.md` 增加实际计算字号与视觉回归规则，设计规范不复制瞬时进展。
- 本次浏览器输入页实测 `1440×1000` 与 `390×844`：可见文字计算字号均在五级集合内，无页面级水平溢出。
  本次未完成结果页、760px 两侧及 200% 放大的完整视觉复验，不把自动测试视作全部前端验收。
- 参考图已落实到 M8 页面：深灰双层输入/确认/执行面板、短金色标题底衬与结论光泽、桌面原 logo 材质展示、
  香槟金细斜纹、12 条金色曲线与暖金区块链几何；移动端隐藏纯装饰 logo。正文与状态不普遍染金，不增加卡片外框。
  1440px 桌面与 390px 手机输入页截图已检查；手机计算字号无越界，页面无水平溢出。
  Dockerfile 已补齐原生主题配置复制，避免生产镜像缺少深色控件主题。本次提交、推送、合并与部署仅针对 M8，不包含 M9/M10 分支。
- 最新非 external 门 207 项通过、9 项排除；Ruff、pip check、16 份 Schema、1000 行限制和无凭据演示通过。
  实际链上只有前述只读 Registry 探针；本地模拟合约交易不计作 Sepolia 外部写入验收。

- M8：资金流对账图、任务/接单/交付承诺和可下钻链上证据；技术详情默认折叠，每个状态只有一个主操作。
- M9：确认 Finding 生成返工包、修复前后并排对比、只追加回执版本链和独立公开验证入口。
- M10：按任务类型聚合可追溯的服务历史事实，并用于下一次人工选择服务；不生成永久综合评分。
- 黑客松阶段明确不建设多租户、复杂账号/RBAC、计费、开放市场、自动付款或主网资金控制。

## M8 发布与部署

- 2026-10-07：M8 代码提交 `484f941` 已推送；[PR #6](https://github.com/CH-ZHOU-0512/xinjv/pull/6)
  合并为 `821bbc228e68beccbd1c761e15cfc631b6225d37`，分支与主线 CI 均通过。未合并或修改 M9/M10 独立分支。
- 广州 `/opt/trust-receipt` 应用已切换为 `trust-receipt:m8-821bbc2`，镜像 revision label 与合并提交一致。
  仅重建应用容器；Blockscout、Nginx 与其他应用不重建。原 `.env`、数据与私有/公共回执挂载保持不变。
- 全量构建下载过慢且会重新选择依赖，已停止该构建容器。最终镜像使用已备份运行层、本次 M8 纯 Python wheel 和静态页面源码，
  离线强制安装 M8 包，并把 langchain-core/openai/types-requests 对齐到已测试锁定版本；未修改依赖锁文件。
  发布源码 tar 与 M8 wheel 的 SHA-256 已校验；镜像 `pip check`、M8 主题/模型 smoke、无网络 FAIL→PASS 与回执重放通过。
- 公网 [应用入口](https://creatoros.top/trust-receipt/) 与健康端点均为 200；WebSocket 握手通过。
  生产配置隔离启动通过，页面只提供真实 DeepSeek 与 Sepolia RPC。线上桌面与 390px 手机输入页截图已检查，
  手机可见文字计算字号均在五级集合内，无页面水平溢出。结果页、760px 两侧与 200% 放大仍未完成完整视觉复验。
- 回滚保留 `trust-receipt:m8-rollback-484f941` 镜像及
  `/opt/trust-receipt-backups/m8-before-484f941/source.tar.gz`；备份目录仅 root 可访问。
  本次没有真实链锚部署、写链或公开回执上传；网页部署不等于全量链上闭环完成。

## M7 工作区收尾

- 已按用户明确授权删除 M7/M6 临时诊断文件、浏览器与测试缓存、代码图缓存以及本地 SSH PEM；`.env`、SQLite 数据、
  私有回执和已核验公共回执继续保留，未进入 Git。
- 已移除两个已合并或补丁等价的辅助 worktree，并删除对应本地功能分支；只保留 `main` 与当前交付分支。
- 收尾后重新执行非 external 测试：151 项通过、8 项排除；Ruff、两个 Python 环境 `pip check`、Schema 漂移检查、
  1000 行限制和无凭据演示均通过。
- 主线首次 CI 暴露未使用的 `langchain[mcp]` extra 与固定 `mcp==1.26.0` 的解析冲突；依赖声明已收窄为普通
  LangChain，并使用现有锁定快照约束 CI 解析，避免无界回溯。
- 修复提交对应的 GitHub Actions 主线 CI 已通过，依赖安装、非 external 测试、Ruff、`pip check`、Schema、
  文件规模检查和无凭据演示均为绿色。

## M11–M14 并行启动

- 用户已授权各工作包独立开发，并进一步授权 M9–M14 自动跨会话沟通，由当前会话主控。最终交付仍须集成验收，不能以分支完成替代。
- 共同计划基线使用 `codex/m11-m14-planning`；A `codex/m11-real-case`，B `codex/m12-user-experience`，
  C `codex/m13-demo-verification`，D `codex/m14-user-trial-prep`。各线使用隔离工作区，不修改他人分支；M12 可本地合入已提交 M10/M9/M11。
- A 拥有案例与预检脚本，B 拥有页面与前端测试，C 拥有路演检查与端到端测试，D 拥有用户就绪验收材料。
  根目录权威文档与公共 wiring 由当前集成会话统一维护，各线提交专属交接材料供同步。
- 本次授权不包含公开发布、写链或部署；最终交付没有真实用户及真实测试用户，取消招募依赖。
  四个会话均已发送纠正任务，D 改为自助说明、验收矩阵与证据模板；历史分支/目录名保留，不代表真实试用。
  六个会话已接收恢复协调并回复主控；Skill/MCP 已列 M15/M16 候选，尚未启动实施。
- 四个会话与隔离工作区已创建并下发实施任务；各线从计划基线 `f66b5ad` 开始，尚不代表实现完成。

| 工作包 | 会话 ID | 隔离工作区（C:/Users/Gzhou/.codex/worktrees/ 下） | 交接材料 |
|---|---|---|---|
| A / M11 | `01a1152f-1458-7be0-8b8e-118d6d65a267` | `m11-real-case/HACKTHON` | `docs/handoffs/m11.md` |
| B / M12 | `01a1152f-1b59-7463-b967-58a294bafb1c` | `m12-user-experience/HACKTHON` | `docs/handoffs/m12.md` |
| C / M13 | `01a1152f-2336-7f21-b642-f4268353aebe` | `m13-demo-verification/HACKTHON` | `docs/handoffs/m13.md` |
| D / M14 | `01a1152f-2e06-7a02-8058-c27324c81425` | `m14-user-trial-prep/HACKTHON` | `docs/handoffs/m14.md` |

### M9–M14 恢复协调快照（2026-10-07）

- M9 `30c13c3` 与 M10 `654b2e0` 已本地交付；专属接口交接分别提交 `8f07a13` 与 `e747493`，主控已核实为仅新增 handoff。
  M10 已含 M9，未合并 main 或部署；分支报告的专项验证不代表本轮主控重跑。
- M11 第二组永久独立输入已提交 `4e19c36`，范围/账户/金额不同于固定案例；实时只读结果及交接已发送给消费者。
- M12 已提交干净本地合流基线 `a739551`，包含 M9/M10、M11 两组输入及页面接线；主控已将精确 SHA 发给 M13/M14。
  分支报告非 external 294 通过、13 排除及 M11 RPC 外部 4 通过；不是主控重跑记录，图投影已知问题仍待修复。
- M13 已提交 `377a243`，恢复新的隔离本地自动化，等待 M12 精确合流提交以执行三轮排练；不触碰用户手动标签页。
- M14 `9473928` 已交付验收材料，恢复可执行矩阵实现；正式 14 项就绪验收尚未通过。
- 主控保留 M9 公开历史包的 ADR-023，将计划与无用户验收决定分别重编号 ADR-024/025，避免本地合流重复编号。
- 六条线仍不能宣称整体完成；最终缺口为真实页面联调、三轮排练、完整就绪矩阵及修复复测。
- M12 实时页面联调发现投影范围缺陷：同区块六条 RPC 原始事件中仅一条符合任务，但图把另外五条范围外事件误标为漏报。
  金额与确定性结论未见受影响。M10 最小修复已提交 `f09b57c`（仅核心投影与专属范围测试），分支复现边数 6→1、金额及 outcome 不变。
  分支报告新增测试与既有 fixture 矩阵共 26 通过；主控核实提交范围并交 M12/M13/M14 消费，最终浏览器图语义仍须重验。
  主控另在 M10 隔离工作区实际执行 `pytest tests/m10/test_projection_scope.py tests/m8/test_fund_flow.py -q`，26 通过、1 条第三方弃用 warning。
- M13 合入整条 M10 遇权威文档冲突，已报告将退出该试合并；改等 M12 干净合流提交，后续只消费最小修复，避免循环合并。
- M12 页面增量 `9f1cd85` 修正不同币种/精度无法比较时的差额展示；分支报告真实模型/RPC 浏览器 FAIL→PASS 与双结果响应式检查通过。
- M14 已消费 `a739551` 等依赖，在隔离 8534 执行可执行矩阵；runner 初次输出解析错误已修复，旧失败保留，完整 14 项仍待实测结论。
- M13/M14 已确认消费 `9f1cd85` 与 `f09b57c`；隔离进程分别在 8533/8534 继续浏览器验证，已重启排除热加载旧 import 缓存。
  M14 报告未确认拒绝、作者未认证说明及首屏五视口证据；三轮排练与完整矩阵仍不能记为通过。
- 主控实际读取 `m14-live-04/matrix.json`：UR02/03/05/06/10/11 共六项 PASS，UR04 FAIL，其余七项 BLOCKED，`ready=false`。
  UR02 为第二组自备报表真实 RPC 金额 `321794352786`；UR05 覆盖八类非法上传后合法恢复。UR04 执行器工作区重设修复等待重跑，
  不把定位到脚本原因当作恢复验收通过；结果页、完整键盘、重启及冲突证据仍须补齐。
- M13 转达并在其会话记录确认用户最新要求停止自动操作并收尾；主控已通知 M12/M13/M14 不再追加浏览器/故障注入验证，
  仅保存现有工作和整理交接。M13 报告最新全量测试 313 通过，准确命令及排除项待最终 handoff 核实，不计作主控实跑。
  三轮连续浏览器排练和完整 M14 矩阵尚未确认通过；开发验证可收口，不宣称 M9–M14 全体验收完成，也不要求真实测试用户。
- M13 最终 HEAD `338ff37`，唯一未提交文件为 `scripts/m13/rehearse_browser.py`，主控只读核实并保留；专属交接文档仍含旧阶段说明，
  不能替代本次最终轮次证据。分支报告非 external 313 通过、14 排除、1 条第三方 warning，但原始完整命令未保留，主控不补造。
- M13 先前排练记录为 86.031 秒 PASS / 54.813 秒 FAILED / 84.578 秒 PASS，未形成连续三轮；新排练前两轮报告为
  75.438 秒与 74.906 秒 PASS，第三轮因用户停止而中断，未生成完整 results，不能记为三轮完成。原始文件留在该隔离工作区 `.tmp/`。
  独立页面读取的是此前公开回执，不是当轮新任务回执；当轮未公开发布，测试 bundle 的模拟授权不等于真实公开上传。

## 状态更新规则

- 这里只记录当前事实、下一步和实际阻塞。
- 完成某阶段时更新本文件，不在多个设计文档重复维护进度。
- 每项“已完成”必须能对应文件、命令输出、测试记录或外部交易。
