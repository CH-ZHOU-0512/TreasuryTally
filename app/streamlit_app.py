"""Responsive Streamlit product page for the M5 vertical demonstration."""

from __future__ import annotations

import json
import os
import sys
from dataclasses import replace
from html import escape
from pathlib import Path
from uuid import uuid4

import streamlit as st
from pydantic import ValidationError

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from app.branding import LOGO_PATH, logo_static_url
from app.case_intake import load_real_case
from app.commitments import render_commitments
from app.fund_flow import render_fund_flow
from app.m9_components import (
    render_public_verification,
    render_repair_comparison,
    render_rework_package,
)
from app.m9_public import render_public_explorer, render_public_history
from app.report_experience import (
    amount_summary,
    contract_example_bytes,
    finding_copy,
    format_token_amount,
    reference_decimals,
    strict_template_bytes,
)
from app.runtime import AppRuntime, ConfigurationBlocked, create_runtime
from app.service_history import render_workspace_history
from app.styles import APP_CSS
from trust_receipt.agents import TaskSpecCandidate
from trust_receipt.hashing import content_hash
from trust_receipt.m9 import PublicReceiptReference, PublicReferenceKind, verify_public_reference
from trust_receipt.models import (
    ExclusionRule,
    ExclusionRuleType,
    PublicationChainStatus,
    VerificationOutcome,
)
from trust_receipt.orchestration.m9 import PublisherReceiptResolver, build_m9_artifacts
from trust_receipt.services.upload import UploadedReport, UploadedReportService

PROVIDERS = ("离线 fixture 演示", "OpenAI 真实模型", "DeepSeek 真实模型")
EVIDENCE_MODES = ("完整 fixture 证据", "模拟证据不可用", "真实 Sepolia RPC")


def _live_only() -> bool:
    return os.environ.get("APP_REQUIRE_LIVE", "").strip().lower() in {"1", "true", "yes"}


def _section(title: str, subtitle: str) -> None:
    st.markdown(
        '<div class="section-head"><div>'
        f'<h2>{escape(title)}</h2></div>'
        f'<p>{escape(subtitle)}</p></div>',
        unsafe_allow_html=True,
    )


def _product_header() -> None:
    logo_url = escape(logo_static_url(st.get_option("server.baseUrlPath")), quote=True)
    environment = "样例演示 · 非真实链上证据"
    if _live_only() or st.session_state.get("evidence_label") == "真实 Sepolia RPC":
        environment = "Sepolia · 真实只读核验"
    st.markdown(
        '<div class="product-bar"><div class="brand">'
        f'<img class="brand-logo" src="{logo_url}" alt="信据品牌 Logo" width="52" height="52">'
        f'<span>信据 Agent</span></div><span class="env-chip"><i class="env-dot"></i>{escape(environment)}</span></div>'
        '<section class="hero-main"><div class="hero-copy"><div class="eyebrow">链上报表验收工具</div>'
        '<h1>核对服务商报表与链上资金流</h1>'
        '<p>生成可复现的验收回执。金额与结论由确定性程序计算，技术依据按需展开。</p></div>'
        '<div class="hero-emblem" aria-hidden="true">'
        f'<img src="{logo_url}" alt="" width="144" height="144"></div></section>'
        '<nav class="workflow-steps" aria-label="验收流程">'
        '<span><b>1</b> 上传报表</span><i>→</i><span><b>2</b> 确认范围</span><i>→</i>'
        '<span><b>3</b> 链上核验</span></nav>',
        unsafe_allow_html=True,
    )


