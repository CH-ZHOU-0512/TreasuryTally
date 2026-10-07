---
doc-id: operations-runbook
title: 本地开发与运行手册
status: active
authority-for:
  - local-setup
  - run-commands
  - troubleshooting
last-reviewed: 2026-10-07
---

# 本地开发与运行手册

## 已准备环境

- 主 Python 3.12 虚拟环境：`D:\HACKTHON\.venv`
- Blockscout MCP 隔离环境：`D:\HACKTHON\.venv-blockscout`
- Node.js/npm：供 ERC-8004 参考合约测试使用
- 上游参考仓库：`D:\HACKTHON\references`

Docker Desktop 当前不可用，但不阻塞开发，因为 Blockscout MCP 已安装到隔离 Python 环境。

## 首次配置

```powershell
cd D:\HACKTHON
Copy-Item .env.example .env
notepad .env
```

需要按开发阶段填写：

```dotenv
OPENAI_API_KEY=
OPENAI_MODEL=
DEEPSEEK_API_KEY=
DEEPSEEK_MODEL=
AI_TIMEOUT_SECONDS=30
AI_MAX_RETRIES=2
BLOCKSCOUT_PRO_API_KEY=
BLOCKSCOUT_MCP_URL=http://127.0.0.1:8000
ETH_RPC_URL=
CHAIN_ID=11155111
RPC_TIMEOUT_SECONDS=30
RPC_CONFIRMATIONS=2
TEST_TOKEN_ADDRESS=
TEST_TRANSFER_TX_HASH=
TEST_FROM_BLOCK=
TEST_TO_BLOCK=
ERC8004_IDENTITY_REGISTRY_ADDRESS=
ERC8004_REPUTATION_REGISTRY_ADDRESS=
ERC8004_VALIDATION_REGISTRY_ADDRESS=
AGENT0_SERVICE_ID=
AGENT0_EXPECTED_OWNER=
ERC8004_FEEDBACK_TX_HASH=
ERC8004_REVIEWER_ADDRESS=
ERC8004_FEEDBACK_INDEX=
M0_ENABLE_WRITES=false
SERVICE_A_PRIVATE_KEY=
SERVICE_B_PRIVATE_KEY=
REVIEWER_PRIVATE_KEY=
PINATA_JWT=
PINATA_API_URL=https://uploads.pinata.cloud/v3/files
PINATA_GATEWAY_URL=https://gateway.pinata.cloud/ipfs
PUBLIC_RECEIPT_DIRECTORY=
PUBLIC_RECEIPT_BASE_URL=
M6_ENABLE_WRITES=false
DATABASE_URL=sqlite:///data/trust_receipt.db
```

所有私钥必须是测试网专用密钥。

`AGENT0_SERVICE_ID` 必须指向团队控制的演示身份，`AGENT0_EXPECTED_OWNER` 用于在探针中强制核对所有者。
已有确认反馈可通过 `ERC8004_FEEDBACK_TX_HASH`、`ERC8004_REVIEWER_ADDRESS` 和
`ERC8004_FEEDBACK_INDEX` 做只读重放，无需再次广播。
ERC-8004 写探针默认关闭；只有完成地址、身份、余额和测试钱包核对后，才临时设置
`M0_ENABLE_WRITES=true`。该探针只提交值为 0、带有 `trust-receipt-m0` 标签的中性测试反馈。

公开合约地址和测试代币地址需与 [INTEGRATIONS.md](INTEGRATIONS.md) 的已核实记录一致；不要从未知来源复制地址。
OpenAI 或 DeepSeek 真实 M4 探针分别要求对应 API key 与固定模型名；只跑离线测试时可以留空。`PINATA_JWT` 留空时
Pinata/IPFS adapter 不可用，但配置完整的 HTTPS 内容寻址 fallback 仍可执行真实公共发布。

M6 缺少 `PINATA_JWT` 且未配置 HTTPS fallback 时，页面明确阻塞公共上传；本地测试仍使用隔离目录 adapter 完整验证脱敏、
上传后哈希核验与新进程重放。
只有核对 Sepolia chain ID、受控 service owner、Reviewer 地址、余额和 pending nonce 后，才可临时设置
`M6_ENABLE_WRITES=true`；页面仍要求二次显式授权。`SUBMITTED` 或广播结果未知时只执行链上读回，不重新点击提交。

