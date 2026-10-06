"""Responsive Streamlit product page for the M5 vertical demonstration."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from uuid import uuid4

import streamlit as st
from pydantic import ValidationError

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from app.runtime import AppRuntime, ConfigurationBlocked, create_runtime
from app.styles import APP_CSS
from trust_receipt.agents import TaskSpecCandidate
from trust_receipt.models import ExclusionRule, ExclusionRuleType, VerificationOutcome

PROVIDERS = ("离线 fixture 演示", "OpenAI 真实模型", "DeepSeek 真实模型")
EVIDENCE_MODES = ("完整 fixture 证据", "模拟证据不可用", "真实 Sepolia RPC")


def _step(number: int, title: str, subtitle: str) -> None:
    st.markdown(
        f'<div class="step-title"><span class="step-number">{number}</span>'
        f'<div><strong>{title}</strong><br><small>{subtitle}</small></div></div>',
        unsafe_allow_html=True,
    )


def _runtime() -> AppRuntime | None:
    provider = st.sidebar.selectbox("AI 路径", PROVIDERS, key="provider")
    if "workspace_id" not in st.session_state:
        st.session_state.workspace_id = f"workspace-{uuid4().hex[:8]}"
    workspace_id = st.sidebar.text_input(
        "工作区 ID",
        key="workspace_id",
        help="保存此 ID 可在页面或进程重启后恢复最新任务和 attempt。",
    )
    evidence_label = st.sidebar.radio(
        "独立证据",
        EVIDENCE_MODES,
        key="evidence_label",
    )
    config = (provider, evidence_label, workspace_id)
    if st.session_state.get("runtime_config") != config:
        for key in ("runtime", "candidate", "task", "executions", "draft_error"):
            st.session_state.pop(key, None)
        st.session_state.runtime_config = config
    if "runtime" not in st.session_state:
        try:
            st.session_state.runtime = create_runtime(
                project_root=PROJECT_ROOT,
                session_id=workspace_id,
                provider=provider,
                evidence_mode=evidence_label,
            )
            restored = st.session_state.runtime.workflow.restore_latest()
            if restored is not None:
                st.session_state.task, st.session_state.executions = restored
                st.session_state.restore_notice = True
        except ConfigurationBlocked as error:
            st.error(str(error))
            st.info("可切换到“离线 fixture 演示”继续；该路径会明确标注，且不会冒充真实模型调用。")
            return None
    return st.session_state.runtime


def _candidate_editor(runtime: AppRuntime) -> None:
    candidate = st.session_state.candidate
    if candidate.missing_fields:
        st.warning("缺失字段：" + "、".join(field.value for field in candidate.missing_fields))
    for issue in candidate.ambiguities:
        st.warning(f"歧义 · {issue.target.value}：{issue.description}")
    for question in candidate.clarification_questions:
        st.caption(f"待确认：{question}")

    with st.form("task_editor"):
        left, right = st.columns(2)
        with left:
            chain_id = st.number_input("Chain ID", min_value=1, value=candidate.chain_id or 11_155_111)
            token = st.text_input("代币地址", value=candidate.token_address or "")
            treasuries = st.text_area(
                "资金账户（每行一个，最多两个）",
                value="\n".join(candidate.treasury_addresses or ()),
            )
            recipients = st.text_area(
                "资助对象（每行一个）",
                value="\n".join(candidate.recipient_addresses or ()),
            )
        with right:
            start_block = st.number_input("起始区块（含）", min_value=0, value=candidate.start_block or 0)
            end_block = st.number_input("结束区块（含）", min_value=0, value=candidate.end_block or 0)
            exclude_internal = st.checkbox(
                "排除资金账户之间的内部互转",
                value=bool(candidate.exclusion_rules),
            )
            st.text_input("记录上限", value="200", disabled=True)
        confirmed = st.checkbox("我已核对以上任务边界并确认执行")
        submitted = st.form_submit_button("确认并冻结任务", type="primary")

    if not submitted:
        return
    if not confirmed:
        st.error("任务未确认：请先勾选任务边界确认框。")
        return
    payload = {
        "schema_version": "1.0",
        "candidate_id": candidate.candidate_id,
        "chain_id": int(chain_id),
        "token_address": token.strip() or None,
        "treasury_addresses": _lines(treasuries) or None,
        "recipient_addresses": _lines(recipients) or None,
        "start_block": int(start_block),
        "end_block": int(end_block),
        "exclusion_rules": (
            [
                ExclusionRule(
                    rule_id="exclude-treasury-internal",
                    rule_type=ExclusionRuleType.EXCLUDE_TREASURY_INTERNAL,
                    reason="Transfers between confirmed treasury accounts are not grants.",
                ).model_dump(mode="json")
            ]
            if exclude_internal
            else []
        ),
        "max_records": 200,
        "ambiguities": [],
        "missing_fields": [],
        "clarification_questions": [],
    }
    try:
        edited = TaskSpecCandidate.model_validate(payload)
        st.session_state.candidate = edited
        st.session_state.task = runtime.workflow.confirm_task(edited)
        st.session_state.executions = []
        st.rerun()
    except (ValidationError, ValueError) as error:
        st.error(f"任务未确认：{error}")
        st.info("字段仍可修改；只有通过 Pydantic 与确定性边界后才会冻结任务。")


def _lines(value: str) -> list[str]:
    return [line.strip() for line in value.splitlines() if line.strip()]


def _run_attempt(runtime: AppRuntime) -> None:
    task = st.session_state.task
    _step(3, "选择团队控制服务并执行", "未确认任务时此步骤不会出现")
    service_label = st.radio("报表服务", tuple(runtime.services), horizontal=True)
    executions = st.session_state.get("executions", [])
    can_run = not executions or (
        len(executions) == 1
        and executions[-1].result.outcome in {VerificationOutcome.FAIL, VerificationOutcome.INCONCLUSIVE}
    )
    button_label = "执行 attempt 1" if not executions else "执行唯一一次补交 / 换源 attempt 2"
    if st.button(button_label, type="primary", disabled=not can_run):
        try:
            with st.spinner("签名交付 → 白名单计划 → 确定性验证 → 本地回执…"):
                execution = runtime.workflow.run_attempt(task.task_id, runtime.services[service_label])
            st.session_state.executions = [*executions, execution]
            st.rerun()
        except Exception as error:
            st.error(f"执行被安全边界拒绝：{error}")
            st.info("未通过 AI/Pydantic/白名单校验的交付不会进入验收或消耗 attempt；请修改任务或配置后重试。")
    if executions and not can_run:
        st.caption("当前任务已通过，或两个 attempt 已用完；历史记录仍完整保留。")


def _render_attempts() -> None:
    executions = st.session_state.get("executions", [])
    if not executions:
        return
    _step(4, "验收结果与 attempt 历史", "后一次不会覆盖前一次")
    for index, execution in enumerate(executions, start=1):
        result = execution.result
        with st.container(border=True):
            st.markdown(
                f'<div class="attempt-card outcome-{result.outcome.value}"><small>Attempt {index}</small>'
                f'<div class="metric-value">{result.outcome.value}</div>'
                f'<span class="badge badge-submitted">服务交付 SUBMITTED</span>'
                f'<span class="badge badge-not-submitted">公共发布 NOT_SUBMITTED</span></div>',
                unsafe_allow_html=True,
            )
            total, count, findings = st.columns(3)
            total.metric("确定性金额（最小单位）", result.calculated_total_base_units or "—")
            count.metric("确定性事件数", result.calculated_count if result.calculated_count is not None else "—")
            findings.metric("Finding", len(result.findings))
            if result.outcome is VerificationOutcome.INCONCLUSIVE:
                st.warning(f"证据不足，不能形成服务负面结论：{result.inconclusive_reason}")
            if execution.explanation:
                st.info("受限解释：" + execution.explanation.summary)
            for error in execution.ai_errors:
                st.warning(error)
            if execution.evidence_diagnostics:
                st.markdown("**证据来源状态**")
                for diagnostic in execution.evidence_diagnostics:
                    st.markdown(
                        f'<div class="status-card"><strong>{diagnostic.source}</strong> · '
                        f'{diagnostic.role}<br><span class="badge badge-submitted">'
                        f'{diagnostic.status}</span> {diagnostic.detail}<br>'
                        f'<small>{diagnostic.pages} pages · {diagnostic.records} records · '
                        f'{diagnostic.elapsed_ms} ms</small></div>',
                        unsafe_allow_html=True,
                    )
            elif result.reference_sources:
                st.markdown("**证据来源状态**")
                for source in result.reference_sources:
                    st.write(
                        f"{source.source.value} · complete={source.complete} · "
                        f"retrieved_at={source.retrieved_at.isoformat()}"
                    )
            if result.findings:
                st.markdown("**Finding 明细**")
                for finding in result.findings:
                    st.markdown(
                        f'<div class="finding-card"><strong>{finding.finding_type.value}</strong> · '
                        f'{finding.severity.value} / {finding.status.value}<br>{finding.explanation}<br>'
                        f'<span class="mono">证据：{", ".join(finding.evidence_refs)}</span></div>',
                        unsafe_allow_html=True,
                    )
            if execution.follow_up:
                st.markdown("**补查 / 后续建议（封闭动作）**")
                for suggestion in execution.follow_up.suggestions:
                    st.write(f"{suggestion.action.value} — {suggestion.rationale}")
            with st.expander("本地回执预览", expanded=index == len(executions)):
                receipt_json = execution.receipt.model_dump(mode="json")
                st.caption("M6 公共发布与写链未执行；publication.chain_status 保持 NOT_SUBMITTED。")
                st.json(receipt_json)
                st.download_button(
                    "下载本地 JSON 回执",
                    data=json.dumps(receipt_json, ensure_ascii=False, indent=2),
                    file_name=f"attempt-{index}-receipt.json",
                    mime="application/json",
                    key=f"download-{index}",
                )


def main() -> None:
    st.set_page_config(page_title="信据 Agent", page_icon="✓", layout="wide")
    st.markdown(APP_CSS, unsafe_allow_html=True)
    st.markdown(
        '<div class="hero"><div class="eyebrow">Trust, but reproduce</div>'
        '<h1>链上报表，<br>验到每一笔。</h1>'
        '<p>确认边界后才执行。金额、Finding 与三态结论只来自确定性引擎；AI 只组织候选、解释和受限建议。</p></div>',
        unsafe_allow_html=True,
    )
    runtime = _runtime()
    if runtime is None:
        return
    st.markdown(
        f'<div class="mode-banner"><strong>当前路径：</strong>{runtime.mode_label}</div>',
        unsafe_allow_html=True,
    )
    st.caption(f"证据路径：{runtime.evidence_label}")
    if st.session_state.pop("restore_notice", False):
        st.info("已从该工作区的 SQLite 与本地回执恢复最新任务；历史 AI 文本未重新生成。")

    _step(1, "描述验收任务", "自然语言只用于生成可修改候选")
    request = st.text_area(
        "任务描述",
        value="核对 Sepolia 上两个资金账户在区块 1000–1010 对两个资助对象的代币拨款，排除内部互转。",
        height=110,
    )
    if st.button("生成任务候选"):
        try:
            st.session_state.candidate = runtime.workflow.draft_task(request)
            st.session_state.pop("draft_error", None)
        except Exception as error:
            st.session_state.candidate = runtime.editable_seed
            st.session_state.draft_error = str(error)
        st.rerun()
    if "draft_error" in st.session_state:
        st.error("模型输出被拒绝：" + st.session_state.draft_error)
        st.info("已打开可修改字段，但没有自动确认或执行。")

    if "candidate" in st.session_state and "task" not in st.session_state:
        _step(2, "修改并确认 TaskSpec", "确认后生成不可变 spec_hash")
        _candidate_editor(runtime)
    elif "task" in st.session_state:
        task = st.session_state.task
        _step(2, "TaskSpec 已确认", "执行范围已冻结")
        st.success(f"任务 {task.task_id} 已确认")
        st.code(task.spec_hash, language=None)
        _run_attempt(runtime)
        _render_attempts()


if __name__ == "__main__":
    main()