def _runtime() -> AppRuntime | None:
    live_only = _live_only()
    providers = ("DeepSeek 真实模型",) if live_only else PROVIDERS
    evidence_modes = ("真实 Sepolia RPC",) if live_only else EVIDENCE_MODES
    with st.expander("运行配置", expanded=False):
        provider_col, evidence_col, workspace_col = st.columns((1, 1.25, 1))
        with provider_col:
            provider = st.selectbox("AI 路径", providers, key="provider")
        if "workspace_id" not in st.session_state:
            st.session_state.workspace_id = f"workspace-{uuid4().hex[:8]}"
        with evidence_col:
            evidence_label = st.radio("独立证据", evidence_modes, key="evidence_label", horizontal=True)
        with workspace_col:
            workspace_id = st.text_input(
                "工作区 ID",
                key="workspace_id",
                help="保存此 ID 可在页面或进程重启后恢复最新任务和 attempt。",
            )
        if live_only:
            st.caption("生产环境已锁定真实 DeepSeek 与真实 Sepolia RPC；不会回退为离线 fixture。")
    config = (provider, evidence_label, workspace_id)
    if st.session_state.get("runtime_config") != config:
        for key in (
            "runtime",
            "candidate",
            "task",
            "executions",
            "draft_error",
            "commitment_pairs",
            "uploaded_service",
            "uploaded_report_hash",
            "m10-next-service",
            "report-service",
        ):
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
            restored = st.session_state.runtime.m8_workflow.restore_latest()
            if restored is not None:
                st.session_state.task, st.session_state.executions, snapshots = restored
                st.session_state.commitment_pairs = [
                    (snapshot.task_commitment, snapshot.delivery_commitment, snapshot.expected_signer)
                    if snapshot is not None else None
                    for snapshot in snapshots
                ]
                st.session_state.restore_notice = True
        except (ConfigurationBlocked, ValueError) as error:
            st.session_state.pop("runtime", None)
            st.error(str(error))
            if not live_only:
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

    with st.container(border=True, key="panel-scope"):
        st.caption("候选内容可以修改。只有勾选确认并通过契约校验后，TaskSpec 才会冻结。")
        with st.form("task_editor"):
            left, right = st.columns(2)
            with left:
                st.markdown("**链与资产**")
                chain_id = st.number_input("Chain ID", min_value=1, value=candidate.chain_id or 11_155_111)
                token = st.text_input("代币地址", value=candidate.token_address or "")
                start_block = st.number_input("起始区块（含）", min_value=0, value=candidate.start_block or 0)
                end_block = st.number_input("结束区块（含）", min_value=0, value=candidate.end_block or 0)
            with right:
                st.markdown("**参与账户与规则**")
                treasuries = st.text_area(
                    "资金账户（每行一个，最多两个）", value="\n".join(candidate.treasury_addresses or ())
                )
                recipients = st.text_area(
                    "资助对象（每行一个）", value="\n".join(candidate.recipient_addresses or ())
                )
                exclude_internal = st.checkbox(
                    "排除资金账户之间的内部互转", value=bool(candidate.exclusion_rules)
                )
                st.text_input("记录上限", value="200", disabled=True)
            st.divider()
            confirmed = st.checkbox("我已核对链、资产、账户与区块边界，并确认冻结此任务")
            submitted = st.form_submit_button("确认并冻结 TaskSpec", type="primary", use_container_width=True)

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


def _task_summary() -> None:
    task = st.session_state.task
    st.markdown(
        '<div class="task-summary">'
        f'<div class="summary-cell"><small>Task ID</small><strong>{escape(str(task.task_id))}</strong></div>'
        f'<div class="summary-cell"><small>Network</small><strong>Sepolia · {task.chain_id}</strong></div>'
        '<div class="summary-cell"><small>Block range</small>'
        f'<strong>{task.start_block} — {task.end_block}</strong></div>'
        '</div>',
        unsafe_allow_html=True,
    )
    with st.expander("查看不可变任务指纹与完整边界"):
        st.code(task.spec_hash, language=None)
        st.json(task.model_dump(mode="json"))


