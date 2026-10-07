"""Local ECharts presentation of existing facts; no monetary JavaScript numbers."""
# ruff: noqa: RUF001

import base64
import hashlib
import json
from html import escape
from importlib.resources import files
from typing import Literal

from trust_receipt.reporting.models import BusinessReportView

ECHARTS_VERSION = "6.0.0"
ECHARTS_SHA256 = "baa8dfe7e1d9336b98e8986ba7e20ea15e7cdbea1ef42a59d59478632fa45a1d"


def echarts_javascript() -> str:
    """Return the unchanged, pinned upstream bundle, never caller-supplied JS."""
    content = files("trust_receipt.reporting").joinpath("assets/echarts/echarts-6.0.0.min.js").read_bytes()
    if hashlib.sha256(content).hexdigest() != ECHARTS_SHA256:
        raise ValueError("ECharts packaged asset integrity mismatch")
    return content.decode("utf-8")


def echarts_flow_option(
    view: BusinessReportView,
    *,
    attempt: Literal["current", "previous"] = "current",
    offset: int = 0,
    limit: int = 12,
    theme: Literal["dark", "print"] = "dark",
) -> dict:
    """Plain JSON graph option. Pagination is explicit, not evidence sampling.

    Exact amounts stay strings in edge names/tooltips; edge width is constant.
    The caller can request each page of the full saved event list.
    """
    if attempt not in {"current", "previous"} or theme not in {"dark", "print"}:
        raise ValueError("unsupported graph attempt or theme")
    if type(offset) is not int or offset < 0 or type(limit) is not int or not 1 <= limit <= 20:
        raise ValueError("offset must be nonnegative; limit must be 1..20")
    report = view.current if attempt == "current" else view.previous
    if report is None:
        raise ValueError("no saved previous report")
    total = len(report.flow_rows)
    if total > 200:
        raise ValueError("more than 200 saved events; split the task")
    if offset >= total and offset != 0:
        raise ValueError("offset outside saved events")
    rows = report.flow_rows[offset : offset + limit]
    dark = theme == "dark"
    foreground, background = ("#f5f5f5", "#191b20") if dark else ("#111111", "#ffffff")
    accent, muted = ("#d9c08a", "#c8c8cc") if dark else ("#887044", "#444444")
    treasuries = {a.full.lower() for a in view.scope.treasuries}
    recipients = {a.full.lower() for a in view.scope.recipients}
    addresses = {}
    for row in rows:
        for address in (row.sender, row.recipient):
            addresses.setdefault(address.full.lower(), address)
    groups = [[], []]
    for key, address in addresses.items():
        groups[0 if key in treasuries else 1].append((key, address))
    nodes = []
    for column, group in enumerate(groups):
        for index, (key, address) in enumerate(group):
            role = "资金账户" if key in treasuries else ("接收对象" if key in recipients else "其他账户")
            nodes.append(
                {
                    "id": key,
                    "name": f"{role}\n{address.full}",
                    "x": 0 if column == 0 else 500,
                    "y": (index + 1) * 500 // (len(group) + 1),
                    "symbol": "roundRect" if key in treasuries else "circle",
                    "symbolSize": 36,
                    "label": {"formatter": f"{role}\n{address.short}"},
                    "itemStyle": {"color": background, "borderColor": accent, "borderWidth": 2},
                }
            )
    links = []
    pairs = {}
    for row in rows:
        source, target = row.sender.full.lower(), row.recipient.full.lower()
        pair = (source, target)
        ordinal = pairs.get(pair, 0)
        pairs[pair] = ordinal + 1
        text = f"{row.status_label}\n{row.amount.display} {row.amount.unit}"
        links.append(
            {
                "source": source,
                "target": target,
                "name": f"{text}\n{row.source_label}\n{row.event_ref}",
                "edge_id": row.edge_id,
                "event_ref": row.event_ref,
                "source_label": row.source_label,
                "status": row.status,
                "amount_base_units": row.amount.base_units,
                "finding_ids": list(row.finding_ids),
                "label": {"formatter": row.status_label},
                "lineStyle": {
                    "color": accent,
                    "width": 2,
                    "type": "solid" if row.status == "MATCHED" else "dashed",
                    "curveness": (ordinal % 4 + 1) / 10,
                    "opacity": 1,
                },
            }
        )
    range_text = f"{offset + 1}–{offset + len(rows)} / {total} 条" if rows else "无可展示的保存事件"
    return {
        "animation": False,
        "backgroundColor": background,
        "textStyle": {"color": foreground, "fontSize": 12, "fontFamily": "sans-serif"},
        "title": {
            "text": f"资金流向 · 第 {report.attempt} 次核验",
            "subtext": f"{range_text} · {report.outcome_label}\n{view.source_mode_label}",
            "textStyle": {"color": foreground, "fontSize": 16},
            "subtextStyle": {"color": muted, "fontSize": 12},
            "left": 12,
            "top": 12,
        },
        "tooltip": {"trigger": "item", "renderMode": "richText", "formatter": "{b}", "confine": True},
        "aria": {"enabled": True, "label": {"description": f"资金流向。{range_text}。{view.conclusion}"}},
        "series": [
            {
                "type": "graph",
                "layout": "none",
                "left": "16%",
                "right": "16%",
                "top": 116,
                "bottom": 56,
                "roam": True,
                "scaleLimit": {"min": 1, "max": 4},
                "data": nodes,
                "links": links,
                "edgeSymbol": ["none", "arrow"],
                "edgeSymbolSize": [0, 10],
                "label": {"show": True, "position": "bottom", "color": foreground, "fontSize": 12},
                "edgeLabel": {"show": True, "color": foreground, "fontSize": 12},
                "emphasis": {"focus": "adjacency"},
            }
        ],
    }


