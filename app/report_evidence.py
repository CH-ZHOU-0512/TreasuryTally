"""One optional evidence entry; business reports remain free of technical directories."""

from app.commitments import render_commitments
from app.m9_components import render_repair_comparison, render_rework_package
from app.m9_public import render_public_history


def render_report_evidence(st, runtime, executions, artifacts, *, allow_actions, publish, report=None):
    with st.expander("验证依据 / 技术详情", expanded=st.session_state.get("show-report-evidence", False)):
        attempt = st.selectbox(
            "查看哪次核对", tuple(range(1, len(executions) + 1)), index=len(executions) - 1,
            format_func=lambda number: f"第 {number} 次核对", key="report-evidence-attempt",
        )
        execution = executions[attempt - 1]
        section = st.selectbox(
            "查看依据类别", ("核验范围与来源", "交易与差异依据", "AI 说明", "任务与签名",
                              "回执与修复历史", "分享与公开验证"), key="report-evidence-section",
        )
        if section == "核验范围与来源":
            st.json(st.session_state.task.model_dump(mode="json"))
            st.caption("以下为当前运行配置，不代表历史快照当时使用的模型或证据来源。")
            st.write("当前模型配置：", runtime.mode_label)
            st.write("当前独立证据配置：", runtime.evidence_label)
            if execution.evidence_diagnostics:
                st.dataframe([
                    {"来源": item.source, "角色": item.role, "状态": item.status,
                     "页数": item.pages, "记录数": item.records, "耗时ms": item.elapsed_ms,
                     "说明": item.detail} for item in execution.evidence_diagnostics
                ], hide_index=True, width="stretch")
            else:
                st.json([item.model_dump(mode="json") for item in execution.result.reference_sources])
        elif section == "交易与差异依据":
            snapshot = (
                report.current if report is not None and report.current.attempt == attempt
                else report.previous if report is not None else None
            )
            if snapshot is not None and snapshot.flow_rows:
                st.dataframe([
                    {"付款账户": row.sender.full, "接收账户": row.recipient.full,
                     "金额": f"{row.amount.display} {row.amount.unit}", "状态": row.status_label,
                     "来源": row.source_label, "事件身份": row.event_ref}
                    for row in snapshot.flow_rows
                ], hide_index=True, width="stretch")
            st.json([item.model_dump(mode="json") for item in execution.result.findings])
            if execution.fund_flow is not None:
                st.json(execution.fund_flow.model_dump(mode="json"))
            else:
                st.info("历史未保留完整转账投影；原回执仍可查看与验证。")
        elif section == "AI 说明":
            if execution.explanation:
                st.write(execution.explanation.summary)
            else:
                st.caption("没有可展示的 AI 说明；业务结论来自确定性程序。")
            for error in execution.ai_errors:
                st.warning(error)
            if execution.follow_up:
                st.json(execution.follow_up.model_dump(mode="json"))
        elif section == "任务与签名":
            pairs = st.session_state.get("commitment_pairs", [])
            pair = pairs[attempt - 1] if attempt <= len(pairs) else None
            task_commitment, delivery, signer = pair or (None, None, None)
            render_commitments(
                st.session_state.task, task_commitment, delivery, execution.submission,
                signer, runtime.commitment_anchor_status,
            )
        elif section == "回执与修复历史":
            st.json(execution.receipt.model_dump(mode="json"))
            st.json(artifacts.revisions[attempt - 1].model_dump(mode="json"))
            if artifacts.rework_package is not None:
                render_rework_package(st, artifacts.rework_package)
            if artifacts.comparison is not None:
                render_repair_comparison(st, artifacts.comparison)
        elif allow_actions:
            publish(runtime, execution, attempt - 1, artifacts)
            render_public_history(st, runtime, artifacts.receipts)
        else:
            st.caption("后台记录需要检查，公开操作已阻塞；原回执仍可查看与下载。")