def _run_attempt(runtime: AppRuntime) -> None:
    task = st.session_state.task
    executions = st.session_state.get("executions", [])
    can_run = not executions or (
        len(executions) == 1
        and executions[-1].result.outcome in {VerificationOutcome.FAIL, VerificationOutcome.INCONCLUSIVE}
    )
    if not can_run:
        st.caption("当前任务已通过，或两个 attempt 已用完。历史记录保持只追加，不会被覆盖。")
        return
    with st.container(border=True, key="panel-execution"):
        left, right = st.columns((1.25, 1))
        with left:
            choices = tuple(runtime.services)
            uploaded_service = st.session_state.get("uploaded_service")
            restoring_upload = bool(executions and executions[0].submission.service_id == "uploaded-report-intake")
            if uploaded_service is not None or restoring_upload:
                choices = ("已上传报表 · 作者签名未验证",)
            if "report-service" not in st.session_state and st.session_state.get("m10-next-service"):
                selected_id = st.session_state["m10-next-service"]
                selected_label = next(
                    (label for label, service in runtime.services.items() if service.service_id == selected_id), None,
                )
                if selected_label in choices:
                    st.session_state["report-service"] = selected_label
            if st.session_state.get("report-service") not in choices:
                st.session_state.pop("report-service", None)
            service_label = st.radio("报表服务", choices, horizontal=True, key="report-service")
            if executions:
                repaired = st.file_uploader(
                    "上传修复后的 JSON 报表（最后一次）", type=("json",), max_upload_size=1, key="repair-upload",
                )
                if repaired is not None:
                    try:
                        uploaded_service = UploadedReportService(
                            repaired.getvalue(), private_directory=runtime.upload_directory,
                        )
                        st.caption("本次将验收上传的修复报表；本地接收签名不证明原作者身份。")
                    except ValueError:
                        st.error("修复报表不符合 JSON 契约；请检查字段、金额整数与记录上限。")
                        return
                if restoring_upload and uploaded_service is None:
                    st.info("原上传任务已恢复。请上传修复报表后再提交；不会替换成演示服务报表。")
                    can_run = False
            st.caption("服务提交的是待验报告；最终金额与结论仍由独立证据和确定性引擎产生。")
        with right:
            button_label = "开始验收 · Attempt 1" if not executions else "补交或换源 · Attempt 2（最后一次）"
            if st.button(button_label, type="primary", disabled=not can_run, use_container_width=True):
                try:
                    with st.spinner("正在完成签名交付、证据读取、确定性核对与本地回执…"):
                        service = uploaded_service or runtime.services[service_label]
                        execution, snapshot = runtime.m8_workflow.run_attempt(task, service)
                    st.session_state.executions = [*executions, execution]
                    pairs = st.session_state.get("commitment_pairs", [])
                    st.session_state.commitment_pairs = [
                        *pairs,
                        (snapshot.task_commitment, snapshot.delivery_commitment, snapshot.expected_signer),
                    ]
                    st.rerun()
                except Exception as error:
                    st.error(f"执行被安全边界拒绝：{error}")
                    st.info("交付前校验失败会撤销请求；已进入验收的 attempt 不会回滚或自动重试。请检查恢复状态。")


def _replace_execution_receipt(index: int, receipt) -> None:
    executions = list(st.session_state.executions)
    executions[index] = replace(executions[index], receipt=receipt)
    st.session_state.executions = executions