生产缺少 Pinata 时可配置内容寻址 HTTPS fallback：应用将 `PUBLIC_RECEIPT_DIRECTORY=/app/receipts/public` 与
`PUBLIC_RECEIPT_BASE_URL=https://creatoros.top/trust-receipt/public` 配对使用。Compose 把宿主机 `receipts/public/` 以可写方式
挂入应用；反向代理必须把同一宿主机目录只读挂到 `/srv/trust-receipt-public`，并使用 `deploy/nginx-location.conf` 的静态规则。
该路径只允许 GET/HEAD、关闭目录列表并固定 JSON 安全头。创建目录时沿用 `receipts/private/` 的容器用户属主，不得使用
world-writable 权限。

## 激活主环境

```powershell
cd D:\HACKTHON
.\.venv\Scripts\Activate.ps1
python -m pip check
```

如 PowerShell 执行策略阻止激活，可直接使用：

```powershell
D:\HACKTHON\.venv\Scripts\python.exe -m pytest
```

## 启动 Blockscout MCP

```powershell
$env:BLOCKSCOUT_PRO_API_KEY="填入密钥"
New-Item -ItemType Directory -Force .tmp | Out-Null
Push-Location .tmp
D:\HACKTHON\.venv-blockscout\Scripts\python.exe `
  -m blockscout_mcp_server `
  --http `
  --http-host 127.0.0.1 `
  --http-port 8000
```

服务停止后执行 `Pop-Location`。必须从 `.tmp/` 启动，避免 Blockscout 自身的设置模型误读项目根目录 `.env`
中的其他配置。该环境与主应用环境必须保持分离。CLI 启动时可能出现来自 `pydantic_settings`
的非致命 warning；只有服务无法监听或工具调用失败才视为启动失败。

## 启动应用

```powershell
.\.venv\Scripts\python.exe -m streamlit run app\streamlit_app.py
```

默认本地数据写入 `data/`，私有回执写入 `receipts/private/`，两者均不提交版本库。

### Linux 容器部署

首屏品牌与 CSS 通过 `st.html` 渲染，Logo eager 请求原生媒体管道生成的 288px PNG 预览，两个位置共用内容寻址资源；不重绘或替换原始品牌 PNG。媒体 URL 保留反向代理的 baseUrlPath 前缀，原始静态 URL 作为无媒体运行时的回退。
部署检查须分别核实标题、CSS、Logo 的实际可见性和加载过程，不把灰色占位或最终截图当作首屏速度证据。

部署不要求真实用户参与；仍须记录版本、质量门与未完成的技术验收。部署授权不自动授权公开回执上传、写链或恢复已暂停的浏览器排练。

若依赖声明与锁定快照完全未变，可复用已验证运行镜像作为基底，以本地构建的纯 Python wheel 执行
`pip install --no-index --no-deps --force-reinstall`，再复制同一提交的 `src/`、`app/`、`fixtures/` 与 `.streamlit/`。
永久配置使用 `deploy/Dockerfile.release`，构建上下文包含源码归档和同源 wheel。页面入口优先导入 `/app/src`，
只更新 wheel 会被旧基镜像源码遮蔽；禁止省略源码同步，也不能通过 PYTHONPATH 绕过验收。
使用 `git archive` 打包已提交源码，传输后校验源码和 wheel 的 SHA-256；镜像必须写入完整
`org.opencontainers.image.revision`，并执行镜像内 `pip check` 和无网络演示。依赖发生变化时不得沿用此快捷路径。
两种 Dockerfile 均在构建期执行 `scripts/deploy/check_image.py`：比较 `/app/src/trust_receipt` 与已安装 wheel 的全部
Python 文件（仅归一化 Git 换行），并用真实 `/app/app/streamlit_app.py` 执行 AppTest，要求零 exception、实际产品标题
及正确源码导入路径。隔离检查不挂生产目录、不注入 `.env`、不提供真实密钥，构建时使用 `--network=none`。
缺外部配置可显示明确阻塞，不可有导入异常。健康端点、HTTP 200、WebSocket 和 `/release` 下演示不能替代真实入口检查。
检查通过 `python -c` 的 runpy 调用从 `/app` 启动，保留生产 `python -m streamlit` 的工作目录导入语义；
不要直接运行位于 `/opt` 的脚本导致脚本目录取代应用根目录，也不另外设置 PYTHONPATH。
切换后只用新独立浏览器会话检查首页渲染及无异常；这不补记业务矩阵或真实用户验收。
切换前保留旧镜像及源码备份，保留 `.env`、data 与私有/公开回执挂载；仅使用
`docker compose ... up -d --no-deps --no-build app` 切换已构建应用镜像，不重建其他容器。

