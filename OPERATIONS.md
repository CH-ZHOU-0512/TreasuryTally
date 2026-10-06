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
DATABASE_URL=sqlite:///data/trust_receipt.db
```

所有私钥必须是测试网专用密钥。

`AGENT0_SERVICE_ID` 必须指向团队控制的演示身份，`AGENT0_EXPECTED_OWNER` 用于在探针中强制核对所有者。
已有确认反馈可通过 `ERC8004_FEEDBACK_TX_HASH`、`ERC8004_REVIEWER_ADDRESS` 和
`ERC8004_FEEDBACK_INDEX` 做只读重放，无需再次广播。
ERC-8004 写探针默认关闭；只有完成地址、身份、余额和测试钱包核对后，才临时设置
`M0_ENABLE_WRITES=true`。该探针只提交值为 0、带有 `trust-receipt-m0` 标签的中性测试反馈。

公开合约地址和测试代币地址需与 [INTEGRATIONS.md](INTEGRATIONS.md) 的已核实记录一致；不要从未知来源复制地址。
OpenAI 或 DeepSeek 真实 M4 探针分别要求对应 API key 与固定模型名；只跑离线测试时可以留空。`PINATA_JWT` 在 M6 前可以留空。

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

首次启动默认进入明确标注的离线 fixture 演示，不调用模型网络。切换到 OpenAI 或 DeepSeek 时，必须同时配置对应 API key
和固定模型名；选择“真实 Sepolia RPC”还必须配置 `ETH_RPC_URL`，可用 `RPC_CONFIRMATIONS` 调整确认数。缺少配置会在页面
显示阻塞。工作区 ID 对应独立本地数据库、私有回执目录和运行时生成的无资产签名账户；进程重启后输入同一 ID 可恢复最新任务
及两个 attempt，历史 AI 文本不会重新生成。页面不会执行公共上传、ERC-8004 写入或其他 M6 动作，回执 publication 状态保持
`NOT_SUBMITTED`。

## 验证

```powershell
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m pip check
.\.venv-blockscout\Scripts\python.exe -m pip check
Get-ChildItem -Recurse -File -Include *.py,*.toml,*.json,*.yaml,*.yml | `
  Where-Object { $_.FullName -notmatch '\\(\.venv|\.venv-blockscout|references|\.tmp)\\' } | `
  ForEach-Object { if ((Get-Content -LiteralPath $_.FullName).Count -gt 1000) { $_.FullName } }
```

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