def _render_publication(runtime: AppRuntime, execution, index: int, m9_artifacts) -> None:
    publication = execution.receipt.publication
    st.caption(runtime.publication_status)
    if publication.uri:
        st.code(publication.uri, language=None)
        st.caption(f"公开内容 SHA-256：{publication.content_hash}")
        verification_key = f"public-verification-{index}-{execution.receipt.receipt_hash}"
        if st.button(
            "独立重放公开回执",
            key=f"verify-public-{index}",
            disabled=runtime.publisher is None,
            use_container_width=True,
        ):
            reference = PublicReceiptReference(PublicReferenceKind.URI, publication.uri)
            resolver = PublisherReceiptResolver(runtime.publisher, execution.receipt, attempt=index + 1)
            st.session_state[verification_key] = verify_public_reference(
                reference,
                resolver,
            )
        if runtime.publisher is None:
            st.info("当前运行配置没有对应公共存储读取器，无法重新下载公开字节。")
        if verification_key in st.session_state:
            render_public_verification(st, st.session_state[verification_key])
    if publication.chain_status is PublicationChainStatus.FAILED:
        st.error(f"发布/链上状态 FAILED：{publication.error_code} · {publication.error_message or ''}")
        authorized = st.checkbox("我已核对失败原因并授权重新准备", key=f"recover-{index}")
        if st.button(
            "恢复为 NOT_SUBMITTED",
            key=f"recover-button-{index}",
            disabled=not authorized,
            use_container_width=True,
        ):
            try:
                recovered = runtime.publication_workflow.recover_failed(
                    execution.receipt, authorized=authorized
                )
                _replace_execution_receipt(index, recovered)
                st.rerun()
            except Exception as error:
                st.error(f"失败状态不能恢复：{error}")
        return
    if publication.uri is None:
        authorized = st.checkbox(
            "我授权公开这份脱敏 JSON 回执",
            key=f"publish-authorized-{index}",
        )
        if st.button(
            "发布公开 JSON 回执",
            key=f"publish-{index}",
            disabled=runtime.publisher is None or not authorized,
            use_container_width=True,
        ):
            try:
                published, _ = runtime.publication_workflow.publish(
                    execution.receipt,
                    runtime.publisher,
                    authorized=authorized,
                )
                _replace_execution_receipt(index, published)
                st.rerun()
            except Exception as error:
                st.error(f"公共发布失败：{error}")
        return
    st.caption(runtime.feedback_status)
    if publication.chain_status is PublicationChainStatus.NOT_SUBMITTED:
        authorized = st.checkbox(
            "我授权向 Sepolia ERC-8004 提交此 URI 与内容哈希",
            key=f"chain-authorized-{index}",
        )
        if st.button(
            "提交 ERC-8004 反馈",
            key=f"chain-submit-{index}",
            disabled=runtime.feedback_adapter is None or not authorized,
            use_container_width=True,
        ):
            try:
                submitted = runtime.publication_workflow.submit_feedback(
                    execution.receipt,
                    runtime.feedback_adapter,
                    authorized=authorized,
                )
                _replace_execution_receipt(index, submitted)
                st.rerun()
            except Exception as error:
                st.error(f"链上提交被安全边界拒绝：{error}")
    elif publication.chain_status is PublicationChainStatus.SUBMITTED:
        st.warning("交易已提交或广播结果未知；系统不会自动重发。请只执行读回核验。")
        if publication.transaction_hash:
            st.code(publication.transaction_hash, language=None)
        if st.button(
            "从链上读回并核验",
            key=f"chain-reconcile-{index}",
            disabled=runtime.feedback_adapter is None,
            use_container_width=True,
        ):
            try:
                reconciled = runtime.publication_workflow.reconcile_feedback(
                    execution.receipt, runtime.feedback_adapter
                )
                _replace_execution_receipt(index, reconciled)
                st.rerun()
            except Exception as error:
                st.error(f"链上读回失败：{error}")
    elif publication.chain_status is PublicationChainStatus.CONFIRMED:
        st.success(
            f"ERC-8004 已确认并读回一致 · block {publication.block_number} · "
            f"feedback #{publication.feedback_index}"
        )