页面 Logo 保持用户原始 PNG，存放于 `app/static/logo.png`；`.streamlit/config.toml` 启用
`server.enableStaticServing` 保留原始静态访问；品牌展示使用兼容 `server.baseUrlPath` 的同源 288px 媒体预览 URL，使浏览器复用资源，避免每次重跑
重复发送大段 base64。OpenAI/Agent0 SDK 仅在对应 adapter 实际使用时加载。生产接入这些改动须经授权重建镜像，
随后检查 `/trust-receipt/app/static/logo.png`、页面实际 `/trust-receipt/media/` 资源、Logo 透明底和 DPR 清晰度及 WebSocket；本地优化不代表生产已经更新。

生产服务器使用 `deploy/docker-compose.prod.yml` 构建两个相互隔离的容器：Streamlit 主应用与
Blockscout MCP。两者只加入既有反向代理网络，不直接向公网发布容器端口；`data/` 和
`receipts/private/` 通过宿主机目录持久化。Compose 固定设置 `APP_REQUIRE_LIVE=true`，因此生产页面只能使用真实
DeepSeek 与真实 Sepolia RPC；缺少任一必要配置时直接阻塞，不会回退 fixture。

```bash
cd /opt/trust-receipt
chmod 600 .env
docker compose -f deploy/docker-compose.prod.yml up -d --build
docker compose -f deploy/docker-compose.prod.yml ps
```

反向代理使用 `deploy/nginx-location.conf` 中的路径规则，入口为 `/trust-receipt/`。规则包含 WebSocket 和长连接，
公开入口不要求 HTTP Basic Auth；明文 HTTP 入口仍必须重定向到 HTTPS。如果 Nginx 配置使用单文件 bind mount，宿主机
原子替换配置后应重建代理容器，使新 inode 被重新挂载。部署后分别检查容器内健康端点、匿名公网入口以及
一次页面 WebSocket 会话。Streamlit 的内联启动脚本和运行时样式需要路径级 CSP 例外；必须使用
`deploy/nginx-location.conf` 中仅限该路径的安全头，不能放宽整个域名。`.env` 和 PEM 私钥不得进入镜像。

若部署地域无法连接 `api.blockscout.com`，清空部署环境的 `BLOCKSCOUT_PRO_API_KEY` 并重建主应用容器，页面会
明确显示 `RPC-only`。此时必须单独验证 `ETH_RPC_URL` 的真实 Sepolia 读取；不得保留已配置提示并让每次操作等待
Blockscout 超时，也不得把 RPC 结果伪装成 Blockscout 抽样成功。

若要恢复受阻地域的 Blockscout 补充抽样，可将 `deploy/blockscout-relay/` 部署到 Vercel，绑定并验证自定义域名后再设置
`BLOCKSCOUT_PRO_API_BASE_URL`。部署完成必须从目标服务器运行真实 MCP 探针；只有返回 `SAMPLED` 后才能重新启用
`BLOCKSCOUT_PRO_API_KEY`。未认领的临时 URL 不得作为生产依赖。

当前生产值为 `BLOCKSCOUT_PRO_API_BASE_URL=https://blockscout-relay.creatoros.top`；DNSPod 的 `blockscout-relay` CNAME
指向 Vercel 提供的项目专用记录。更换域名或部署后应先执行 Vercel 域名验证，再从广州服务器验证配置端点、真实交易端点、
MCP 工具与产品级 `SAMPLED` 诊断，整个过程不得输出 Bearer key。

本地首次启动默认进入明确标注的离线 fixture 演示，不调用模型网络。切换到 OpenAI 或 DeepSeek 时，必须同时配置对应 API key
和固定模型名；选择“真实 Sepolia RPC”还必须配置 `ETH_RPC_URL`，可用 `RPC_CONFIRMATIONS` 调整确认数。缺少配置会在页面
显示阻塞。工作区 ID 对应独立本地数据库、私有回执目录和运行时生成的无资产签名账户；进程重启后输入同一 ID 可恢复最新任务
及两个 attempt，历史 AI 文本不会重新生成。M6 公共发布和 ERC-8004 写入分别要求页面内显式授权；缺少 publisher 或写链配置
时按钮保持禁用，已发布但尚未写链的回执保持 `NOT_SUBMITTED`。

## 验证

