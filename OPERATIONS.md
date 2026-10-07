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

`--kind` 还支持 `URI`、`TASK_HASH` 和 `FEEDBACK_TRANSACTION`。attempt 2 必须使用 `--revision` 和
`--parent-revision` 提供可验证的 parent/supersedes 关系；反馈交易入口还必须提供独立读回的内容哈希，
否则返回 `INCONCLUSIVE`。未接入 M8 承诺 adapter 时输出 `commitment_status=UNVERIFIED`。

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

- 不删除 `fixtures/`、`schemas/` 或已发布回执。
- 本地数据库损坏时先复制 `data/` 作为证据，再重建开发数据库。
- 私有回执不得为了“清理”而移动到公开目录。
- 参考仓库如被意外修改，先查看 `git status`，不得使用破坏性重置覆盖未知改动。
