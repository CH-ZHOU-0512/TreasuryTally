"""Lazy private downloads; renderer configuration belongs to deployment only."""

import os
from functools import partial

import streamlit as st

from trust_receipt.hashing import content_hash
from trust_receipt.reporting import (
    EChartsRenderer,
    export_docx,
    export_html,
    export_pdf,
    graph_png,
    graph_svg,
)


@st.cache_resource
def application_renderer():
    """One application instance, shared across sessions and all formats.

    Never discover a bare PATH Node: the deployment launcher owns isolation.
    Environment changes require an application restart.
    """
    return EChartsRenderer(
        node_path=os.environ.get("REPORT_RENDERER_NODE") or "/opt/trust-receipt-renderer/renderer-node",
        modules_path=os.environ.get("REPORT_RENDERER_MODULES") or "/opt/trust-receipt-renderer/node_modules",
    )


def document_exporters():
    renderer = application_renderer()
    return partial(export_docx, renderer=renderer), partial(export_pdf, renderer=renderer)


def render_export_download(st, report, *, label, suffix, mime, export):
    """No worker runs until requested; cache is bound to the entire frozen view."""
    key = f"report-export:{content_hash(report.model_dump_json().encode())}:{suffix}"
    if key not in st.session_state:
        if st.button(f"生成{label}", key=key + ":create", use_container_width=True):
            try:
                with st.spinner(f"正在生成{label}…"):
                    st.session_state[key] = export(report)
                st.rerun()
            except (ValueError, OSError, RuntimeError, ImportError):
                st.error(f"{label}导出暂不可用（组件缺失、繁忙或生成失败）；原 JSON 回执仍可下载。")
    else:
        st.download_button(
            label, st.session_state[key], f"treasury-report-{report.current.attempt}.{suffix}", mime,
            key=key + ":download", use_container_width=True,
        )


def render_additional_exports(st, report):
    st.caption("以下文件属于最新业务报告的阅读副本；有两次交付时包含原核对历史，不是公开发布。")
    renderer = application_renderer()
    for label, suffix, mime, exporter in (
        ("离线 HTML 报告", "html", "text/html", export_html),
        ("资金流 PNG", "png", "image/png", graph_png),
        ("资金流 SVG", "svg", "image/svg+xml", graph_svg),
    ):
        render_export_download(
            st, report, label=label, suffix=suffix, mime=mime,
            export=partial(exporter, renderer=renderer),
        )
    st.caption("静态资金流仅展示最多前 4 条记录，拥挤并行线仅首条；完整事件见报告明细与原回执。")