```powershell
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m pip check
.\.venv-blockscout\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe scripts\export_schemas.py --check
.\.venv\Scripts\python.exe scripts\check_file_sizes.py
.\.venv\Scripts\python.exe scripts\run_mvp_demo.py
```

最后一条是无需凭据的 M7 演示：执行服务 A `FAIL`、切换服务 B `PASS`、两个 attempt 持久化、两份回执独立重放和进程恢复。
输出 `"valid": true` 才算成功；其 `publication_mode=not-executed` 明确表示该命令不代替真实 M6 公共发布与写链验收。

M4 离线门槛与真实模型探针分别运行：

```powershell
.\.venv\Scripts\python.exe -m pytest tests\m4
.\.venv\Scripts\python.exe -m pytest tests\external\test_openai_ai_probe.py -m external -v
.\.venv\Scripts\python.exe -m pytest tests\external\test_deepseek_ai_probe.py -m external -v
.\.venv\Scripts\python.exe -m pytest tests\external\test_m5_live_product_probe.py -m external -v
```

外部探针缺少 key、固定模型名或 RPC 配置时会明确 skip。不要把 mock 通过解释为真实模型已连通。项目所有者明确授权继续使用
对话中提供的测试供应商密钥时，只能放入被 Git 忽略的本机 `.env`；不得写入日志、提交、fixture、回执或模型 prompt。

本地回执可在独立进程中校验和重放：

```powershell
.\.venv\Scripts\python.exe -m trust_receipt.receipts.cli path\to\receipt.json
```

命令以 JSON 输出回执哈希、任务哈希、对象链接和三态结果复算状态；任一检查失败时退出码非零。

M9 公开回执验证不读取 SQLite 或私有工作区。可对本地下载的公开 JSON 或 HTTP(S) URI 执行：

```powershell
.\.venv\Scripts\python.exe -m trust_receipt.m9.cli `
  path\to\public-receipt.json `
  --kind RECEIPT_HASH `
  --value 0x<receipt-hash> `
  --attempt 1 `
  --expected-content-hash 0x<published-byte-sha256>