def _render_attempts(runtime: AppRuntime) -> None:
    executions = st.session_state.get("executions", [])
    if not executions:
        return
    try:
        m9_artifacts = build_m9_artifacts(
            executions,
            st.session_state.get("commitment_pairs", []),
            runtime.revision_store,
        )
    except ValueError as error:
        st.error(f"M9 版本链校验失败：{error}")
        return
    _section("验收结果", "每次交付独立留档；后一次成功不会覆盖前一次失败。")
    for index, execution in enumerate(executions, start=1):
        result = execution.result
        meaning = {
            VerificationOutcome.PASS: "本次验收通过 · 可继续预览回执",
            VerificationOutcome.FAIL: "未通过验收 · 查看问题与补交依据",
            VerificationOutcome.INCONCLUSIVE: "证据不足 · 暂不判断服务对错",
        }[result.outcome]
        with st.container(border=True):
            st.markdown(
                f'<div class="attempt-card outcome-{result.outcome.value}"><div><small>Attempt {index}</small>'
                f'<div class="attempt-title">{result.outcome.value}</div>'
                f'<div class="attempt-meaning">{escape(meaning)}</div></div><div>'
                '<span class="badge badge-submitted">服务交付 · SUBMITTED</span>'
                f'<span class="badge badge-not-submitted">公共发布 · '
                f'{execution.receipt.publication.chain_status.value}</span></div></div>',
                unsafe_allow_html=True,
            )
            token_decimals = reference_decimals(execution.evidence, st.session_state.task.token_address)
            summary = amount_summary(
                execution.submission.claimed_total_base_units,
                result.calculated_total_base_units,
                decimals=token_decimals,
            )
            verified_display = (
                format_token_amount(summary.verified, summary.decimals)
                if result.calculated_total_base_units is not None
                else "无法确定"
            )
            st.markdown(
                '<div class="business-summary"><strong>金额核对结论</strong>'
                f'<p>{escape(summary.direction)}</p>'
                f'<small>报表：{escape(format_token_amount(summary.claimed, summary.decimals))}</small>'
                f'<small>链上有效：{escape(verified_display)}</small>'
                '</div>',
                unsafe_allow_html=True,
            )
            claimed, actual, difference, findings = st.columns(4)
            claimed.metric("服务声称 · 最小单位", execution.submission.claimed_total_base_units)
            with actual, st.container(key=f"metric-actual-{index}"):
                st.metric("链上有效 · 最小单位", result.calculated_total_base_units or "无法确定")
            difference.metric("精确差额 · 报表 − 链上", summary.difference)
            findings.metric("问题数量", len(result.findings))
            if result.outcome is VerificationOutcome.INCONCLUSIVE:
                st.warning(f"证据不足，不能形成服务负面结论：{result.inconclusive_reason}")
            render_fund_flow(
                execution.fund_flow,
                allow_explorer_links=runtime.evidence_label.startswith("真实 Sepolia RPC"),
            )
            if execution.explanation:
                st.info("受限解释：" + execution.explanation.summary)
            for error in execution.ai_errors:
                st.warning(error)
            if execution.evidence_diagnostics:
                with st.expander("证据来源与采样诊断", expanded=False):
                    for diagnostic in execution.evidence_diagnostics:
                        st.markdown(
                            f'<div class="status-card"><strong>{escape(diagnostic.source)}</strong> · '
                            f'{escape(diagnostic.role)}<br><span class="badge badge-confirmed">'
                            f'{escape(diagnostic.status)}</span> {escape(diagnostic.detail)}<br>'
                            f'<small>{diagnostic.pages} pages · {diagnostic.records} records · '
                            f'{diagnostic.elapsed_ms} ms</small></div>',
                            unsafe_allow_html=True,
                        )
            elif result.reference_sources:
                with st.expander("证据来源"):
                    for source in result.reference_sources:
                        st.write(
                            f"{source.source.value} · complete={source.complete} · "
                            f"retrieved_at={source.retrieved_at.isoformat()}"
                        )
            if result.findings:
                st.markdown("**需要处理的差异**")
                for finding_number, finding in enumerate(result.findings, start=1):
                    title, action = finding_copy(finding.finding_type)
                    refs = ", ".join(finding.evidence_refs)
                    st.markdown(
                        f'<div class="finding-card"><strong>{finding_number}. {escape(title)}</strong>'
                        f'<p>{escape(action)}</p><small>{escape(finding.status.value)} · '
                        f'{escape(finding.finding_type.value)}</small></div>',
                        unsafe_allow_html=True,
                    )
                    with st.expander(f"查看差异 {finding_number} 的交易与判定依据"):
                        st.write("处理建议：", action)
                        st.write("确定性说明：", finding.explanation)
                        st.write("判定规则：", finding.violated_rule)
                        st.write("证据引用：", list(finding.evidence_refs))
                        st.json({"链上预期": finding.expected, "报表实际": finding.actual})
                        st.caption(f"完整证据索引：{refs}")
            pairs = st.session_state.get("commitment_pairs", [])
            task_commitment = delivery_commitment = expected_signer = None
            if index <= len(pairs) and pairs[index - 1] is not None:
                task_commitment, delivery_commitment, expected_signer = pairs[index - 1]
            render_commitments(
                st.session_state.task,
                task_commitment,
                delivery_commitment,
                execution.submission,
                expected_signer,
                runtime.commitment_anchor_status,
            )
            if index == 1 and m9_artifacts.rework_package is not None:
                render_rework_package(st, m9_artifacts.rework_package)
            with st.expander("M9 外置回执版本记录", expanded=False):
                st.json(m9_artifacts.revisions[index - 1].model_dump(mode="json"))
            if (
                index == len(executions)
                and result.outcome is VerificationOutcome.PASS
                and execution.receipt.publication.uri is None
                and st.button(
                    "预览并发布脱敏回执",
                    type="primary",
                    key=f"preview-publication-{index}",
                    use_container_width=True,
                )
            ):
                st.session_state[f"show-publication-{index}"] = True
                st.rerun()
            if execution.follow_up:
                with st.expander("补查与后续建议"):
                    for suggestion in execution.follow_up.suggestions:
                        st.write(f"{suggestion.action.value} — {suggestion.rationale}")
            with st.expander("本地回执与下载", expanded=False):
                receipt_json = execution.receipt.model_dump(mode="json")
                st.caption("本地回执保留完整发布状态；公开文件只包含脱敏、可重放字段。")
                st.json(receipt_json)
                st.download_button(
                    "下载本地 JSON 回执",
                    data=json.dumps(receipt_json, ensure_ascii=False, indent=2),
                    file_name=f"attempt-{index}-receipt.json",
                    mime="application/json",
                    key=f"download-{index}",
                )
            with st.expander(
                "公共回执与 ERC-8004",
                expanded=st.session_state.get(f"show-publication-{index}", False),
            ):
                _render_publication(runtime, execution, index - 1, m9_artifacts)
    if m9_artifacts.comparison is not None:
        _section("返工闭环", "保留首次失败与补交结果，并核验两次 M8 EIP-712 承诺。")
        render_repair_comparison(st, m9_artifacts.comparison)
    render_public_history(st, runtime, m9_artifacts.receipts)


