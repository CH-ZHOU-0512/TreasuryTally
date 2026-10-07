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

### 自动上传与单一业务报告页面（2026-10-07，本地联调中，未发布）

M12 从 `9fd663c` 消费 M14 自动识别三组核心/记录和有界外部测试提交，取代未发布的手工映射/采用 JSON 入口。
正常 CSV/.xlsx/JSON 上传后自动读取；仅必要链/资产/精度/金额单位局部询问，首步和修正版共用组件。
文件/模型/局部条件变化清旧结果与服务；失败不回退旧报表，范围确认和主动核验仍必需。
`6068b83` 视觉集成版本完整非 external 实跑 554 passed / 16 deselected / 1 既有 warning，Ruff、pip check、21 Schema、1000 行门通过。
新 UI/缓存 13 项、原值/私有留档入口 8 项及全页自动修正版 3 项均通过；XLSX 合法金额和公式替换阻塞使用显式模型 double。
本地浏览器实际选 CSV 验证未配真实识别模型的阻塞；严格 JSON 无采纳步骤直接摘要，明确确认范围、主动首轮 FAIL，
自动读取 JSON 修正版但不自动核验，主动第二轮 PASS 保留原失败、无第三次入口；390px 无页面横向溢出、exception 0。

结果报告按 ADR-033 由 M13 reporting 视图驱动：消费 `4b91d0b`、`8b46ec9`、`e6097c0`，不另造报告/金额模型。
默认三项正常单位金额、中文结论/范围、同类差异概览及两次业务对比；AI 原文/签名/诊断/JSON 集中一个技术入口。
错误或混合资产/精度不猜换算，冷恢复不借当前模式冒充原核验；报告公开授权按回执身份隔离。
消费 M13 ECharts `6a7c79d`（本地 `25d6049`），默认本地隔离 iframe 图、12 条显式分页、前后切换、文字图例已接入；
完整事件正常单位表放在单一技术入口。4 项新增 AppTest 证明全部 200 条逐页可达、原失败保留、缺图不补造，
消费 M13 `005b1a9`（本地 `fc66134`），正常可比金额差异说明使用精确代币单位，未知/冲突不猜换算，下一步移除内部工作流术语。
消费 M13 `677e5b0`（本地 `c28cffd`），事件仅在任务资产、唯一参考精度与事件精度一致时换算，
否则保留整数最小单位并标「精度未确认」。reporting/报告/图控件组合 60 项通过；既有无凭据演示双回执重放/恢复 valid=true。
用户暂停浏览器自动操作，本次接图后未调用浏览器或声称视觉验收；手机可读性与真实交互留待人工检查。
Word/PDF 逐页验收及接线尚未完成；不能称整版报告或导出完成。
用户随后取消 Canva、明确继续 ECharts；仅消费 M13 `5b939ed` 的三个实现/测试文件和 `3602720` 横向箭头修复，
不取其状态或 dirty 导出。动态图显示角色卡片、20px 金额/12px 状态，长标签省略但完整事实保留，720px 图内滚动。
随后消费标签小修 `ef481e1`（本地 `0a2551e`），长单位指向完整明细，未知精度始终明确标「最小单位（精度未确认）」，
内部互转标签进一步避开卡片；新增实际错误资产 fixture 的可见标签/原整数/完整来源测试。
最新报告/图控件组合 61 项、Ruff/21 Schema/1000 行/diff 通过，本次小修未重跑全量，不把前次 554 计作新增测试后的全量。
继续消费 `e68cd25`（本地 `aa40d9f`）的两行避让/单位文案修复，61 项回归、Ruff/1000 行/diff 再次通过。
该提交不包含「最多前 4」或「并行线仅 1 标签」的逻辑；未将这些尚未交接规则记作网页已实现，仍保持 12 条显式分页。
实际查看更新的离线合成 PNG，确认横向箭头不再被卡片覆盖；不是浏览器/触摸/生产验收，未把 PNG 或此前 imagegen 草案嵌入任务。
固定 Node/ECharts SSR + pinned sharp 的导出方案已批准并写入 ADR-033，renderer/依赖/运行环境等待各负责人已验提交，
不把方案批准当实现或逐页检查成功；Word/PDF 仍待接线和验收，不回退 Python 仿制图。
旧 ADR-031 各项验收为历史事实，不发布旧交互。
未自行追加真实模型/RPC 调用、真人测试、线上工作区恢复、公共上传/写链、推送、合并或部署；M14 外部识别实跑归属见下项。

### 统一上传与受限模型识别（2026-10-07，本地核心，未发布）

用户最新需求替代旧转换/采纳界面：正常路径统一 CSV / `.xlsx` / JSON 上传，模型只识别表头，
用户不手动转换或采纳 JSON。旧 `9fd663c` 手动界面不发布；下面 ADR-031 各项作为历史本地证据保留。
M14 从 `9fd663c` 切 `codex/automatic-report-recognition`，单写受限核心与技术文档；
M12 从同一基线独立单写 app/PRODUCT/FRONTEND/ADR-032；核心提交已交接，最终页面接线仍由 M12 完成。
核心 `header_recognition` / `report_recognition` 已实现安全表头、真实列绑定、严格 JSON bypass、
单位/整表条件局部问题、原声明不修正、失败脱敏/无 fixture fallback、自动私有留档与缓存原件/模型绑定。
没有模型行值、文件名、私有备注外发，没有新增依赖或修改公共 Schema/签名/金额/attempt 规则。
核心提交为 `f275825902ad3058f644b6139dab3e9234fc7a6c` 与增量
`ac2015f5c0f96bd227698f2b7f1f55c39a3a755e`，新增 35 项离线 mock 识别测试通过；
最终完整非 external 门实际完成 490 passed / 14 deselected / 1 条既有 websockets warning。
全仓 Ruff、主环境 pip check、21 Schema 重生成检查、1000 物理行限制与 diff check 通过。
随后有界真实验收使用既有被忽略配置的固定 `DeepSeek:deepseek-flash`，实际 factory/provider/
recognize_report 路径的 2 项 external 测试通过（1 条既有 warning）；请求超时上限 30 秒、自动重试 0。
只发送合成业务表头及索引，不发送文件名、行值、金额、地址、哈希、备注或用户文件，没有切换供应商。
正常 CSV 用时 3.469 秒，API/Schema/真实列绑定通过、ready=true；缺金额单位 CSV 用时 2.375 秒，
API/Schema/绑定通过，ready=false 且仅提示 `amount_unit`，本地补充 base 后缓存复用 ready=true、无第三次请求。
脱敏列绑定：0 chain_id、1 token_address、2 transaction_hash、3 log_index、4 block_number、
5 from_address、6 to_address、7 amount_base_units（缺单位案例为 amount）、8 token_decimals、
9 claimed_total_base_units、10 claimed_count；schema_version=1.0、所有 ambiguous=false、无 issues/missing_fields。
只证明这两个合成 CSV 场景的模型识别，不代表完整业务、RPC、真实 XLSX/API 失败场景或生产页面已验收。
未推送、主线合并、部署或操作用户任务。

