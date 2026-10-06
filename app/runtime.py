"""Composition root for one isolated Streamlit browser session."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from eth_account import Account

from trust_receipt.agents import (
    DeepSeekStructuredOutputAdapter,
    M4AISettings,
    OfflineDemoStructuredOutputAdapter,
    OpenAIStructuredOutputAdapter,
    RestrictedAIService,
    TaskSpecCandidate,
)
from trust_receipt.chain import RpcReferenceEvidenceProvider
from trust_receipt.integrations.config import M0Settings
from trust_receipt.orchestration import (
    M5Workflow,
    StaticEvidenceProvider,
    candidate_from_fixture,
    eligible_records,
    evidence_from_fixture,
    load_vertical_demo_fixture,
)
from trust_receipt.services import FaultMode, TeamControlledReportService
from trust_receipt.storage.sqlite import SQLiteRepository
from trust_receipt.verification.scope import scope_violation


class ConfigurationBlocked(RuntimeError):
    pass


@dataclass(frozen=True)
class AppRuntime:
    workflow: M5Workflow
    services: dict[str, TeamControlledReportService]
    mode_label: str
    editable_seed: TaskSpecCandidate
    evidence_label: str


def create_runtime(
    *,
    project_root: Path,
    session_id: str,
    provider: str,
    evidence_mode: str,
) -> AppRuntime:
    if re.fullmatch(r"[a-z0-9][a-z0-9-]{0,31}", session_id) is None:
        raise ConfigurationBlocked("工作区 ID 仅允许 1-32 位小写字母、数字和连字符")
    fixture = load_vertical_demo_fixture(project_root)
    candidate = candidate_from_fixture(fixture)
    ai_service, mode_label = _ai_service(provider, candidate, project_root)
    evidence_provider, evidence_label = _evidence_provider(
        evidence_mode,
        fixture=fixture,
        project_root=project_root,
    )
    repository = SQLiteRepository(project_root / "data" / "m5" / f"{session_id}.db")
    workflow = M5Workflow(
        repository=repository,
        evidence_provider=evidence_provider,
        ai_service=ai_service,
        receipt_directory=project_root / "receipts" / "private" / "m5" / session_id,
    )
    if evidence_mode == "真实 Sepolia RPC":
        def records_provider(task):
            return _eligible_live_records(evidence_provider, task)
    else:
        records = eligible_records(fixture)

        def records_provider(task):
            del task
            return records
    services = {
        "服务 A · 首次故意漏项": TeamControlledReportService(
            service_id="service-a",
            private_key=Account.create().key.to_0x_hex(),
            records_provider=records_provider,
            fault_by_attempt={1: FaultMode.OMIT_LAST_TRANSFER},
        ),
        "服务 B · 完整交付": TeamControlledReportService(
            service_id="service-b",
            private_key=Account.create().key.to_0x_hex(),
            records_provider=records_provider,
        ),
    }
    return AppRuntime(
        workflow=workflow,
        services=services,
        mode_label=mode_label,
        editable_seed=candidate,
        evidence_label=evidence_label,
    )


def _evidence_provider(evidence_mode: str, *, fixture, project_root: Path):
    if evidence_mode == "完整 fixture 证据":
        return StaticEvidenceProvider(evidence_from_fixture(fixture)), "fixture · 完整人工标注证据"
    if evidence_mode == "模拟证据不可用":
        return (
            StaticEvidenceProvider(evidence_from_fixture(fixture, sufficient=False)),
            "fixture · 模拟证据不可用",
        )
    settings = M0Settings.load(project_root / ".env")
    if settings.rpc_url is None:
        raise ConfigurationBlocked("真实 RPC 配置阻塞：缺少 ETH_RPC_URL")
    live = RpcReferenceEvidenceProvider(
        settings.rpc_url_value(),
        expected_chain_id=settings.chain_id,
        timeout_seconds=settings.rpc_timeout_seconds,
        confirmations=settings.rpc_confirmations,
        blockscout_mcp_url=settings.blockscout_mcp_url,
        enable_blockscout_cross_check=settings.blockscout_pro_api_key is not None,
    )
    blockscout = "已配置抽样交叉检查" if settings.blockscout_pro_api_key is not None else "未配置，RPC-only"
    return live, f"真实 Sepolia RPC · Blockscout {blockscout}"


def _eligible_live_records(evidence_provider, task):
    evidence = evidence_provider.fetch(task)
    if not evidence.evidence_sufficient:
        return ()
    return tuple(
        record
        for stream in evidence.streams
        for page in stream.pages
        for record in page.transfers
        if scope_violation(task, record) is None
    )


def _ai_service(provider: str, candidate, project_root: Path) -> tuple[RestrictedAIService, str]:
    settings = M4AISettings.load(project_root / ".env")
    if provider == "离线 fixture 演示":
        adapter = OfflineDemoStructuredOutputAdapter(candidate)
        return RestrictedAIService(adapter), "离线 fixture 演示（非真实模型调用）"
    if provider == "OpenAI 真实模型":
        missing = settings.missing_for_openai()
        if missing:
            raise ConfigurationBlocked(f"OpenAI 配置阻塞：缺少 {', '.join(missing)}")
        adapter = OpenAIStructuredOutputAdapter(
            api_key=settings.api_key_value(),
            model_name=settings.model_name or "",
            timeout_seconds=settings.timeout_seconds,
            max_retries=settings.max_retries,
        )
        return RestrictedAIService(adapter), f"OpenAI 真实模型：{settings.model_name}"
    missing = settings.missing_for_deepseek()
    if missing:
        raise ConfigurationBlocked(f"DeepSeek 配置阻塞：缺少 {', '.join(missing)}")
    adapter = DeepSeekStructuredOutputAdapter(
        api_key=settings.deepseek_api_key_value(),
        model_name=settings.deepseek_model_name or "",
        timeout_seconds=settings.timeout_seconds,
        max_retries=settings.max_retries,
    )
    return RestrictedAIService(adapter), f"DeepSeek 真实模型：{settings.deepseek_model_name}"
