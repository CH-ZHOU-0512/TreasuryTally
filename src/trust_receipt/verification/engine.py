"""Pure three-state verification against complete independent evidence."""

from __future__ import annotations

from datetime import datetime

from trust_receipt.models.enums import FindingType, VerificationOutcome
from trust_receipt.models.submissions import ServiceSubmission
from trust_receipt.models.tasks import TaskSpec
from trust_receipt.models.transfers import TransferRecord
from trust_receipt.models.verification import Finding, SourceDescriptor, VerificationResult
from trust_receipt.verification.evidence import ReferenceEvidence, collect_reference
from trust_receipt.verification.findings import confirmed_finding, insufficient_evidence_finding, transfer_summary
from trust_receipt.verification.normalization import address_key, equivalent_reference, event_key
from trust_receipt.verification.scope import scope_violation

VERIFIER_VERSION = "m2.1"


def _inconclusive(
    *,
    run_id: str,
    task: TaskSpec,
    submission: ServiceSubmission,
    sources: tuple[SourceDescriptor, ...],
    reference_complete: bool,
    reason: str,
    verifier_version: str,
    started_at: datetime,
    finished_at: datetime,
) -> VerificationResult:
    return VerificationResult(
        run_id=run_id,
        task_id=task.task_id,
        submission_id=submission.submission_id,
        verifier_version=verifier_version,
        reference_sources=sources,
        reference_complete=reference_complete,
        evidence_sufficient=False,
        calculated_total_base_units=None,
        calculated_count=None,
        findings=(insufficient_evidence_finding(run_id, reason),),
        outcome=VerificationOutcome.INCONCLUSIVE,
        inconclusive_reason=reason,
        started_at=started_at,
        finished_at=finished_at,
    )


def _reference_records(
    task: TaskSpec,
    records: tuple[TransferRecord, ...],
) -> tuple[dict[tuple[int, str, int], TransferRecord], str | None]:
    merged: dict[tuple[int, str, int], TransferRecord] = {}
    for record in records:
        if record.chain_id != task.chain_id:
            return {}, "Reference source returned a transfer from a different chain"
        key = event_key(record)
        existing = merged.get(key)
        if existing is not None and not equivalent_reference(existing, record):
            return {}, f"Reference sources disagree on event {key}"
        if existing is None or (existing.block_hash is None and record.block_hash is not None):
            merged[key] = record
    eligible = {key: record for key, record in merged.items() if scope_violation(task, record) is None}
    if len(eligible) > task.max_records:
        return {}, f"Relevant reference events exceed max_records={task.max_records}; split the task"
    if len({record.token_decimals for record in eligible.values()}) > 1:
        return {}, "Reference events disagree on token decimals"
    return eligible, None