```

`--kind` 还支持 `URI`、`TASK_HASH` 和 `FEEDBACK_TRANSACTION`。单 Receipt attempt 2 必须使用 `--revision`、
`--parent-revision` 和 `--parent-receipt` 提供公开父回执与关系。完整历史包可直接验证最新 attempt：

```powershell
.\.venv\Scripts\python.exe -m trust_receipt.m9.cli public-history.json --bundle --kind URI
```

哈希定位加 `--kind RECEIPT_HASH --value 0x<public-receipt-hash>` 或 `--kind TASK_HASH --value 0x<spec-hash>`。
反馈入口从配置 `ETH_RPC_URL` 和 `ERC8004_REPUTATION_REGISTRY_ADDRESS` 只读真实交易：

```powershell
.\.venv\Scripts\python.exe -m trust_receipt.m9.cli --kind FEEDBACK_TRANSACTION --value 0x<tx-hash> --attempt 2 --public-history public-history.json
```

未提供可验证公开父回执时返回 INCONCLUSIVE；未提供公开承诺时 `commitment_status=UNVERIFIED`。
页面的 `?verify=1` 为独立入口，支持文件、配置公共目录 HTTPS/IPFS 和反馈交易，不需要原工作区或模型密钥。
“分享完整验收历史”分别授权历史导出与公共上传，元数据保存在私有 `public-history/`，恢复后复用已有发布引用。

M0 真实探针使用：

```powershell
.\.venv\Scripts\python.exe -m pytest -m external -v
```

缺少配置时会逐项显示 `blocked by missing configuration` 并跳过。跳过只代表阻塞已被明确报告，不能作为
M0 已连通的证据。

## 参考合约验证

仅在需要复核 ERC-8004 上游合约时运行：

```powershell
cd D:\HACKTHON\references\erc-8004-contracts
$env:SEPOLIA_RPC_URL="http://127.0.0.1:8545"
$env:MAINNET_RPC_URL="http://127.0.0.1:8545"
npx hardhat compile
npm test
```

上游锁文件存在 Hardhat peer dependency 冲突，首次安装使用 `npm ci --legacy-peer-deps`。不要运行 `npm audit fix` 改写参考仓库。

## 常见故障

### Blockscout 工具认证失败

检查当前进程是否实际继承 `BLOCKSCOUT_PRO_API_KEY`；不要通过打印环境变量值来诊断。

### RPC 没有返回事件

依次确认链 ID、代币地址、区块范围、RPC 是否为归档/完整节点，以及查询是否因范围过大被限制。空数组和查询失败必须区分。

### Streamlit 端口占用

```powershell
.\.venv\Scripts\python.exe -m streamlit run app\streamlit_app.py --server.port 8502
```

### Docker Desktop

当前 4.79.0 在本机因旧运行时链接启动失败，自动升级需要管理员步骤。开发默认走本地 Blockscout MCP，不把修复 Docker 作为 MVP 前置条件。

## 清理与恢复

### M8 上传与工作区恢复

上传只接受 `schemas/v1/uploaded_report.schema.json` 对应的 UTF-8 JSON，最多 1 MB、200 条 service 来源记录。
原始文件保存在 `receipts/private/m5/<workspace-id>/uploads/`；不得公开该目录。SQLite 同工作区新增只追加 M8 artifact
表，不存私钥。重启后输入原 workspace ID，系统校验承诺、证据 manifest 并重放结果；上传任务恢复后补交需重新上传文件，
不会静默换成演示服务。缺少旧快照只保留原回执；损坏快照拒绝恢复，不自动覆盖或重拉参考证据。

专用锚候选当前没有部署地址或生产配置；本地编译可用 `npx --yes --package solc@0.8.30 solcjs --bin --abi
contracts/CommitmentAnchor.sol -o .tmp/m8-solc`。不将本地模拟交易当作 Sepolia 已提交或已确认。

可在隔离开发端口启动 `npx --yes --package ganache@7.9.2 ganache --server.host 127.0.0.1 --server.port 18549 --logging.quiet --wallet.deterministic`，
然后运行 `python scripts/check_m8_anchor_local.py`。脚本只允许 loopback HTTP 与开发 chain 1337，使用本地测试币和新生成的
测试身份，校验授权、requester 命名空间、只追加 attempt 和 task/delivery 事件读回；不读取 `.env` 或真实密钥。
Ganache 启动输出中的默认开发密钥不是生产凭据，但日志仍应留在忽略的 `.tmp/`。

页面主题由 `.streamlit/config.toml` 的原生深色主题与 `app/styles.py` 共同控制；不要只修改背景却保留原生浅色主题。
生产 Dockerfile 必须复制 `.streamlit/` 到镜像工作目录；发布需重建应用镜像，不能只刷新浏览器或更新 CSS。
更新导入的样式后重启开发 Streamlit，浏览器刷新并用原 workspace ID 恢复，避免缓存旧样式。

- 不删除 `fixtures/`、`schemas/` 或已发布回执。
- 本地数据库损坏时先复制 `data/` 作为证据，再重建开发数据库。
- 私有回执不得为了“清理”而移动到公开目录。
- 参考仓库如被意外修改，先查看 `git status`，不得使用破坏性重置覆盖未知改动。

## 首步报表转换

入口保留严格 JSON，同时支持 UTF-8（含 BOM）或 GB18030 CSV、仅一个可见工作表的无宏 XLSX。
CSV 支持逗号、分号、制表符；编码与原始字节哈希显示在转换记录中。PDF、截图、旧 XLS、UTF-16 CSV 不支持。
不是任意 Excel 导入器：公式、外部链接、日期及非 General 数值格式、多工作表、超限内容拒绝，不静默抽样。
XLSX 使用有界标准库 ZIP/XML reader，无新增 Excel 依赖；文本支持 inline string、共享字符串及富文本 run。

先查看列映射和缺失字段，可手动补充全表链 ID、代币地址和精度；交易哈希、日志序号、区块、付款/收款地址与金额必须
在原表提供。金额列明确选择最小单位整数或代币单位小数；XLSX 金额及声明总额必须设为文本，科学计数法不能猜回原值。
已有声明总额/笔数即使错误也不改写；缺失时显示由明细计算的转换摘要，需用户明确采用。
完整 JSON 预览通过既有 UploadedReport 校验后，用户确认才交给旧 intake；随后仍要确认核验范围。

原件、规范 JSON、来源记录分别保存在私有目录的 `conversion-originals/`、`conversion-json/`、
`conversion-provenance/`，文件名为内容哈希，来源记录含原文件名、映射、补充字段、警告及两份内容哈希。
保留与正式提交没有跨文件事务；失败可能留下内容寻址的私有孤立文件，但不会自动签名、上传公开文件或覆盖历史交付。
