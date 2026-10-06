"""Responsive visual shell kept separate from page behavior."""

APP_CSS = """
<style>
:root { --ink:#17231f; --muted:#64746d; --paper:#f6f3eb; --line:#d9ded8; --mint:#d9f2e7; }
.stApp { background:linear-gradient(145deg,#f8f5ed 0%,#eef5f1 55%,#f8f5ed 100%); color:var(--ink); }
.block-container { max-width:1180px; padding-top:2rem; padding-bottom:5rem; }
.eyebrow { color:#1f6b52; font-size:.78rem; font-weight:800; letter-spacing:.12em; text-transform:uppercase; }
.hero { padding:1.4rem 0 1rem; border-bottom:1px solid var(--line); margin-bottom:1.2rem; }
.hero h1 { font-size:clamp(2rem,5vw,4.4rem); line-height:.96; letter-spacing:-.045em; margin:.35rem 0 .8rem; }
.hero p { max-width:760px; color:var(--muted); font-size:1.05rem; }
.mode-banner { border:1px solid #a9c8bc; background:#edf8f3; border-radius:14px;
  padding:.85rem 1rem; margin:.5rem 0 1.25rem; }
.step-title { display:flex; gap:.7rem; align-items:center; margin:1.6rem 0 .75rem; }
.step-number { width:2rem; height:2rem; border-radius:50%; background:var(--ink); color:white;
  display:grid; place-items:center; font-weight:800; }
.status-card,.finding-card,.attempt-card { overflow-wrap:anywhere; border:1px solid var(--line);
  border-radius:16px; padding:1rem; background:rgba(255,255,255,.78);
  box-shadow:0 8px 28px rgba(31,53,45,.06); margin:.55rem 0; }
.status-card small,.attempt-card small { color:var(--muted); text-transform:uppercase; letter-spacing:.08em; }
.metric-value { font-size:1.55rem; font-weight:800; margin-top:.25rem; }
.outcome-PASS { border-left:6px solid #1f8a5b; }
.outcome-FAIL { border-left:6px solid #c85645; }
.outcome-INCONCLUSIVE { border-left:6px solid #c88b2d; }
.badge { display:inline-block; padding:.25rem .55rem; border-radius:999px; font-size:.76rem;
  font-weight:800; margin:.12rem .25rem .12rem 0; }
.badge-submitted { background:#e8efff; color:#264d91; }
.badge-confirmed { background:#dff4e9; color:#17613f; }
.badge-not-submitted { background:#f7e7d1; color:#874e10; }
.mono { font-family:ui-monospace,SFMono-Regular,Consolas,monospace; font-size:.82rem; overflow-wrap:anywhere; }
div[data-testid="stButton"] button, div[data-testid="stDownloadButton"] button { min-height:2.8rem; width:100%; }
div[data-testid="stJson"] { max-width:100%; overflow-x:auto; }
@media (max-width: 760px) {
  .block-container { padding:1rem .9rem 4rem 3.35rem; }
  .hero { padding-top:.4rem; }
  .hero h1 { font-size:2.45rem; }
  div[data-testid="stHorizontalBlock"] { flex-direction:column !important; gap:.5rem !important; }
  div[data-testid="column"] { width:100% !important; flex:1 1 100% !important; min-width:0 !important; }
  .status-card,.finding-card,.attempt-card { padding:.85rem; border-radius:13px; }
  .metric-value { font-size:1.3rem; }
  code,pre { white-space:pre-wrap !important; word-break:break-word !important; }
}
</style>
"""
