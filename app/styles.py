"""Black-gold responsive shell for the report-verification workflow."""

# ruff: noqa: E501

APP_CSS = """
<style>
:root { --tr-bg-page:#0A0A0A; --tr-bg-surface:#141414; --tr-bg-raised:#1C1C1C;
  --tr-text-primary:#F3F1EA; --tr-text-secondary:#B8B3A8; --tr-text-note:#9B978F;
  --tr-border-default:#33302B; --tr-border-control:#8B7355; --tr-gold-primary:#D4AF37;
  --tr-gold-line:#8B7355; --tr-gold-highlight:#FAEBD7; --tr-text-on-accent:#0A0A0A;
  --tr-state-matched:#4ADE80; --tr-state-error:#F87171; --tr-state-internal:#FB923C;
  --tr-state-duplicate:#C084FC; --tr-state-inconclusive:#FACC15;
  --tr-shadow-card:0 4px 12px rgb(0 0 0 / 24%); }
html,body,[class*="css"] { font-family:Inter,'Noto Sans SC','Microsoft YaHei',system-ui,sans-serif; }
.stApp { color:var(--tr-text-primary); background-color:var(--tr-bg-page); background-image:linear-gradient(rgb(255 255 255 / 1%) 1px,transparent 1px),linear-gradient(90deg,rgb(255 255 255 / 1%) 1px,transparent 1px); background-size:32px 32px; }
.block-container { max-width:1240px; padding:1rem 24px 5rem; }
header[data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stSidebar"] { display:none !important; }
.product-bar { display:flex; align-items:center; justify-content:space-between; min-height:52px; border-bottom:1px solid var(--tr-border-default); margin-bottom:24px; }
.brand { display:flex; align-items:center; gap:12px; font-weight:800; }
.brand-mark { width:32px; height:32px; border:1px solid var(--tr-gold-line); border-radius:8px; display:grid; place-items:center; color:var(--tr-gold-primary); font-size:.75rem; }
.env-chip { display:inline-flex; align-items:center; gap:8px; color:var(--tr-text-secondary); border:1px solid var(--tr-border-default); border-radius:9999px; padding:6px 10px; font-size:.75rem; }
.env-dot { width:7px; height:7px; border-radius:50%; background:var(--tr-state-matched); }
.hero-main { padding:20px 0 24px; border-bottom:1px solid var(--tr-gold-line); }
.eyebrow,.section-kicker { color:var(--tr-gold-primary); font-size:.7rem; font-weight:800; letter-spacing:.13em; text-transform:uppercase; }
.hero-main h1 { margin:8px 0; max-width:820px; color:var(--tr-text-primary); font-size:clamp(1.9rem,4vw,3rem); line-height:1.12; letter-spacing:-.04em; }
.hero-main p { margin:0; max-width:720px; color:var(--tr-text-secondary); line-height:1.7; }
.workflow-steps { display:flex; align-items:center; gap:12px; padding:16px 0 4px; color:var(--tr-text-secondary); }
.workflow-steps span { display:inline-flex; align-items:center; gap:8px; }.workflow-steps b { width:25px; height:25px; display:grid; place-items:center; border:1px solid var(--tr-gold-line); border-radius:9999px; color:var(--tr-gold-primary); font-size:.72rem; }.workflow-steps i { color:var(--tr-text-note); font-style:normal; }
.signal-grid { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:16px; margin:24px 0 32px; }
.signal-card,.summary-cell { min-width:0; border:1px solid var(--tr-border-default); border-radius:12px; background:var(--tr-bg-surface); padding:12px; box-shadow:var(--tr-shadow-card); }
.signal-card small,.summary-cell small,.attempt-card small,.status-card small { color:var(--tr-text-note); display:block; font-size:.68rem; font-weight:800; letter-spacing:.08em; text-transform:uppercase; margin-bottom:4px; }
.signal-value { color:var(--tr-text-secondary); overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }.signal-value:before { content:""; display:inline-block; width:7px; height:7px; border-radius:50%; background:var(--tr-state-matched); margin-right:8px; }
.section-head { display:flex; align-items:flex-end; justify-content:space-between; gap:16px; margin:32px 0 12px; }.section-head h2 { margin:4px 0 0; color:var(--tr-text-primary); font-size:1.45rem; }.section-head p { max-width:500px; margin:0; color:var(--tr-text-note); font-size:.84rem; text-align:right; }
.task-summary { display:grid; grid-template-columns:1.1fr .65fr .65fr; gap:16px; }.summary-cell strong { display:block; overflow-wrap:anywhere; color:var(--tr-text-primary); font-size:.84rem; }
.attempt-card,.status-card,.finding-card { overflow-wrap:anywhere; border:1px solid var(--tr-border-default); border-radius:12px; padding:12px; background:var(--tr-bg-raised); margin:8px 0; }
.attempt-card { display:flex; align-items:center; justify-content:space-between; gap:16px; border-left-width:4px; }.attempt-title { font-size:1.55rem; font-weight:800; }.outcome-PASS { border-left-color:var(--tr-state-matched); }.outcome-FAIL { border-left-color:var(--tr-state-error); }.outcome-INCONCLUSIVE { border-left-color:var(--tr-state-inconclusive); }
.badge { display:inline-block; padding:5px 9px; border:1px solid var(--tr-border-default); border-radius:9999px; color:var(--tr-text-secondary); font-size:.68rem; font-weight:800; margin:2px; }.badge-confirmed { border-color:var(--tr-state-matched); }.badge-submitted { border-color:var(--tr-state-inconclusive); }.badge-not-submitted { color:var(--tr-text-note); }
.mono,.flow-key { font-family:ui-monospace,SFMono-Regular,Consolas,monospace; overflow-wrap:anywhere; }
.flow-legend-row { display:flex; flex-wrap:wrap; gap:8px; margin:8px 0 12px; }.flow-legend { border-left:3px solid; border-radius:4px; padding:4px 8px; background:var(--tr-bg-raised); color:var(--tr-text-secondary); font-size:.75rem; }
.flow-edge { display:grid; grid-template-columns:minmax(0,1.6fr) minmax(120px,.55fr) minmax(150px,.6fr); gap:12px; align-items:center; border-left:4px solid; border-radius:12px; padding:12px; margin:8px 0; background:var(--tr-bg-raised); }.flow-route { display:flex; gap:8px; align-items:center; min-width:0; }.flow-route span { overflow-wrap:anywhere; }.flow-route b { color:var(--tr-text-note); }
.flow-amount { color:var(--tr-gold-primary); font-variant-numeric:tabular-nums; text-align:right; }.flow-amount small { color:var(--tr-text-note); }.flow-status { font-weight:700; }.flow-key { grid-column:1/-1; color:var(--tr-text-note); font-size:.72rem; }
.flow-MATCHED { border-color:var(--tr-state-matched); }.flow-MISSING_FROM_REPORT,.flow-NOT_FOUND_ON_CHAIN { border-color:var(--tr-state-error); }.flow-INTERNAL_TRANSFER { border-color:var(--tr-state-internal); }.flow-DUPLICATE { border-color:var(--tr-state-duplicate); }.flow-INCONCLUSIVE { border-color:var(--tr-state-inconclusive); }
div[data-testid="stVerticalBlockBorderWrapper"] { border-color:var(--tr-border-default) !important; border-radius:12px !important; background:var(--tr-bg-surface); box-shadow:var(--tr-shadow-card); } div[data-testid="stForm"] { border:0; padding:0; }
div[data-testid="stTextArea"] textarea,div[data-testid="stTextInput"] input,div[data-testid="stNumberInput"] input { border-radius:8px; border-color:var(--tr-border-control); background:var(--tr-bg-raised); color:var(--tr-text-primary); }
div[data-testid="stButton"] button,div[data-testid="stFormSubmitButton"] button,div[data-testid="stDownloadButton"] button { border-radius:8px; min-height:2.75rem; } div[data-testid="stButton"] button[kind="primary"],div[data-testid="stFormSubmitButton"] button[kind="primary"] { min-height:3rem; border:0; background:var(--tr-gold-primary); color:var(--tr-text-on-accent); font-weight:800; } div[data-testid="stButton"] button[kind="primary"]:hover,div[data-testid="stFormSubmitButton"] button[kind="primary"]:hover { background:var(--tr-gold-highlight); color:var(--tr-text-on-accent); border:0; }
div[data-testid="stMetric"] { border:1px solid var(--tr-border-default); border-radius:12px; padding:12px; background:var(--tr-bg-raised); box-shadow:var(--tr-shadow-card); } div[data-testid="stMetricValue"] { color:var(--tr-gold-primary); font-size:1.3rem; font-variant-numeric:tabular-nums; } div[data-testid="stExpander"] { border:1px solid var(--tr-border-default); border-radius:12px; background:var(--tr-bg-surface); } div[data-testid="stJson"] { max-width:100%; overflow-x:auto; }
@media (max-width:760px) { .block-container { padding:.7rem 24px 4rem; }.workflow-steps { align-items:flex-start; flex-direction:column; gap:8px; }.workflow-steps i { display:none; }.signal-grid,.task-summary { grid-template-columns:1fr; gap:8px; }.section-head { display:block; margin-top:32px; }.section-head p { text-align:left; margin-top:6px; } div[data-testid="stHorizontalBlock"] { flex-direction:column !important; gap:.5rem !important; } div[data-testid="column"] { width:100% !important; flex:1 1 100% !important; min-width:0 !important; }.attempt-card { align-items:flex-start; flex-direction:column; }.flow-edge { grid-template-columns:1fr; }.flow-amount { text-align:left; }.flow-key { grid-column:auto; } code,pre { white-space:pre-wrap !important; word-break:break-word !important; } }
</style>
"""