def _service_findings(
    *,
    run_id: str,
    task: TaskSpec,
    submission: ServiceSubmission,
    reference: dict[tuple[int, str, int], TransferRecord],
) -> list[Finding]:
    findings: list[Finding] = []

    def add(
        kind: FindingType,
        rule: str,
        explanation: str,
        expected: dict | None,
        actual: dict | None,
        records: tuple[TransferRecord, ...],
        additional_refs: tuple[str, ...] = (),
    ) -> None:
        findings.append(
            confirmed_finding(
                run_id=run_id,
                number=len(findings) + 1,
                finding_type=kind,
                rule=rule,
                explanation=explanation,
                expected=expected,
                actual=actual,
                records=records,
                additional_refs=additional_refs,
            )
        )

    submitted: dict[tuple[int, str, int], tuple[int, TransferRecord]] = {}
    ordered = sorted(
        enumerate(submission.transfers),
        key=lambda item: (event_key(item[1]), item[1].amount_base_units, item[1].token_decimals, item[0]),
    )
    for index, record in ordered:
        key = event_key(record)
        if key in submitted:
            first_index, first_record = submitted[key]
            add(
                FindingType.DUPLICATE_TRANSFER,
                "unique_event_key",
                "The service reported the same chain, transaction hash, and log index more than once.",
                {"event_key": list(key), "occurrences": 1},
                {"event_key": list(key), "occurrences": 2},
                (first_record, record),
                (
                    f"submission:{submission.submission_id}:{first_index}",
                    f"submission:{submission.submission_id}:{index}",
                ),
            )
            continue
        submitted[key] = (index, record)
        violation = scope_violation(task, record)
        if violation is not None:
            add(
                violation,
                "task_scope",
                "The service included a transfer outside the confirmed task rules.",
                {"included": False},
                transfer_summary(record),
                (record,),
            )

    eligible_service = {
        key: record for key, (_, record) in submitted.items() if scope_violation(task, record) is None
    }
    for key in sorted(reference.keys() - eligible_service.keys()):
        expected = reference[key]
        add(
            FindingType.MISSING_TRANSFER,
            "complete_event_set",
            "An eligible reference transfer is absent from the service report.",
            transfer_summary(expected),
            None,
            (expected,),
        )
    for key in sorted(eligible_service.keys() - reference.keys()):
        actual = eligible_service[key]
        add(
            FindingType.EXTRA_TRANSFER,
            "complete_event_set",
            "The service reported an eligible transfer that is absent from the reference evidence.",
            None,
            transfer_summary(actual),
            (actual,),
        )
    for key in sorted(reference.keys() & eligible_service.keys()):
        expected = reference[key]
        actual = eligible_service[key]
        if (
            address_key(expected.from_address) != address_key(actual.from_address)
            or address_key(expected.to_address) != address_key(actual.to_address)
        ):
            add(
                FindingType.WRONG_DIRECTION,
                "event_parties",
                "The service's transfer parties disagree with the reference event.",
                transfer_summary(expected),
                transfer_summary(actual),
                (expected, actual),
            )
        if expected.block_number != actual.block_number:
            add(
                FindingType.EXTRA_TRANSFER,
                "event_block_number",
                "The service's block number disagrees with the reference event.",
                transfer_summary(expected),
                transfer_summary(actual),
                (expected, actual),
            )
        if expected.token_decimals != actual.token_decimals:
            add(
                FindingType.DECIMAL_ERROR,
                "token_decimals",
                "The service used a different token decimal scale from the reference event.",
                {"token_decimals": expected.token_decimals},
                {"token_decimals": actual.token_decimals},
                (expected, actual),
            )
        if expected.amount_base_units != actual.amount_base_units:
            add(
                FindingType.AMOUNT_MISMATCH,
                "event_amount_base_units",
                "The service's base-unit amount disagrees with the reference event.",
                {"amount_base_units": expected.amount_base_units},
                {"amount_base_units": actual.amount_base_units},
                (expected, actual),
            )
    if not findings:
        calculated_total = sum(int(record.amount_base_units) for record in reference.values())
        if int(submission.claimed_total_base_units) != calculated_total or submission.claimed_count != len(reference):
            add(
                FindingType.AMOUNT_MISMATCH,
                "aggregate_claim",
                "The service's claimed total or count disagrees with verified transfers.",
                {"total_base_units": str(calculated_total), "count": len(reference)},
                {"total_base_units": submission.claimed_total_base_units, "count": submission.claimed_count},
                (),
            )
    return findings


def verify_submission(
    task: TaskSpec,
    submission: ServiceSubmission,
    evidence: ReferenceEvidence,
    *,
    run_id: str,
    started_at: datetime,
    finished_at: datetime,
    verifier_version: str = VERIFIER_VERSION,
) -> VerificationResult:
    """Verify one immutable attempt with explicit reference evidence and no I/O."""
    if submission.task_id != task.task_id:
        raise ValueError("submission.task_id must match task.task_id")
    collected = collect_reference(evidence)
    if not collected.complete or not collected.sufficient:
        return _inconclusive(
            run_id=run_id,
            task=task,
            submission=submission,
            sources=collected.sources,
            reference_complete=collected.complete,
            reason=collected.reason or "Reference evidence is incomplete",
            verifier_version=verifier_version,
            started_at=started_at,
            finished_at=finished_at,
        )
    reference, problem = _reference_records(task, collected.transfers)
    if problem is not None:
        return _inconclusive(
            run_id=run_id,
            task=task,
            submission=submission,
            sources=collected.sources,
            reference_complete=True,
            reason=problem,
            verifier_version=verifier_version,
            started_at=started_at,
            finished_at=finished_at,
        )
    findings = _service_findings(run_id=run_id, task=task, submission=submission, reference=reference)
    calculated_total = sum(int(record.amount_base_units) for record in reference.values())
    return VerificationResult(
        run_id=run_id,
        task_id=task.task_id,
        submission_id=submission.submission_id,
        verifier_version=verifier_version,
        reference_sources=collected.sources,
        reference_complete=True,
        evidence_sufficient=True,
        calculated_total_base_units=str(calculated_total),
        calculated_count=len(reference),
        findings=tuple(findings),
        outcome=VerificationOutcome.FAIL if findings else VerificationOutcome.PASS,
        inconclusive_reason=None,
        started_at=started_at,
        finished_at=finished_at,
    )
