"""Independent Streamlit component for receipt-backed service comparison."""

from __future__ import annotations

from typing import Any

from trust_receipt.history import HistoryCategory, ReceiptSourceRef, ServiceComparison, ServiceHistoryProjection

_METRICS = (
    ("首次通过", "first_pass_count", HistoryCategory.FIRST_PASS),
    ("修复后通过", "fixed_pass_count", HistoryCategory.FIXED_PASS),
    ("未通过", "fail_count", HistoryCategory.FAIL),
    ("无法判断", "inconclusive_count", HistoryCategory.INCONCLUSIVE),
)


def _render_source(st: Any, source: ReceiptSourceRef) -> None:
    label = f"{source.task_id} · {source.outcome.value} · {source.receipt_hash[:12]}…"
    st.markdown(f"**{label}**")
    st.caption(f"回执来源：{source.source_ref}")
    if source.public_uri:
        st.link_button("查看公开回执", source.public_uri)


def _render_sources(st: Any, history: ServiceHistoryProjection, category: HistoryCategory) -> None:
    sources = history.sources_for(category)
    if not sources:
        st.caption("没有对应的已核验任务。")
        return
    for source in sources:
        _render_source(st, source)


def _render_service(st: Any, history: ServiceHistoryProjection) -> None:
    st.subheader(history.service_name)
    st.caption(f"服务 ID：{history.service_id} · 任务类型：{history.task_type}")
    top = st.columns(2)
    top[0].metric("已核验任务", history.verified_task_count)
    top[1].metric("可验证回执", history.verifiable_receipt_count)
    with st.expander(f"全部可验证回执（{history.verifiable_receipt_count}）"):
        for source in history.receipt_refs:
            _render_source(st, source)
    for label, field, category in _METRICS:
        count = getattr(history, field)
        st.metric(label, count)
        with st.expander(f"{label}来源（{count}）"):
            _render_sources(st, history, category)
    latest = history.latest_delivery_at.isoformat() if history.latest_delivery_at else "暂无"
    st.caption(f"最近交付：{latest}")
    if history.receipt_refs:
        with st.expander("最近交付来源"):
            _render_source(st, history.receipt_refs[-1])


def render_service_history(
    comparison: ServiceComparison,
    *,
    streamlit_api: Any | None = None,
    key: str = "m10-service-history",
) -> str | None:
    """Render two histories without ranking them; return only an explicit user choice."""
    if streamlit_api is None:
        import streamlit as streamlit_api

    st = streamlit_api
    st.header("服务历史对比")
    st.caption("以下事实仅来自已核验回执；无法判断不计为未通过，系统不会生成综合评分。")
    columns = st.columns(2)
    for column, history in zip(columns, comparison.services, strict=True):
        with column:
            _render_service(st, history)

    labels = {service.service_id: service.service_name for service in comparison.services}
    selected = st.radio(
        "人工选择服务",
        options=tuple(labels),
        index=None,
        format_func=lambda service_id: f"{labels[service_id]} · {service_id}",
        key=f"{key}-choice",
        help="选择由您确认，不代表系统推荐。",
    )
    if st.button("确认选择", type="primary", disabled=selected is None, key=f"{key}-confirm"):
        return selected
    return None


__all__ = ["render_service_history"]
