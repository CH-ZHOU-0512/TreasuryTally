"""A single business reading surface; all facts and amounts come from reporting."""

from html import escape

from trust_receipt.hashing import content_hash


def render_business_report(st, report, *, graph=None, exports=None, receipt_json: str):
    current = report.current
    st.html(
        f'<section class="attempt-card outcome-{escape(report.outcome.value)}">'
        f'<div><small>第 {current.attempt} 次核对 · {escape(report.source_mode_label)}</small>'
        f'<h2 class="attempt-title">{escape(report.conclusion)}</h2></div></section>'
    )
    st.caption(report.scope.summary)
    st.caption(f"核验资产：{report.scope.token.short}")
    st.caption("资金账户：" + "、".join(item.short for item in report.scope.treasuries))
    st.caption("资助对象：" + "、".join(item.short for item in report.scope.recipients))
    for exclusion in report.scope.exclusions:
        st.caption(exclusion)
    amounts = (current.claimed, current.calculated, current.difference)
    units = {amount.unit for amount in amounts if amount is not None}
    columns = st.columns(3)
    for column, label, amount in zip(
        columns, ("报表金额", "链上有效金额", "差额（报表 − 链上）"),
        amounts, strict=True,
    ):
        with column:
            st.metric(
                label, amount.display if amount is not None else "无法确定",
                help=(f"{amount.unit}；精确最小单位：{amount.base_units}" if amount else current.difference_reason),
            )
            if len(units) > 1 and amount is not None:
                st.caption(amount.unit)
    if len(units) == 1:
        st.caption(current.claimed.unit)
    if current.difference_reason:
        reason = current.difference_reason
        if report.outcome.value == "INCONCLUSIVE":
            reason = "证据不足，不能形成服务负面结论：" + reason
        st.warning(reason)
    for uncertainty in current.uncertainties:
        st.caption(uncertainty)

    if current.findings:
        st.markdown("#### 需要处理的差异")
        grouped = {}
        for finding in current.findings:
            grouped.setdefault((finding.finding_type, finding.confirmed), []).append(finding)
        for number, items in enumerate(grouped.values(), 1):
            finding = items[0]
            st.html(
                '<div class="finding-card">'
                f'<strong>{number}. {escape(finding.title)}</strong>'
                f'<p>{escape(finding.description)}</p>'
                f'<p>{escape(finding.recommendation)}</p>'
                f'<small>{len(items)} 条{"已确认差异" if finding.confirmed else "待核实线索"}</small></div>'
            )
    if report.previous is not None:
        st.markdown("#### 修复前后")
        st.caption(report.repair_label)
        st.dataframe([
            {"核对": f"第 {item.attempt} 次", "结论": item.outcome_label,
             "报表金额": f"{item.claimed.display} {item.claimed.unit}",
             "有效金额": f"{item.calculated.display} {item.calculated.unit}" if item.calculated else "无法确定",
             "差额": f"{item.difference.display} {item.difference.unit}" if item.difference else "无法确定",
             "差异数": len(item.findings)} for item in (report.previous, current)
        ], hide_index=True, width="stretch")

    st.markdown("#### 资金流与差异")
    if graph is not None:
        st.html(graph(report, theme="dark"))
    elif not current.graph_available:
        st.info("没有可重建的已保存资金流图，原回执结论仍保留。")
    else:
        st.caption("资金流图组件尚未接入，不能把技术准备版本作为完整报告交付。")
    st.write(report.next_step)
    st.markdown("#### 保存报告")
    buttons = st.columns(3)
    with buttons[0]:
        st.download_button(
            "原 JSON 回执", receipt_json, f"attempt-{current.attempt}-receipt.json",
            "application/json", key=f"report-json-{current.receipt_hash}", use_container_width=True,
        )
    if exports is not None:
        for column, label, suffix, mime, export in (
            (buttons[1], "Word 报告", "docx",
             "application/vnd.openxmlformats-officedocument.wordprocessingml.document", exports[0]),
            (buttons[2], "PDF 报告", "pdf", "application/pdf", exports[1]),
        ):
            with column:
                key = f"report-export:{content_hash(report.model_dump_json().encode())}:{suffix}"
                if key not in st.session_state:
                    if st.button(f"生成{label}", key=key + ":create", use_container_width=True):
                        try:
                            with st.spinner(f"正在生成{label}…"):
                                st.session_state[key] = export(report)
                            st.rerun()
                        except (ValueError, OSError, RuntimeError):
                            st.error(f"{label}暂时无法生成；原回执已保留，请联系维护者。")
                else:
                    st.download_button(
                        label, st.session_state[key], f"treasury-report-{current.attempt}.{suffix}", mime,
                        key=key + ":download", use_container_width=True,
                    )
    for limitation in report.limitations:
        st.caption(limitation)
    st.caption(report.notice)