### 表格转换独立集成验收（2026-10-07，本地通过，未发布）

M14 新建 `m14-report-conversion-integration/HACKTHON`、`codex/report-conversion-integration`，
实际重试 fetch 核实 `origin/main=e2cfbe24d0e95999057870433956e97310694928`；整条分支 fast-forward 至
M12 `2c645ba067c47b28679a3d4754f7111965a830b0`，没有重复摘取转换核心。仅补充 M14 的 STATUS-only
`095040e` 证据（本地映射 `ef3df38`）、恢复/私有来源集成测试及 TEST_PLAN/本状态记录，不改 app。
M12 浏览器证据属于下项负责人实测；不写成 M14 重做了完整浏览器矩阵。

- M14 独立全量非 external：455 passed / 14 deselected / 1 条既有第三方 warning（包括新增 1 项转换恢复测试）。
  全仓 Ruff、主环境 pip check、21 Schema 可复现、1000 物理行和 diff check 通过。
  无凭据 MVP 演示 FAIL→PASS、两份回执重放与新会话恢复 valid=true。
- 同源归档/wheel 的隔离 Linux 镜像构建门及独立 `--network none` 运行门通过：101 个源码文件匹配安装 wheel，
  实际入口导入 `/app/src/trust_receipt`、页面 exception 0、TreasuryTally 产品区存在。没有生产环境、真实密钥或用户数据挂载。
  该门只证明真实初始页面可运行，不代表外部核验或生产部署。
- 额外 Linux 测试使用只读测试源码挂载：21 项转换 UI 加 1 项恢复/私有来源测试全部通过。
  首次挂载包含 Windows 字节码缓存，导致 11 项 inspect 源路径失败；容器独立缓存并原样重跑后 22 passed。
  不跳过失败断言，不将缓存问题改成应用修复。
- 新增测试证明采纳不创建任务/attempt，原声明和 local-upload-intake 身份保留；新 workflow 从持久化证据与签名恢复，
  不重新取证。原 CSV 私有备注、文件名及转换 provenance 不进入本地构造的授权公开包；未授权导出拒绝。
  只测试序列化，不调用 publisher 或写链。
- 审查未发现阻断本地合流的新增问题。私有输入使用内容哈希文件名，位于工作区 `receipts/private/.../uploads`，
  不在 `app/static` 或公共回执目录；签名、Receipt/Schema、发布器、确定性规则和品牌资产与基线无差异。
  confirmed 参数不是授权令牌，provenance 不是原作者签名；跨文件留档非事务，失败可能留下私有孤立文件。
  原型不提供多租户访问控制，不适合真实敏感报表；这些限制没有因转换入口而解除。
- 未进行真实模型/RPC/外部服务核验、真人测试、线上任务恢复、760px 两侧/原生 200% 全状态视觉矩阵，
  未推送、合并 main、部署、公开上传或写链；生产仍保留既有品牌版本。

### 原始报表转换 UI（2026-10-07，本地完成，未部署）

M12 在独立 `m12-report-intake/HACKTHON` 工作树、`codex/report-intake-ui` 分支从已发布主线
`e2cfbe24d0e95999057870433956e97310694928` 开发；不修改有未提交改动的旧主 checkout。
M14 拥有 CSV/XLSX 纯转换核心，M12 唯一写入首次/修正版页面与 PRODUCT/FRONTEND_SPEC/ADR-031。
转换与明确采纳边界已写入设计文档；UI 确认状态按原字节哈希、文件名、映射、共用条件及工作区/入口隔离，
改变输入撤销旧采纳，恢复旧设置也不会自动恢复。已消费 M14 `611523d`、`de776dc`、`dc52a71`，
首步与修正版共用映射、缺失条件、预览和明确采用组件；非法或未采用修正版阻塞执行，不回退旧报表。
本轮实跑非 external 全量 454 passed / 14 deselected / 1 条既有 warning，含 21 项 UI 采纳/修正新增测试；
Ruff、pip check、21 Schema、1000 物理行和 diff 检查通过；离线 MVP 双回执重放通过。
独立本地 8538 浏览器实际上传 CSV/XLSX：CSV 预览、映射失效、原表手机横向容器检查及采用/范围确认后 PASS；XLSX 首次 FAIL、
公式修正版阻塞、合法修正版明确采用后第二次 PASS，保留首次记录且无第三次入口。
缺日志身份、Excel 数字金额和公式实际阻塞；共用链编号由用户明确填写，格式转换不认证作者、不代表 PASS。
1440/390px 输入和结果页无页面横向溢出；完整刷新重开引导，普通 rerun 不重开。
未执行外部服务、真实链上核验、真人可用性测试、用户线上工作区操作、公开上传、写链、推送、main 合并或部署。

### 首步表格转 JSON（2026-10-07，本地实现，未发布）

M14 核心 `611523d`、结构拒绝增量 `de776dc`、有界解压增量 `dc52a718de7e6802cc48c307608b9f65a2205e94`
基于 `e2cfbe2`，支持受限 CSV/单工作表 XLSX 到既有
UploadedReport 的确定性转换候选与确认后私有留档。原始声明、重复行及来源边界不变，不调用 AI/RPC，不创建参考证据。
最终核心实际验证：转换专项 66 passed；全量非 external 433 passed / 14 deselected / 1 条既有 warning；
全仓 ruff、pip check、21 Schema 可复现与 diff check 通过。新增代码与测试的物理行数均低于 1000 行。
核心阶段由 M12 独立接入 UI 并单写 PRODUCT/FRONTEND_SPEC/ADR031；现已完成，界面证据见前项。
未进行真实用户测试、外部网络核验、推送、合并或部署；生产仍是下述品牌版本，不将本地候选称为上线能力。

