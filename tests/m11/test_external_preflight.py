from __future__ import annotations

import os
from pathlib import Path

import pytest

from scripts.m11.preflight import load_case_bundle, run_preflight
from trust_receipt.agents import OfflineDemoStructuredOutputAdapter, RestrictedAIService, TaskSpecCandidate
from trust_receipt.chain import RpcReferenceEvidenceProvider
from trust_receipt.models import VerificationOutcome
from trust_receipt.orchestration import M5Workflow
from trust_receipt.services.upload import UploadedReportService
from trust_receipt.storage.sqlite import SQLiteRepository

pytestmark = pytest.mark.external

CASE_DIRECTORY = Path(__file__).resolve().parents[2] / "fixtures" / "m11"


def test_fixed_sepolia_case_still_matches_live_rpc():
    rpc_url = os.environ.get("M11_RPC_URL") or os.environ.get("ETH_RPC_URL")
    if not rpc_url:
        pytest.skip("blocked by missing M11_RPC_URL or ETH_RPC_URL")

    result = run_preflight(rpc_url, case_directory=CASE_DIRECTORY)

    assert result["ok"] is True
    assert result["status"] == "COMPLETE"
    assert result["raw_event_count"] == 6
    assert result["eligible_event_count"] == 1
    assert result["calculated_total_base_units"] == "180674489737"


def test_fixed_reports_run_fail_then_pass_against_live_sepolia_rpc(tmp_path):
    rpc_url = os.environ.get("M11_RPC_URL") or os.environ.get("ETH_RPC_URL")
    if not rpc_url:
        pytest.skip("blocked by missing M11_RPC_URL or ETH_RPC_URL")
    bundle = load_case_bundle(CASE_DIRECTORY)
    task = bundle.task
    candidate = TaskSpecCandidate(
        schema_version="1.0",
        candidate_id="candidate-m11-live-case",
        chain_id=task.chain_id,
        token_address=task.token_address,
        treasury_addresses=task.treasury_addresses,
        recipient_addresses=task.recipient_addresses,
        start_block=task.start_block,
        end_block=task.end_block,
        exclusion_rules=task.exclusion_rules,
        max_records=task.max_records,
        ambiguities=(),
        missing_fields=(),
        clarification_questions=(),
    )
    repository = SQLiteRepository(tmp_path / "m11-live.db")
    repository.add_task(task)
    workflow = M5Workflow(
        repository=repository,
        evidence_provider=RpcReferenceEvidenceProvider(
            rpc_url,
            expected_chain_id=task.chain_id,
            confirmations=int(bundle.manifest["provenance"]["minimum_confirmations"]),
        ),
        ai_service=RestrictedAIService(OfflineDemoStructuredOutputAdapter(candidate)),
        receipt_directory=tmp_path / "receipts",
    )
    error_path = CASE_DIRECTORY / bundle.manifest["reports"]["error"]
    corrected_path = CASE_DIRECTORY / bundle.manifest["reports"]["corrected"]

    failed = workflow.run_attempt(
        task.task_id,
        UploadedReportService(error_path.read_bytes(), private_directory=tmp_path / "uploads"),
    )
    passed = workflow.run_attempt(
        task.task_id,
        UploadedReportService(corrected_path.read_bytes(), private_directory=tmp_path / "uploads"),
    )

    assert failed.result.outcome is VerificationOutcome.FAIL
    assert passed.result.outcome is VerificationOutcome.PASS
    assert failed.result.calculated_total_base_units == "180674489737"
    assert passed.result.calculated_total_base_units == "180674489737"
    assert failed.evidence_diagnostics[0].status == "COMPLETE"
    assert passed.evidence_diagnostics[0].status == "COMPLETE"
    assert failed.receipt_path is not None and failed.receipt_path.is_file()
    assert passed.receipt_path is not None and passed.receipt_path.is_file()
    assert len(repository.list_attempts(task.task_id)) == 2