def _script_hash(script: str) -> str:
    return base64.b64encode(hashlib.sha256(script.encode("utf-8")).digest()).decode("ascii")


def echarts_component_html(view: BusinessReportView, **kwargs) -> str:
    """Self-contained sandboxable graph; no CDN, network, templates or user JS.

    This is a read-only component, not the full HTML report/export adapter.
    Recreate it for each requested pagination/attempt selection in the UI.
    """
    option = echarts_flow_option(view, **kwargs)
    # Script-element escaping is separate from HTML escaping. Never interpolate
    # a user-controlled field into executable JavaScript or its formatter.
    data = json.dumps(option, ensure_ascii=True, separators=(",", ":"))
    data = data.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    runtime = echarts_javascript().replace("</script", "<\\/script")
    boot = (
        'const root=document.getElementById("flow");'
        'const chart=echarts.init(root,null,{renderer:"svg"});'
        'chart.setOption(JSON.parse(document.getElementById("flow-data").textContent));'
        'new ResizeObserver(()=>chart.resize()).observe(root);'
    )
    policy = (
        "default-src 'none'; connect-src 'none'; img-src data:; style-src 'unsafe-inline'; "
        f"script-src 'sha256-{_script_hash(runtime)}' 'sha256-{_script_hash(boot)}'"
    )
    background = option["backgroundColor"]
    text_color = option["textStyle"]["color"]
    return (
        '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<meta http-equiv="Content-Security-Policy" content="{escape(policy, quote=True)}">'
        '<title>资金流向图</title><style>'
        f'body{{margin:0;background:{background};color:{text_color};font:12px sans-serif}}'
        '#flow{width:100%;height:480px}p{padding:0 12px;line-height:1.6;margin:0}'
        '</style></head><body><div id="flow" role="img" aria-label="已保存证据的资金流向图"></div>'
        '<p>箭头表示转账方向；线宽不表示金额。点击连线查看精确金额、来源和事件引用。'
        '本图按页展示，完整事件仍以报告明细为准；不重新访问链上或生成新结论。</p>'
        f'<script id="flow-data" type="application/json">{data}</script>'
        f'<script>{runtime}</script><script>{boot}</script></body></html>'
    )
