"""Product-grade responsive visual shell kept separate from page behavior."""

# ruff: noqa: E501

APP_CSS = """
<style>
:root { --navy:#071521; --navy-2:#102433; --ink:#14222d; --muted:#637380; --paper:#f4f6f5;
  --card:#fff; --line:#dce3e1; --aqua:#23c6a2; --aqua-soft:#e8f8f3; --blue:#356df3;
  --amber:#e89a32; --red:#dd5b4d; --shadow:0 16px 44px rgba(7,21,33,.08); }
html,body,[class*="css"] { font-family:Inter,'Noto Sans SC','Microsoft YaHei',system-ui,sans-serif; }
.stApp { background:var(--paper); color:var(--ink); }
.block-container { max-width:1240px; padding:1.15rem 2.2rem 5rem; }
header[data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stSidebar"] { display:none !important; }
.product-bar { display:flex; align-items:center; justify-content:space-between; min-height:54px;
  border-bottom:1px solid var(--line); margin-bottom:1.2rem; }
.brand { display:flex; align-items:center; gap:.7rem; font-weight:800; letter-spacing:-.02em; }
.brand-mark { width:30px; height:30px; border-radius:9px; background:var(--navy); color:#fff;
  display:grid; place-items:center; font-size:.82rem; }
.env-chip { display:inline-flex; align-items:center; gap:.45rem; color:#315244; background:var(--aqua-soft);
  border:1px solid #bfe8dc; border-radius:999px; padding:.36rem .68rem; font-size:.78rem; font-weight:700; }
.env-dot { width:7px; height:7px; border-radius:50%; background:var(--aqua); box-shadow:0 0 0 4px rgba(35,198,162,.12); }
.hero-grid { display:grid; grid-template-columns:minmax(0,1.35fr) minmax(320px,.65fr); gap:1rem; margin-bottom:1rem; }
.hero-main { position:relative; overflow:hidden; min-height:250px; padding:2.1rem 2.25rem; border-radius:24px;
  color:#fff; background:radial-gradient(circle at 90% 12%,rgba(35,198,162,.24),transparent 35%),
  linear-gradient(135deg,var(--navy),var(--navy-2)); box-shadow:var(--shadow); }
.hero-main:after { content:""; position:absolute; right:-70px; bottom:-120px; width:280px; height:280px;
  border:1px solid rgba(255,255,255,.12); border-radius:50%; box-shadow:0 0 0 38px rgba(255,255,255,.025); }
.eyebrow { color:#72e4c8; font-size:.72rem; font-weight:800; letter-spacing:.15em; text-transform:uppercase; }
.hero-main h1 { position:relative; z-index:1; max-width:720px; font-size:clamp(2.15rem,4vw,3.75rem);
  line-height:1.05; letter-spacing:-.045em; margin:.55rem 0 1rem; }
.hero-main p { position:relative; z-index:1; max-width:700px; color:#bdd0d8; font-size:1rem; line-height:1.75; margin:0; }
.hero-side { border:1px solid var(--line); border-radius:24px; background:var(--card); padding:1.45rem;
  box-shadow:0 12px 36px rgba(7,21,33,.05); }
.hero-side-label { color:var(--muted); font-size:.72rem; font-weight:800; letter-spacing:.12em; text-transform:uppercase; }
.promise { display:grid; grid-template-columns:34px 1fr; gap:.7rem; padding:.82rem 0; border-bottom:1px solid #edf0ef; }
.promise:last-child { border-bottom:0; }
.promise-index { width:30px; height:30px; border-radius:9px; background:#edf3f1; color:#244439;
  display:grid; place-items:center; font-weight:800; font-size:.78rem; }
.promise strong { display:block; font-size:.92rem; margin-bottom:.16rem; }
.promise span { display:block; color:var(--muted); font-size:.79rem; line-height:1.45; }
.signal-grid { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:.75rem; margin:.85rem 0 1.4rem; }
.signal-card { min-width:0; border:1px solid var(--line); border-radius:15px; background:rgba(255,255,255,.82); padding:.78rem .92rem; }
.signal-card small { color:var(--muted); display:block; font-size:.68rem; font-weight:800; letter-spacing:.1em;
  text-transform:uppercase; margin-bottom:.28rem; }
.signal-value { font-weight:700; font-size:.87rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.signal-value:before { content:""; display:inline-block; width:7px; height:7px; border-radius:50%; background:var(--aqua); margin-right:.48rem; }
.section-head { display:flex; align-items:flex-end; justify-content:space-between; gap:1rem; margin:1.85rem 0 .8rem; }
.section-kicker { color:var(--blue); font-size:.7rem; font-weight:800; letter-spacing:.12em; text-transform:uppercase; }
.section-head h2 { margin:.18rem 0 0; font-size:1.45rem; letter-spacing:-.025em; }
.section-head p { max-width:480px; margin:0; color:var(--muted); font-size:.84rem; text-align:right; }
.task-summary { display:grid; grid-template-columns:1.1fr .65fr .65fr; gap:.75rem; margin:.5rem 0; }
.summary-cell { min-width:0; border:1px solid var(--line); border-radius:14px; padding:.8rem .9rem; background:#fbfcfc; }
.summary-cell small { display:block; color:var(--muted); font-size:.68rem; font-weight:800; letter-spacing:.08em;
  text-transform:uppercase; margin-bottom:.28rem; }
.summary-cell strong { display:block; overflow-wrap:anywhere; font-size:.84rem; }
.attempt-card,.status-card,.finding-card { overflow-wrap:anywhere; border:1px solid var(--line); border-radius:15px;
  padding:1rem; background:#fbfcfc; margin:.55rem 0; }
.attempt-card { display:flex; align-items:center; justify-content:space-between; gap:1rem; border-left-width:5px; }
.attempt-card small,.status-card small { color:var(--muted); font-size:.68rem; font-weight:800; letter-spacing:.1em; text-transform:uppercase; }
.attempt-title { font-size:1.55rem; font-weight:800; letter-spacing:-.03em; margin-top:.15rem; }
.outcome-PASS { border-left-color:var(--aqua); background:linear-gradient(90deg,#eefaf6,#fff 34%); }
.outcome-FAIL { border-left-color:var(--red); background:linear-gradient(90deg,#fff1ef,#fff 34%); }
.outcome-INCONCLUSIVE { border-left-color:var(--amber); background:linear-gradient(90deg,#fff8eb,#fff 34%); }
.badge { display:inline-block; padding:.28rem .58rem; border-radius:999px; font-size:.68rem; font-weight:800;
  margin:.12rem .2rem .12rem 0; white-space:nowrap; }
.badge-submitted { background:#e9efff; color:#264f9e; }
.badge-confirmed { background:#dff6ed; color:#126247; }
.badge-not-submitted { background:#fff0db; color:#8c5313; }
.mono { font-family:ui-monospace,SFMono-Regular,Consolas,monospace; font-size:.78rem; overflow-wrap:anywhere; }
div[data-testid="stVerticalBlockBorderWrapper"] { border-color:var(--line) !important; border-radius:18px !important;
  background:var(--card); box-shadow:0 10px 32px rgba(7,21,33,.045); }
div[data-testid="stForm"] { border:0; padding:0; }
div[data-testid="stTextArea"] textarea,div[data-testid="stTextInput"] input,div[data-testid="stNumberInput"] input {
  border-radius:11px; border-color:#d7dfdd; background:#fafcfc; }
div[data-testid="stTextArea"] textarea:focus,div[data-testid="stTextInput"] input:focus,
div[data-testid="stNumberInput"] input:focus { border-color:var(--aqua); box-shadow:0 0 0 1px var(--aqua); }
div[data-testid="stButton"] button[kind="primary"],div[data-testid="stFormSubmitButton"] button[kind="primary"] {
  min-height:3rem; border-radius:11px; border:0; background:var(--navy); color:#fff; font-weight:750; }
div[data-testid="stButton"] button[kind="primary"]:hover,div[data-testid="stFormSubmitButton"] button[kind="primary"]:hover {
  background:#153348; border:0; }
div[data-testid="stDownloadButton"] button { width:100%; min-height:2.75rem; border-radius:10px; }
div[data-testid="stMetric"] { border:1px solid var(--line); border-radius:14px; padding:.78rem .9rem; background:#fff; }
div[data-testid="stMetricValue"] { font-size:1.35rem; }
div[data-testid="stExpander"] { border:1px solid var(--line); border-radius:14px; background:rgba(255,255,255,.7); }
div[data-testid="stJson"] { max-width:100%; overflow-x:auto; }
@media (max-width:900px) {
  .hero-grid { grid-template-columns:1fr; }
  .hero-main { min-height:auto; }
  .hero-side { display:grid; grid-template-columns:repeat(3,1fr); gap:.55rem; }
  .hero-side-label { grid-column:1/-1; }
  .promise { grid-template-columns:30px 1fr; border:0; padding:.45rem; }
}
@media (max-width:760px) {
  .block-container { padding:.7rem .85rem 4rem; }
  .product-bar { margin-bottom:.75rem; }
  .hero-grid { gap:.7rem; }
  .hero-main { padding:1.4rem 1.2rem; border-radius:18px; }
  .hero-main h1 { font-size:2.1rem; }
  .hero-main p { font-size:.9rem; }
  .hero-side { display:block; padding:1rem; border-radius:18px; }
  .signal-grid,.task-summary { grid-template-columns:1fr; gap:.5rem; }
  .section-head { display:block; margin-top:1.35rem; }
  .section-head p { text-align:left; margin-top:.35rem; }
  div[data-testid="stHorizontalBlock"] { flex-direction:column !important; gap:.5rem !important; }
  div[data-testid="column"] { width:100% !important; flex:1 1 100% !important; min-width:0 !important; }
  .attempt-card { align-items:flex-start; flex-direction:column; }
  .attempt-title { font-size:1.35rem; }
  code,pre { white-space:pre-wrap !important; word-break:break-word !important; }
}
</style>
"""
