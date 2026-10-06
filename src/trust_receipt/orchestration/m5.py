"""M5 page-facing use case that composes existing stable ports."""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from trust_receipt.agents import FollowUpAdvice, RestrictedAIService, ResultExplanation, TaskSpecCandidate
from trust_receipt.hashing import verify_submission_hash, verify_task_spec_hash
from trust_receipt.models import FixtureCase, Receipt, ServiceIdentity, TaskSpec, VerificationPlan, VerificationResult
from trust_receipt.receipts import build_receipt, save_receipt
from trust_receipt.services import ReportService, verify_submission_signature
from trust_receipt.storage.ports import TaskRepository
from trust_receipt.verification import ReferenceEvidence, ReferencePage, ReferenceStream, verify_submission
from trust_receipt.verification.scope import scope_violation


@dataclass(frozen=True)
class StaticEvidenceProvider:
    evidence: ReferenceEvidence

    def fetch(self, task: TaskSpec) -> ReferenceEvidence:
        del task
        return self.evidence


@dataclass(frozen=True)
class AttemptExecution:
    plan: VerificationPlan
    result: VerificationResult
    receipt: Receipt
    receipt_path: Path | None
    explanation: ResultExplanation | None
    follow_up: FollowUpAdvice | None
    ai_errors: tuple[str, ...]


class M5Workflow:
    """One page-safe vertical workflow; no Streamlit or supplier SDK dependency."""

    def __init__(
        self,
        *,
        repository: TaskRepository,
        evidence_provider: StaticEvidenceProvider,
        ai_service: RestrictedAIService,
        receipt_directory: Path | None = None,
        clock: Callable[[], datetime] = lambda: datetime.now(UTC),
        id_factory: Callable[[], str] = lambda: str(uuid4()),
    ) -> None:
        self._repository = repository
        self._evidence_provider = evidence_provider
        self._ai_service = ai_service
        self._receipt_directory = receipt_directory
        self._clock = clock
        self._id_factory = id_factory

    def draft_task(self, user_request: str) -> TaskSpecCandidate:
        if not user_request.strip():
            raise ValueError("Describe the verification task before generating a candidate")
        return self._ai_service.draft_task(user_request)

    def confirm_task(self, candidate: TaskSpecCandidate) -> TaskSpec:
        task = self._ai_service.confirm_task(
            candidate,
            task_id=f"task-{self._id_factory()}",
            confirmed_at=self._clock(),
        )
        if not verify_task_spec_hash(task):
            raise ValueError("confirmed task hash does not match canonical content")
        self._repository.add_task(task)
        return task

    def run_attempt(self, task_id: str, service: ReportService) -> AttemptExecution:
        stored = self._repository.get_task(task_id)
        attempt = self._repository.request_attempt(task_id)
        try:
            delivery = service.submit(stored.task, attempt=attempt)
            submission = delivery.submission
            self._validate_delivery(service, submission)
            extraction = self._ai_service.extract_claims(
                report_id=submission.submission_id,
                report_text=submission.report_text,
            )
            plan = self._ai_service.propose_plan(stored.task, extraction)
        except Exception:
            self._repository.cancel_attempt_request(task_id)
            raise

        self._repository.save_delivery(delivery)
        self._repository.begin_verification(task_id, submission.submission_id)
        evidence = self._evidence_provider.fetch(stored.task)
        started_at = self._clock()
        result = verify_submission(
            stored.task,
            submission,
            evidence,
            run_id=f"run-{self._id_factory()}",
            started_at=started_at,
            finished_at=self._clock(),
        )
        self._repository.save_verification(result)

        explanation, follow_up, errors = self._safe_ai_result_artifacts(result)
        receipt = build_receipt(
            receipt_id=f"receipt-{self._id_factory()}",
            task=stored.task,
            submission=submission,
            service_identity=ServiceIdentity(
                service_id=submission.service_id,
                name=f"Team-controlled {submission.service_id}",
                identity_scheme="local-demo-signer",
                identity_reference=service.signer_address,
            ),
            plan=plan,
            result=result,
            evidence=evidence,
            created_at=self._clock(),
        )
        receipt_path = self._save_receipt(receipt, attempt)
        return AttemptExecution(
            plan=plan,
            result=result,
            receipt=receipt,
            receipt_path=receipt_path,
            explanation=explanation,
            follow_up=follow_up,
            ai_errors=errors,
        )

    def list_attempts(self, task_id: str):
        return self._repository.list_attempts(task_id)

    @staticmethod
    def _validate_delivery(service: ReportService, submission) -> None:
        if submission.service_id != service.service_id:
            raise ValueError("service response identity does not match selected service")
        if not verify_submission_hash(submission):
            raise ValueError("service report_hash does not match canonical content")
        if not verify_submission_signature(submission, service.signer_address):
            raise ValueError("service submission signature is invalid")

    def _safe_ai_result_artifacts(
        self, result: VerificationResult
    ) -> tuple[ResultExplanation | None, FollowUpAdvice | None, tuple[str, ...]]:
        errors: list[str] = []
        explanation = None
        follow_up = None
        try:
            explanation = self._ai_service.explain_result(result)
        except Exception as error:
            errors.append(f"Result explanation rejected: {error}")
        try:
            follow_up = self._ai_service.suggest_follow_up(result)
        except Exception as error:
            errors.append(f"Follow-up advice rejected: {error}")
        return explanation, follow_up, tuple(errors)

    def _save_receipt(self, receipt: Receipt, attempt: int) -> Path | None:
        if self._receipt_directory is None:
            return None
        path = self._receipt_directory / receipt.task_spec.task_id / f"attempt-{attempt}.json"
        return save_receipt(receipt, path)


def load_vertical_demo_fixture(project_root: Path) -> FixtureCase:
    path = project_root / "fixtures" / "m1" / "cases" / "missing-transfer-vertical-slice.json"
    return FixtureCase.model_validate(json.loads(path.read_text(encoding="utf-8")))


def candidate_from_fixture(fixture: FixtureCase) -> TaskSpecCandidate:
    task = fixture.task_spec
    return TaskSpecCandidate(
        schema_version="1.0",
        candidate_id=f"candidate-{fixture.fixture_id}",
        chain_id=task.chain_id,
        token_address=task.token_address,
        treasury_addresses=task.treasury_addresses,
        recipient_addresses=task.recipient_addresses,
        start_block=task.start_block,
        end_block=task.end_block,
        exclusion_rules=task.exclusion_rules,
        max_records=200,
        ambiguities=(),
        missing_fields=(),
        clarification_questions=(),
    )


def evidence_from_fixture(fixture: FixtureCase, *, sufficient: bool = True) -> ReferenceEvidence:
    source = fixture.reference.sources[0]
    stream = ReferenceStream(
        source=source,
        pages=(ReferencePage(cursor=None, next_cursor=None, transfers=fixture.reference.transfers),),
    )
    return ReferenceEvidence(
        streams=(stream,),
        evidence_sufficient=sufficient,
        insufficiency_reason=None if sufficient else "Offline demo: independent evidence source unavailable",
    )


def eligible_records(fixture: FixtureCase):
    return tuple(record for record in fixture.reference.transfers if scope_violation(fixture.task_spec, record) is None)