### TreasuryTally 品牌统一（2026-10-07，已合并并部署）

用户确认产品与品牌名称统一为 `TreasuryTally`。网页标题、品牌文字、Logo 替代文本、README、产品与前端规范、
自助说明、立项材料、包描述及回执 CLI 帮助已修改；受维护主线文本扫描无旧品牌或 AGNET 拼写残留。
兼容性技术标识与历史签名/回执保持不变，边界见 ADR-030；不重命名仓库、生产路径或协议标识。
主控实跑非 external pytest 为 367 passed / 14 deselected / 1 条既有 warning；pip check、21 Schema 与文件规模门通过。
Skill 品牌增量 `1b6e525` 与 MCP 品牌增量 `808ff86` 已由各负责人在独立分支验证；不将其新增实现混入网页发布。
Skill 独立公开仓库品牌同步提交 `be53ac0`，URL 保持不变。

- 品牌提交 `3c6ad8815b0b75fdd3f7c81123f5a43bf471f2bc` 经
  [PR #17](https://github.com/CH-ZHOU-0512/xinjv/pull/17) 合并为 `5fb7f753fb7c72ecd65e68e45e2024c35832c8a0`，
  并完成首次品牌镜像切换。随后主控补充 app 包 docstring，完整品牌提交为
  `935dc82e60d48b2612f04f1c2af00b51efb78059`，经
  [PR #18](https://github.com/CH-ZHOU-0512/xinjv/pull/18) 合并为 `5872c8922a0760035a340c0f46c39dff5d8faad8`，
  两者源码树相同；两次 PR/分支及合并主线 CI 均通过。不是把首次镜像改标为补漏后的源码。
- 当前生产镜像 `trust-receipt:brand-935dc82e60d48b2612f04f1c2af00b51efb78059`，revision 为完整品牌提交，
  image ID `sha256:5357c9fb6562072cf761d8f3306f1883437bd46724edb610e32a7a72bb4c1a01`。
  同源归档/wheel 上传 SHA-256 校验通过；构建、独立无网络运行和切换前真实 `/app` 入口均为
  98 源文件匹配 wheel、exception 0、TreasuryTally 品牌区存在；镜像 pip check 通过。
- 只替换 app，两次切换均核验 `.env` 哈希、三个数据/回执挂载、Blockscout ID/启动时间不变；当前 healthy、公网 health 200/ok，
  `APP_REQUIRE_LIVE=true`、`M6_ENABLE_WRITES=false`。未动 Nginx、用户任务或历史回执，无公开上传/写链。
- 最新回滚 `trust-receipt:brand-rollback-935dc82e60d48b2612f04f1c2af00b51efb78059` 指向前一健康品牌镜像 `brand-3c6ad88…`，
  原业务版本回滚 `trust-receipt:brand-rollback-3c6ad8815b0b75fdd3f7c81123f5a43bf471f2bc` 指向 `ui-002b8e1…`；
  均按旧镜像自身入口门验证，不用新品牌要求否决旧版本。两次源码备份分别在
  `/opt/trust-receipt-backups/brand-935dc82e60d48b2612f04f1c2af00b51efb78059/` 与
  `/opt/trust-receipt-backups/brand-3c6ad8815b0b75fdd3f7c81123f5a43bf471f2bc/`。
- 发布者独立 `m14-brand-release` 在最终镜像切换后刷新并实测 1440×1000 / 390×844 首页：标题与可见品牌为 TreasuryTally，
  Logo alt 为 TreasuryTally Logo，可见页面无旧中文品牌，exception 0、无页面水平溢出，黑金 CSS 就绪；
  名称完整显示。两处 Logo 实际复用 `.../media/fcec295ccbc208d821452279307d79e9.png`，自然宽 288px，
  桌面显示 52/144px、手机 44px/大图按规范隐藏；不能仅由 image_id 更名推断 URL 必变。
  原 PNG SHA-256 仍为 `875de454…0610c`。截图位于发布者工作树忽略目录
  `output/playwright/treasurytally-final-1440.png` 和 `treasurytally-final-390.png`。
- 发布者复跑品牌/文档 4 项通过，补漏 docstring Ruff/diff check 通过；完整 367 项质量门由主控实际执行并由各轮 CI 复验。
  发布浏览器记录包含容器切换期间 WebSocket close 与短暂 502，最终页面与健康恢复；不声称全会话 console 0。
  未做本轮真实核验、上传、用户故障任务恢复或性能改善验证，未纳 M15/M16 实现；原有多状态视觉与冷加载待验收项仍保留。

### 网页集成修复发布（2026-10-07，已合并并部署）

- 用户授权继续发布仅 M9 持久化 attempt 修复与 M12 引导/普通交互整合；不纳入 M15/M16。
  完整分支提交 `002b8e117f24033238cd686c230083a140b33bab` 已经
  [PR #15](https://github.com/CH-ZHOU-0512/xinjv/pull/15) 合并至
  `1153e51cb40831f29f9207eeb25671f3803cb782`，两者源码树完全一致；分支、PR 和合并主线 CI 均通过。
- 广州当前应用镜像为 `trust-receipt:ui-002b8e117f24033238cd686c230083a140b33bab`，revision 与完整源码提交一致，
  image ID 为 `sha256:c630c94f5450d4d474e5da96cf2b8f20b1b3cc1983105e8b69495de286666140`。
  source archive 和纯 Python wheel 上传后 SHA-256 校验通过；构建期、独立无网络运行、切换前均通过真实 `/app` 入口门：
  98 个源码文件与安装 wheel 一致、导入 `/app/src`、首页 exception 0、品牌区存在；依赖未变，镜像 pip check 通过。
- 只重建 app。`.env` 字节哈希、Blockscout 容器 ID/启动时间、三处数据/私有与公开回执挂载前后一致；应用 healthy，
  公网 health 返回 200/ok，`APP_REQUIRE_LIVE=true`、`M6_ENABLE_WRITES=false`。未改 Nginx、Blockscout 或业务开关。
  未删除、解锁或重跑用户 task/attempt/receipt，未新增公开上传、链上交易或合约部署。
- 回滚镜像 `trust-receipt:ui-rollback-002b8e117f24033238cd686c230083a140b33bab` 指向切换前健康的 `recovery-ea8f772…`，
  旧镜像也实际通过隔离入口门；源码备份与旧镜像记录在
  `/opt/trust-receipt-backups/ui-002b8e117f24033238cd686c230083a140b33bab/`。原图 SHA-256 仍为 `875de454…0610c`。
- 发布者独立公网浏览器 `m14-public-ui` 实测新标题、引导第 1/5 步、下一步到第 2 步、Escape 关闭；
  输入全新隔离工作区 `m14-release-probe-002b8e1` 并 Enter 后实际后端重跑完成，新工作区文件存在且引导保持关闭；
  完整刷新后从第 1/5 步重开。没有上传报表或执行核验。主控独立 `root-ui-release` 另复核新版引导、刷新重开及手机首页。
- 公网当前首页 1440×1000 与 390×844：异常 0、页面无横向溢出、主题 CSS 就绪；可见文字字号只在
  `12/14/16/20/24px` 集合，流程卡片 gap 为 16px，手机页顶为 12px。两处 Logo 复用同一自然宽 288px PNG：
  桌面显示 52/144px，手机 44px/大图按规范隐藏。未上传文件时“整理核对范围”禁用，没有首次/补交执行入口。
  截图为发布工作树忽略目录 `output/playwright/public-ui-1440.png`、`public-ui-390.png`；不能据首页推断完整结果/全部状态规范通过。
- 公网资源加载仍慢：独立首次导航的多个基础 chunk 耗时约 20–83s；一次带浏览器缓存的 reload 中 Logo 请求约 14.7s，
  浏览器报 slow-network 信息。无修复前同条件基线、无双视口全新冷上下文完整时序，不声称首屏速度达标或改善幅度；
  容器健康和页面最终渲染不替代速度验收。发布者检查时无 console error；主控会话有旧导航错误，不据此声称所有会话 console 0。
- 未完成：线上用户故障工作区具体原因或恢复验证、本轮真实 RPC/模型验收、公开上传/写链、完整冷加载性能对比、
  760px 边界两侧及 200% 全状态视觉矩阵。真人测试由用户取消；下面本地/旧发布条目为历史阶段证据，不代表当前未部署。

### 发布前本地网页集成验证（2026-10-07，历史阶段）

- 新独立工作树 `m14-local-ui-integration/HACKTHON`、分支 `codex/m14-local-ui-integration` 从已安全 fetch 核实的
  `origin/main=675728a` 创建；原 M14 工作树干净且保留。按顺序合入 M9 `795dddd` 和 M12
  `6f41026 / 5660f99 / ea4b82f / 8642b5c / a9c6523`，代码集成提交 `287770b`；没有合入 `8f8a311` 或 M15/M16。
  文档冲突保留 ADR-025 取消真人要求、ADR-026/029 UI 决定及已部署 Logo 记录，027/028 仍留给后续扩展。
- 合流后完整非 external pytest 再跑为 367 passed / 14 deselected（1 条既有第三方弃用 warning）；Ruff、主环境
  pip check、21 份 Schema、1000 行限制、diff check 通过。无凭据 FAIL→PASS→重放→恢复演示 valid=true。
- 本轮本地 Docker Desktop 可用。隔离 Linux 验证镜像 `trust-receipt:local-ui-287770b` 从同源归档/wheel、锁定依赖构建，
  没有 `.env`、真实密钥或生产挂载；构建期和独立 `docker run --rm --network none` 均通过真实 `/app` 入口门：
  98 个源码文件与 wheel 一致、实际导入 `/app/src`、首页异常 0、品牌区存在。该镜像只是本地验证，不是生产发布镜像。
- 本地浏览器 1440×1000 与 390×844、DPR 2：完整刷新从引导第 1 步开始；关闭后切换报表输入触发实际后端重跑，
  引导不重开；只读状态刷新同样不重开。Escape、Tab/Shift+Tab 焦点环实测通过。纯 JS 生命周期测试另覆盖打开时步骤保持。
  浏览器弹窗打开时按 `r` 未观察到后端重跑，不能将此时仍在第 2 步计为“打开弹窗下重跑”的浏览器实测。
- 新建本地 fixture 中断工作区恢复为 REQUESTED，仅显示中文阻塞与只读刷新，没有首次或补交按钮。
  两视口刷新后 task ID 不变、仍 REQUESTED / 0 交付 / 0 结果 / in-flight=1 / next_attempt=None；没有解锁、重跑或删除。
  截图 `output/playwright/integrated-pending-1440.png`、`integrated-pending-390.png`，只属于本地测试工作区。
- 两视口实际走通离线合成报表首次 FAIL → 缺修正版禁用最后一次 → 上传修正版 → PASS；首次记录保留，
  不再提供首次/补交按钮，不出现第三次请求，引导不重开，页面无横向溢出或 exception。
  截图分别为 `output/playwright/integrated-fail-{1440,390}.png`、`integrated-pass-{1440,390}.png`。
- 原 `branding.py/styles.py` 与主线首屏修复无差异；本地待处理页可见字号全部属于五级集合、导航 gap=16px、CSS 就绪、异常 0，
  两处 Logo 复用自然宽 288px 媒体资源；桌面 52/144px、手机 44px/大图隐藏。原 PNG 未修改。
- 未完成：真实 RPC/模型、线上用户任务原因确认或中断请求恢复、公开上传、写链、线上首屏冷时序、760px 两侧及 200% 完整视觉矩阵。
  该本地验证阶段未推送、未合并 main、未部署；后续经授权的发布结果见上方。测试脚本/本地 fixture 留在忽略的 `.tmp/`，截图不提交。

M12 新手引导独立补丁（2026-10-07，本地未部署）：工作台五步原生弹窗已接入，完整刷新从第一步显示；
Streamlit rerun 保留步骤与关闭状态，公开验证入口不弹上传引导。纯 JS 生命周期与 Python 接入测试 4 项通过，
非外部全量测试 311 passed / 13 deselected，Ruff 与 pip check 通过。本地浏览器实测下一步、Escape、
关闭后切换输入模式不重开、完整刷新重开；390×844 弹窗宽 352px、无页面横向溢出、按钮高 44px。
未执行本轮外部服务检查、公开上传、写链或部署。

### Attempt 持久化状态错位修复（本地业务与页面已接入，待主控集成部署）

- 用户截图的“仍显示 Attempt 1，却被安全锁拒绝”已在隔离测试复现同类路径：交付后异常保留 VERIFYING，
  或结果已保存但回执写入失败；恢复过滤未完成/缺回执 attempt，页面空 session 错当未开始。不归因于重复点击。
  未读取或修改用户线上工作区，因此不宣称已确认其具体数据库状态。
- 新增只读 `get_attempt_status(task_id)`，由持久化 state、交付与结果计数决定 in-flight/next attempt；
  缺失或冲突原始回执阻塞页面执行。M5/M8 `restore_task(task_id)` 仅读当前任务，不误选其他会话最新任务。
  REQUESTED/SUBMITTED/VERIFYING 不自动解锁、回滚或重跑；最多两次和第二次仅 FAIL/INCONCLUSIVE 规则不变。
- `request_attempt` 读/检查/请求在 SQLite IMMEDIATE 事务内串行化，两连接不能同时预约同一 attempt。
  本轮11项新增状态/故障/并发回归通过；页面接线由 M12 唯一写入，尚未部署或在线恢复用户任务。
- 修复基线为已知 `origin/main=675728a`；本轮 fetch 因 GitHub 443 连接失败未成功，不称已取实时最新远端。
- 本地完整 pytest 为340通过、14项外部配置缺失跳过；Ruff、pip check、21份 Schema、1000行限制和diff检查通过。
  无凭据 FAIL→PASS→回执重放→恢复演示 valid=true；没有外部探针、线上数据操作或部署。

### Logo 首屏与间距修复（已部署，公网冷加载时序待复核）

用户确认两个 Logo 曾一起缺席、随后出现，并授权修复。原图仍为 1,395,476 字节；标题和全局样式原经
Markdown 异步组件，当前 Streamlit 1.65.0 的 Markdown 独立 chunk 为 226,308 字节，HTML 独立 chunk 为 1,788 字节
（不含各自共享依赖，不把此大小比当作加载速度提升倍数）。修复首屏 CSS/品牌区改用直接 HTML，Logo 明确 eager，
两个位置复用原生媒体管道生成的 288px PNG 预览；保持原始图字节及业务行为不变。实际渲染资源已调整，不能沿用原始静态 URL 不变的旧结论；尚未声称生产加载速度已改善。

同次规范核查发现移动同组字段/卡片 gap 为 8px、页顶 padding 为 11.2px，结果结论卡片 margin 为 24px；分别修正为
16px、12px、16px。桌面输入面板 24px / 移动 16px 内边距属于 FRONTEND_SPEC 材质面板明确例外，保持不变。
本地输入页 1440px 与 390px 可见字号均属于五级集合，未发现页面横向溢出；不据此声称完整结果页/所有状态已通过规范验收。
修正后浏览器复测：移动页顶 12px、同组字段 16px、三步卡片间距 16px；桌面同组字段/三步卡片均为 16px。
显示预览为 288×288 RGBA（alpha 范围 0–254），82,098 bytes；原图 SHA-256 为
`875de454cce5210d4d8ca3049f68126b6196be1e465d558f8aa840146a00610c`，未修改。
本地非外部 pytest 329 passed / 14 deselected，ruff、pip check、diff check 通过；DPR 2 桌面小图 52px / 大图 144px
复用自然宽 288px 资源，手机小图 44px / 大图按规范隐藏，均已加载。
修复提交 `ea8f772a9bd8a512e01de0319e028bb24df99344` 经 [PR #13](https://github.com/CH-ZHOU-0512/xinjv/pull/13)
合并至 `2cc27e23ae8e2c71756b0c5206c5ee8e02f0b633`，两者源码树相同，分支/PR/main CI 均通过。
生产镜像 `trust-receipt:recovery-ea8f772a9bd8a512e01de0319e028bb24df99344` 已切换，仅重建 app；构建、独立运行和
切换前真实入口检查均 PASS（98 个源码文件与 wheel 一致、首页异常 0、品牌区存在）。容器 healthy，公网健康端点 200，
生产原图 hash 一致；APP_REQUIRE_LIVE=true、M6_ENABLE_WRITES=false，三处数据/回执挂载保持原路径，Blockscout 启动时间未变。
回滚镜像 `trust-receipt:recovery-rollback-ea8f772a9bd8a512e01de0319e028bb24df99344` 指向本次切换前已恢复的版本，
源码备份位于 `/opt/trust-receipt-backups/recovery-ea8f772a9bd8a512e01de0319e028bb24df99344/source.tar.gz`。
本轮新独立公网浏览器导航 60s 超时，未取得可用的线上冷加载时序；不能以容器/健康端点正常替代实际浏览器加载速度，
也不能由本地时序或资源字节比推断线上加速。线上加载复核与完整多状态视觉验收仍未完成；本轮没有真实用户测试、公开上传或写链。

本轮用户明确取消真实用户测试要求，并授权更新文档、提交、推送、合并与部署。发布采用 M14 已合流的 M9–M12 功能、
M13 已提交专属材料及 M14 技术验收交付；不纳入 M13 未提交浏览器驱动，不恢复暂停的浏览器排练。
真人参与不是发布条件，但 M14 仍为 8 PASS / 6 BLOCKED，M13 重新确认排练第三轮中断；不得称全部技术验收完成。
本授权不包含新增公开回执上传、合约部署或写链。当前发布执行结果将在本文件记录。

### M9–M14 发布与部署（2026-10-07）

#### 页面启动事故已恢复

- 修复提交 `b5f2bcf` 与调用方式修正 `bdc705cff5ed073451ddf21cacb0d5df0ef1b51b` 已分别通过
  [PR #10](https://github.com/CH-ZHOU-0512/xinjv/pull/10)、[PR #11](https://github.com/CH-ZHOU-0512/xinjv/pull/11)
  合并；修复主线为 `050a8527068e2b3e516ebdc0baf93c1ebf891ceb`，分支、PR、合并主线 CI 均通过。
- 当前线上镜像为 `trust-receipt:recovery-bdc705cff5ed073451ddf21cacb0d5df0ef1b51b`，revision label 对应同名完整源码提交，
  其应用/部署树与 PR #11 合并主线一致。98 个 Python 文件与已安装 wheel 一致（只归一化换行）。
- 旧故障镜像运行新增一致性门明确失败；恢复镜像在构建、隔离运行和切换前均通过真实 `/app/app/streamlit_app.py`
  AppTest：零 exception、产品标题渲染、实际导入 `/app/src/trust_receipt/__init__.py`。无网络、无生产挂载、无密钥，未用 PYTHONPATH。
  检查器初版直接从 `/opt` 启动的路径差异也被门拦截；修正为匹配生产模块启动的 `/app` 工作目录调用后才放行。
- 主控独立 `root-release-recovery` 浏览器在切换后实际显示工作台、产品标题、Logo、自定义黑金样式、运行配置、服务历史、
  示例/严格 JSON 模板与任务候选入口。最终 DOM 为 header=true、logoLoaded=true、moduleError=false、stException=0，console error=0。
  完整首页截图为主控工作区 `.playwright-cli/page-2026-10-07T09-00-19-212Z.png`（UTC 工具文件名，仅首页呈现证据）。
  初始灰色占位为尚未完成的异步加载，后续自行完成；未测速，不推导稳定加载耗时。本发布会话两个超时/空快照不冒计通过。
- 应用 running/healthy，公网 health 为 200/ok，镜像 pip check 通过。只替换应用容器，原配置及三个数据/回执挂载保持不变，
  Blockscout 仍为 `trust-receipt-blockscout:d0cf46a`，`M6_ENABLE_WRITES=false`，未触发业务上传、公开发布或写链。
- 已准备可用的 M8 回滚镜像 `trust-receipt:recovery-rollback-bdc705cff5ed073451ddf21cacb0d5df0ef1b51b`，
  同时保留原 M8 源码备份；故障现场源码保存在
  `/opt/trust-receipt-backups/recovery-bdc705cff5ed073451ddf21cacb0d5df0ef1b51b/source.tar.gz`，不把故障镜像当作健康回滚。
- 本地修复全量门为 326 passed、14 external deselected，新增 7 项发布回归通过；后续调用小修正的 9 项专属/治理检查通过，
  CI 重新运行完整门。Ruff、pip check、21 份 Schema、文件规模检查均通过。真人测试不要求；M14 六项待验收及 M13 中断边界不变。

**发布事故纠正：** 下列 healthy/200/WebSocket 仅证明服务连接，不代表业务页面成功渲染。用户截图与真实镜像隔离 AppTest
已复现 `streamlit_app.py:23 → m9_components.py:10 → ModuleNotFoundError: trust_receipt.m9`。
新 wheel 含 M9/history，但快捷发布漏复制 src，页面优先导入继承的 M8 `/app/src`。此前 `/release` 目录演示掩盖了旧源码覆盖，
“网页正常”结论撤回。当前按用户继续发布授权修复：永久 Dockerfile 同源复制 src，并新增真实入口及源码/wheel 一致性门。
修复部署结果见上方恢复记录；健康检查不补记 M13/M14 缺失验收。

- 发布分支已提交并推送，[PR #8](https://github.com/CH-ZHOU-0512/xinjv/pull/8) 已合并；
  主线部署提交为 `cd01f8dad329ebe6b7874c56a9a9ee0c005cc2e7`，分支、PR 与合并主线 CI 均通过。
- 广州应用镜像为 `trust-receipt:m14-cd01f8dad329ebe6b7874c56a9a9ee0c005cc2e7`，revision label 与部署提交完全一致。
  源码归档与纯 Python wheel 哈希校验通过；依赖未变，镜像内 pip check 通过，无网络 FAIL→PASS、回执重放及恢复 valid=true。
- 应用 running/healthy；匿名公网入口、健康端点、Logo 均为 200，WebSocket 连接为 Open。
  原 `.env`、data、private/public 回执挂载保留；Blockscout 仍为 `trust-receipt-blockscout:d0cf46a`，未重建其他应用，
  `M6_ENABLE_WRITES=false`。
- 回滚镜像为 `trust-receipt:m14-rollback-cd01f8dad329ebe6b7874c56a9a9ee0c005cc2e7`；源码备份为
  `/opt/trust-receipt-backups/m14-cd01f8dad329ebe6b7874c56a9a9ee0c005cc2e7/source.tar.gz`，同目录记录旧镜像。
- 本次不做真实用户测试，不恢复暂停的页面交互验证；M14 的 6 项待验收及 M13 第三轮中断保留。
  未新增公开回执上传、合约部署或链上交易。后续文档收尾提交不改变已部署的应用代码版本。

### 本轮发布质量门

- 发布合流版本实际执行非 external pytest：319 passed、14 deselected，1 条既有第三方弃用 warning。
- 全仓 Ruff、主环境 pip check、21 份可重复 Schema、1000 物理行限制和 git diff --check 通过。
- 无凭据演示得到 FAIL→PASS、两份回执重放及恢复，valid=true；未执行公开发布。
- 本轮没有重跑外部探针或暂停的浏览器排练；这些本地检查不补记 M13/M14 缺失的技术验收。

M12 页面接入补充（2026-10-07）：已消费 M9 `795dddd` 的 M8 状态与当前 task 恢复端口，
首次/补交按钮仅依赖持久化 next_attempt；未完成请求、缺回执、记录或快照冲突均阻塞，不以空 session 判首次。
操作失败保留实际错误并 rerun 只读重投影，点击前再次检查状态；不自动重试、撤销请求、删历史或新增第三次。
当前任务缓存落后时仅读恢复该 task_id，不误选另一会话最新任务；恢复冲突提供中文阻塞和实际错误详情。
27 项状态专项回归（核心 11 + 页面 6 + 视图/同步 10）通过；最终非外部全量 348 passed / 13 deselected。
Ruff、pip check、21 份 Schema 重新生成无差异、1000 行限制与 diff 检查通过。
本地浏览器恢复独立 fixture 中断工作区，1440×1000 与 390×844 均无横向溢出；无首次按钮，
只有只读刷新，刷新后 DB 仍 REQUESTED、零交付，引导未重开。截图留在 `.tmp/`，不提交。
新会话恢复、请求后异常、结果写后回执异常、FAIL/INCONCLUSIVE 补交、PASS/两次结束及并发预约由离线测试验证。
线上具体 DB 状态未读取，真实 RPC/模型、公开上传、写链、部署与用户线上悬挂请求恢复均未执行。


M12 普通人交互独立补丁（2026-10-07，本地未部署）：业务按钮与必要报表选择、完整范围确认、
高级配置折叠、原输入折叠、金额/差额/原因/下一步优先及证据详情折叠已实现。缺文件/范围不能继续，
整理失败不替代演示范围，首次 FAIL 上传任务缺修正版禁用唯一补交；模拟说明与真实 AI 调用区分。
非外部全量 318 passed / 13 deselected（最后文案收敛前），新增交互测试覆盖输入门禁、确认、AI 失败、
三态与写链状态、修正版门禁和唯一主操作。本地 390px 浏览器实测显式练习→整理→人工确认→主动核对→
FAIL 差异与修正版门禁，页面无横向溢出；引导全程未重开。修正版 PASS 与 INCONCLUSIVE 由 AppTest 验证，
AppTest 不支持文件上传，修正版 adapter 使用测试注入，不冒充真实浏览器上传。本轮真实模型/RPC、
公开上传、写链和部署未执行。M14 `ea8f772` 的品牌/CSS 与相关测试块已局部移植至本地共测，
未移植部署脚本/根文档；最终共测 321 passed / 13 deselected，Ruff、pip check 与行数检查通过。
浏览器冷启动确认 288px 原生媒体 Logo 与引导共存、390px 无横向溢出；上一页/五步/完成可用，
首尾 Tab 与 Shift+Tab 的显式循环焦点约束已补强并实测，Python/JS 引导测试 4 passed。
本地热更新曾遇旧 branding 模块缓存，重启本人启动的本地进程后冷启动正常，不视为生产部署验证。

M1 已完成：领域契约、Pydantic 模型、8 份 JSON Schema、契约测试和 12 份人工标注 fixtures
均已集成到 `codex/m1-integration`。M2 PR #1 已合并，远端合并提交为
`d9ac1108e9a21fe0073587d4f458848ed1ac8ecd`。M3 无 UI 纵向闭环及本地回执重放已在本地实现并验证。
M4 受限 AI 编排、供应商 adapter、离线对抗测试及真实 DeepSeek 结构化调用已完成。M5 Streamlit 产品页面、
fixture 路径与真实 DeepSeek + Sepolia RPC + Blockscout 产品闭环均已完成；桌面、移动端和进程重启恢复均已做真实浏览器检查。
M5 已部署至广州 Linux 服务器的隔离容器，并通过现有 HTTPS 反向代理公开访问。M6 公共回执发布与 ERC-8004 关联均已
完成真实 Sepolia 产品闭环：公共内容哈希、链上反馈、事件读回和 SQLite 终态一致。M7 验收封装与本地收尾已完成；
`codex/m1-integration` 已同步远端 M2 合并历史并进入 `main`，最终主线 CI 已通过。M8 资金流投影、EIP-712 承诺、前端主流程
重构与 Validation Registry 只读探针已合并并部署到广州应用；M9–M14 本轮已集成发布，剩余技术验收见前述记录。
专用锚仍只是未部署候选。

合流依赖分支补充记录（待主控统一治理）：

重构与 Validation Registry 只读探针已通过 PR #6 合并到 `main`（`821bbc2`）。M9 确定性返工、外置版本链、修复对比与公开验证
已在独立交付分支实现并完成本地验收，包括 M8 承诺快照、恢复、返工主流程、可移交公开历史包和独立验证页面；
已只读核验既有公开回执与 Sepolia feedback，尚未合并主线、部署或上传新的公开历史包。
M10 已在独立交付分支接入 M8+M9 工作区与页面并完成本地验收；尚未合并主线或部署。

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

按新授权补齐保留的技术验收；不依赖用户招募，也不自动恢复暂停的浏览器操作。专用最小锚只交付未部署候选；
真实部署、生产接入、公共上传验证与写链仍需额外审查、配置和明确授权。

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
## M10 服务历史实现进展

- 已新增独立 `trust_receipt.history` 读模型：按服务、显式任务类型与任务聚合首次 PASS、修复后 PASS、FAIL、
  INCONCLUSIVE、可验证回执数和最近交付；所有计数可由任务事实与来源回执重新计算。
- 只有通过现有独立回执重放的回执进入统计；篡改或未核验回执被排除。`INCONCLUSIVE` 单独展示，不增加失败数；修复成功任务
  不继续计为负面任务，但下钻保留修复前后的完整回执链。
- 已提供只读 `ReceiptRevisionPort` 适配 M9 父级/替代关系，并提供两服务同任务类型对比与显式人工选择 API；不生成排名、
  综合分或自动选择。
- 已集成 M8/M9 页面入口与运行时装配：当前工作区历史按需扫描，两服务无历史时明确显示暂无；可下钻原始回执与真实父版本，
  显式确认服务后带入下一次报表验收。版本链核验缺父、身份冲突或篡改时排除任务并提示 INCONCLUSIVE。
- 仅原始不可变 attempt 参与统计；M6 发布快照不重复计数，本地与公开哈希不混用。跨服务 A FAIL → B FIXED 成功只属于 B，
  A 的失败保留。测试覆盖空历史、缺父链、伪造关系、重复发布、换服务修复与中性证据不足。
- AppTest 走通 A FAIL → B PASS/FIXED → 来源下钻 → 选择 B → 下一任务继续选择 B；真实浏览器走通同样的两个 attempt、
  历史对比与人工确认。1440×1000 桌面和 390×844 手机截图已检查，手机页面无横向溢出；未完成 760px 两侧/200% 全矩阵。
- 加载优化：原图 Logo 改用可缓存同源静态 URL，避免每次重跑重复内嵌约 3.72MB base64；OpenAI/Agent0 SDK 按需加载。
  本地 runtime 导入由约 3.81 秒降至 2.12–2.49 秒；本地热刷新从单次约 1.80 秒到三次 1.39–1.43 秒。
  样本有限，不当作生产测速；冷启动与网络条件不同，生产优化尚未部署。
- 本轮全量 pytest 266 项通过、9 项 external 缺配置跳过，另有第三方弃用 warning；Ruff、pip check、21 份 Schema 漂移和
  1000 行检查通过。没有新增公开上传、真实密钥使用、写链、推送、主线合并或部署。

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

## M9 修复与回执验证进展

- 新增确定性 `ReworkPackage`：仅把 `FAIL` 回执中 `confirmed + error` Finding 映射为闭合返工动作，
  不把 hypothesis 或证据不足改写为确定指令；返工包使用 canonical SHA-256 自哈希。
- 新增外置 `ReceiptRevision` 和只创建不覆盖的 `LocalRevisionStore`；两次 attempt 以 parent/supersedes 形成自哈希链，
  不修改 `Receipt 1.0` 或旧回执哈希。`RepairComparison` 保留 task/service/attempt/receipt hash/outcome/resolution、
  整数金额与证据引用，并复用既有 v1 交付哈希和 EVM 签名校验。
- 新增只读 `PublicReceiptResolver` / `ReceiptCommitmentVerifier` 稳定端口及独立 CLI，支持 URI、receipt hash、
  task hash 和 feedback transaction 入口；必要公开证据缺失返回 `INCONCLUSIVE`，冲突返回 `INVALID`。
  M8 承诺端口缺失时显式记为 `UNVERIFIED`，不伪造承诺已核验。
- 新增 M8→M9 适配层，直接复验持久化 Task/Delivery EIP-712 承诺、完整对象链接和期望 signer；有效快照标记为
  `VERIFIED`，缺失保持 `UNVERIFIED`，篡改或冲突标记为 `INVALID`。`NOT_SUBMITTED` 锚状态继续明确展示，不冒充链上确认。
- `app/streamlit_app.py` 已接入首次失败返工单、每次 attempt 的外置版本记录、第二次修复前后对比和公共 URI 独立重放入口；
  版本存储基于原始不可变 attempt 回执，避免后续 M6 publication 状态改变回执哈希时覆盖历史。
  公共 attempt 2 缺少公开 parent revision 时按契约返回 `INCONCLUSIVE`，不会借用私有 SQLite 补证。
- 新增显式授权的 `PublicVerificationBundle`，同时携带公开父/子回执与对应外置版本链；公开哈希与本地不可变
  attempt 哈希分开重建，不混用两套历史。导出可在另一进程和空私有会话中独立验证；重复发布从追加元数据恢复，
  上传后必须下载原始字节核对哈希。未授权不能导出或上传，首轮 FAIL 不会被修复成功掩盖。
- 独立 `?verify=1` 页面不初始化 AI 或私有工作区；支持公开文件、配置范围内 HTTPS/IPFS、回执/任务哈希和真实
  feedback 交易。真实 feedback 只读校验链、Registry、确认数、canonical 区块、交易 sender、事件字段和公开内容哈希；
  调用者自报交易字符串不能作为链上证据，缺少公开父回执仍为 `INCONCLUSIVE`。
- 浏览器实际走通 fixture 服务 A 首轮 FAIL → 服务 B 第二轮 PASS → FIXED 对比 → 授权导出 → 新独立页面验证
  PASS/FIXED；两个 attempt 和不同服务身份保留。主流程与独立结果页在 390×844 均无页面横向溢出，抽查可见字号
  在 `12/14/16/20/24px` 集合内。本轮未完成 760px 两侧及 200% 放大的完整视觉矩阵。
- 已匿名下载并重放既有公开 M6 回执；已真实只读核验既有 Sepolia feedback 交易
  `0xbf09156a706ca8a49b18606083cacd2f2d844684a0af60e65602c6167374dad9`。事件、公开授权、字节哈希和回执重放通过；
  旧 attempt 2 缺少公开父链，所以总体为 `INCONCLUSIVE`，M8 承诺仍为 `UNVERIFIED`。没有新增公开上传或写链。
- 五份 M9 追加契约纳入稳定导出，总计 21 份 Schema。全量本地测试为 251 项通过、9 项 external 因当前环境配置
  缺失而明确跳过；公开历史和反馈冲突、缺父链、非规范 JSON、独立进程等边界均覆盖。M9 下一步为交给现有 M10
  分支集成服务历史与人工选择，不把 M10 能力标为已经完成。
- 收尾 Ruff、`pip check`、21 份 Schema 漂移、1000 物理行限制与无凭据 FAIL→PASS→恢复演示均通过。

## M11–M14 并行启动

- 用户已授权各工作包独立开发，并进一步授权 M9–M14 自动跨会话沟通，由当前会话主控。最终交付仍须集成验收，不能以分支完成替代。
- 共同计划基线使用 `codex/m11-m14-planning`；A `codex/m11-real-case`，B `codex/m12-user-experience`，
  C `codex/m13-demo-verification`，D `codex/m14-user-trial-prep`。各线使用隔离工作区，不修改他人分支；M12 可本地合入已提交 M10/M9/M11。
- A 拥有案例与预检脚本，B 拥有页面与前端测试，C 拥有路演检查与端到端测试，D 拥有用户就绪验收材料。
  根目录权威文档与公共 wiring 由当前集成会话统一维护，各线提交专属交接材料供同步。
- 初始开发授权不包含公开发布、写链或部署；最终交付没有真实用户及真实测试用户，取消招募依赖。
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
- M14 最终交接提交 `8669ed9`，主控只读核实工作树干净；最新 `m14-live-06/matrix.json` 为八项 PASS
  （UR02/03/05/06/10/11/13/14）、六项 BLOCKED（UR01/04/07/08/09/12），`ready=false`。
  已有独立真实报表、冷上下文、八类非法上传恢复、确认拒绝、身份、写隔离、键盘和说明路径证据；未验收的重启、
  浏览器故障/来源冲突、第三 attempt 拒绝及原生 200% 缩放等仍保留。新摘要在该分支 `docs/user-trials/readiness-evidence-2026-10-07.md`。
  故障进程已由 M14 关闭，正常 8534 保留只供手动查看；不再自动操作。未做真实用户测试，完整 M14 技术验收未齐。

## 业务报告资金流图补充

- 在独立 reporting 工作树加入本地固定 Apache ECharts 6.0.0 组件、数据配置接口与自包含图组件；
  账户节点和转账箭头保留已保存的精确金额、来源及事件引用，不重新计算结论。默认 12 条分页预览明确标注，完整 200 条可逐页访问。
- reporting 与图接口测试 37 项通过，限定文件 Ruff 通过；五种离线视图各在 390/1440px 完成 SVG SSR 生成检查。
  此项不是人工视觉验收；独立组件交接时尚未接入页面，本地接线现况见首项，也没有生产部署。
- 用户已要求暂停浏览器自动操作，由其手动验证。实际手机可读性、交互与页面接线仍待验；
  Word/PDF 逐页验收尚未完成，本分支不能标记全量收尾。

## 状态更新规则

- 这里只记录当前事实、下一步和实际阻塞。
- 完成某阶段时更新本文件，不在多个设计文档重复维护进度。
- 每项“已完成”必须能对应文件、命令输出、测试记录或外部交易。
