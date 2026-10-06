"""Composition root for one isolated Streamlit browser session."""

from __future__ import annotations

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


class ConfigurationBlocked(RuntimeError):
    pass


@dataclass(frozen=True)
class AppRuntime:
    workflow: M5Workflow
    services: dict[str, TeamControlledReportService]
    mode_label: str
    editable_seed: TaskSpecCandidate


def create_runtime(
    *,
    project_root: Path,
    session_id: str,
    provider: str,
    evidence_sufficient: bool,
) -> AppRuntime:
    fixture = load_vertical_demo_fixture(project_root)
    candidate = candidate_from_fixture(fixture)
    ai_service, mode_label = _ai_service(provider, candidate, project_root)
    repository = SQLiteRepository(project_root / "data" / "m5" / f"{session_id}.db")
    workflow = M5Workflow(
        repository=repository,
        evidence_provider=StaticEvidenceProvider(
            evidence_from_fixture(fixture, sufficient=evidence_sufficient)
        ),
        ai_service=ai_service,
        receipt_directory=project_root / "receipts" / "private" / "m5" / session_id,
    )
    records = eligible_records(fixture)
    services = {
        "服务 A · 首次故意漏项": TeamControlledReportService(
            service_id="service-a",
            private_key=Account.create().key.to_0x_hex(),
            records_provider=lambda task: records,
            fault_by_attempt={1: FaultMode.OMIT_LAST_TRANSFER},
        ),
        "服务 B · 完整交付": TeamControlledReportService(
            service_id="service-b",
            private_key=Account.create().key.to_0x_hex(),
            records_provider=lambda task: records,
        ),
    }
    return AppRuntime(
        workflow=workflow,
        services=services,
        mode_label=mode_label,
        editable_seed=candidate,
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