def _draft_task(runtime: AppRuntime) -> bool:
    _section("上传报表", "上传约定格式的 JSON 报表；演示模式也可直接使用固定样例。")
    with st.container(border=True, key="panel-input"):
        input_mode = st.selectbox(
            "报表输入方式",
            ("上传自己的 JSON", "加载真实 Sepolia 案例", "加载契约测试示例"),
            help="真实案例使用团队构造报表与公开 Sepolia 交易；契约测试示例为合成数据。",
        )
        real_case = load_real_case(PROJECT_ROOT)
        with st.expander("下载示例报表与核验范围"):
            st.caption("团队为演示构造报表，引用真实公开 Sepolia 交易；账户角色为演示设定。")
            for report_label, report_data, filename in (
                ("下载真实案例错误版 JSON", real_case.error_report, "error-missing-transfer.json"),
                ("下载真实案例修正版 JSON", real_case.corrected_report, "corrected-complete.json"),
            ):
                st.download_button(report_label, report_data, filename, "application/json")
            st.json(real_case.candidate.model_dump(mode="json"))
        st.download_button(
            "下载严格 JSON 空白模板",
            data=strict_template_bytes(),
            file_name="uploaded-report-template.json",
            mime="application/json",
            use_container_width=True,
        )
        uploaded = st.file_uploader(
            "服务商报表",
            type=("json",),
            accept_multiple_files=False,
            max_upload_size=1,
            disabled=input_mode != "上传自己的 JSON",
        )
        upload_valid = True
        st.caption("报表格式：schema_version、claimed_total_base_units、claimed_count、transfers。")
        with st.expander("查看上传格式与身份说明"):
            st.json(UploadedReport.model_json_schema())
            st.caption("无签名报表使用本地接收身份留档；不表示外部作者或 ERC-8004 服务 owner 已签名。")
        payload = None
        report_name = None
        if input_mode == "加载真实 Sepolia 案例":
            payload = real_case.error_report
            report_name = "真实 Sepolia 案例错误版（团队构造报表）"
            st.caption("下一步预填案例范围供你修改和确认；实时参考证据只从 Sepolia RPC 获取。")
            if not runtime.evidence_label.startswith("真实 Sepolia RPC"):
                upload_valid = False
                st.info("请在运行配置中把独立证据切换为“真实 Sepolia RPC”，再核验此案例。")
        elif input_mode == "加载契约测试示例":
            payload = contract_example_bytes(PROJECT_ROOT)
            report_name = "契约测试示例（人工标注合成数据，非 M11 真实案例）"
        elif uploaded is not None:
            payload = uploaded.getvalue()
            report_name = uploaded.name
        candidate_source = (input_mode, content_hash(payload) if payload else None)
        if st.session_state.get("candidate_source") != candidate_source:
            st.session_state.pop("candidate", None)
            st.session_state.candidate_source = candidate_source
        if payload is not None:
            try:
                digest = content_hash(payload)
                if (
                    st.session_state.get("uploaded_report_hash") != digest
                    or "uploaded_service" not in st.session_state
                ):
                    st.session_state.uploaded_service = UploadedReportService(
                        payload, private_directory=runtime.upload_directory,
                    )
                    st.session_state.uploaded_report_hash = digest
                st.success(f"已读取 {report_name} · SHA-256 {digest}")
                st.caption("原始字节已私有留档；接下来核验这份报表的原始金额和记录声明。")
            except ValueError:
                upload_valid = False
                st.session_state.pop("uploaded_service", None)
                st.session_state.pop("uploaded_report_hash", None)
                st.error("无法解析报表：需要严格 UTF-8 JSON、完整字段、整数金额、service 来源与最多 200 条记录。")
        else:
            st.session_state.pop("uploaded_service", None)
            st.session_state.pop("uploaded_report_hash", None)
        request = st.text_area(
            "核验范围说明",
            value="核对 Sepolia 上两个资金账户在区块 1000–1010 对两个资助对象的代币拨款，排除内部互转。",
            height=130,
            help="这里不会直接触发链上操作；系统先生成一份可修改候选。",
        )
        st.caption("下一步会展示结构化字段供你逐项确认，不会自动冻结或执行。")
        if st.button(
            "生成可核对的任务候选",
            type="secondary" if "candidate" in st.session_state else "primary",
            disabled=not upload_valid,
            use_container_width=True,
        ):
            try:
                st.session_state.candidate = (
                    real_case.candidate
                    if input_mode == "加载真实 Sepolia 案例"
                    else runtime.workflow.draft_task(request)
                )
                st.session_state.pop("draft_error", None)
            except Exception as error:
                if _live_only():
                    st.session_state.pop("candidate", None)
                else:
                    st.session_state.candidate = runtime.editable_seed
                st.session_state.draft_error = str(error)
            st.rerun()
    if "draft_error" in st.session_state:
        st.error("模型输出被拒绝：" + st.session_state.draft_error)
        st.info("请修正请求或模型配置后重新生成；不会自动确认或执行。")
    return upload_valid


