from trust_receipt.models import FundFlowVisualStatus, VerificationOutcome


def test_finding_driven_projection_keeps_sources_event_keys_and_internal_transfer(m5_components) -> None:
    _, candidate, _, workflow, service = m5_components
    task = workflow.confirm_task(candidate)
    execution = workflow.run_attempt(task.task_id, service)
    projection = execution.fund_flow

    assert projection is not None
    assert projection.outcome is VerificationOutcome.FAIL
    statuses = {edge.status for edge in projection.edges}
    assert FundFlowVisualStatus.MATCHED in statuses
    assert FundFlowVisualStatus.MISSING_FROM_REPORT in statuses
    assert FundFlowVisualStatus.INTERNAL_TRANSFER in statuses
    missing = next(edge for edge in projection.edges if edge.status is FundFlowVisualStatus.MISSING_FROM_REPORT)
    assert missing.reference_refs
    assert not missing.service_refs
    assert missing.finding_ids
    assert len(missing.event_key) == 3


def test_insufficient_evidence_never_projects_a_negative_chain_fact(tmp_path, m5_components) -> None:
    from trust_receipt.agents import OfflineDemoStructuredOutputAdapter, RestrictedAIService
    from trust_receipt.orchestration import M5Workflow, StaticEvidenceProvider, evidence_from_fixture
    from trust_receipt.storage.sqlite import SQLiteRepository

    fixture, candidate, _, _, service = m5_components
    workflow = M5Workflow(
        repository=SQLiteRepository(tmp_path / "projection.db"),
        evidence_provider=StaticEvidenceProvider(evidence_from_fixture(fixture, sufficient=False)),
        ai_service=RestrictedAIService(OfflineDemoStructuredOutputAdapter(candidate)),
    )
    task = workflow.confirm_task(candidate)
    projection = workflow.run_attempt(task.task_id, service).fund_flow

    assert projection is not None
    assert projection.outcome is VerificationOutcome.INCONCLUSIVE
    assert {edge.status for edge in projection.edges} == {FundFlowVisualStatus.INCONCLUSIVE}