def main() -> None:
    st.set_page_config(
        page_title="信据 Agent · 链上验收工作台",
        page_icon=str(LOGO_PATH),
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    st.markdown(APP_CSS, unsafe_allow_html=True)
    _product_header()
    if st.query_params.get("verify") == "1":
        render_public_explorer(st, PROJECT_ROOT)
        return
    st.link_button("打开独立公开验证页", "?verify=1")
    runtime = _runtime()
    if runtime is None:
        return
    if st.session_state.pop("restore_notice", False):
        st.info("已从该工作区恢复最新任务与 attempt；历史 AI 文本没有重新生成。")
    render_workspace_history(st, runtime)

    if "task" not in st.session_state:
        input_valid = _draft_task(runtime)
        if input_valid and "candidate" in st.session_state:
            _section("确认核验范围", "核对链、资产、账户与区块范围后，再开始验收。")
            _candidate_editor(runtime)
        return

    _section("核验范围已确认", "链、资产、账户与区块范围已经锁定。")
    _task_summary()
    _section("链上核验", "选择服务交付；最多两次验收，签名或计划校验失败不消耗次数。")
    _run_attempt(runtime)
    _render_attempts(runtime)
    executions = st.session_state.get("executions", [])
    if (
        executions
        and (len(executions) == 2 or executions[-1].result.outcome is VerificationOutcome.PASS)
        and st.button("开始下一次报表验收", key="m10-next-task")
    ):
        for key in (
            "task", "candidate", "executions", "commitment_pairs", "uploaded_service", "uploaded_report_hash",
        ):
            st.session_state.pop(key, None)
        st.rerun()


if __name__ == "__main__":
    main()
