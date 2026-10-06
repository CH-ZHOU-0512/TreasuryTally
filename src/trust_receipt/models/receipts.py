"""Portable receipt and explicit publication lifecycle models."""

from typing import Literal

from pydantic import StrictBool, model_validator

from trust_receipt.models.base import DomainModel, Hex32, Identifier, NonEmptyText, UtcDatetime
from trust_receipt.models.enums import EvidenceSource, PublicationChainStatus
from trust_receipt.models.plans import VerificationPlan
from trust_receipt.models.tasks import TaskSpec
from trust_receipt.models.verification import VerificationResult


class ServiceIdentity(DomainModel):
    service_id: Identifier
    name: NonEmptyText
    identity_scheme: Identifier
    identity_reference: NonEmptyText


class EvidenceDescriptor(DomainModel):
    evidence_id: Identifier
    source: EvidenceSource
    content_hash: Hex32
    uri: NonEmptyText | None
    event_keys: tuple[str, ...]


class Publication(DomainModel):
    authorized: StrictBool
    uri: NonEmptyText | None
    content_hash: Hex32 | None
    transaction_hash: Hex32 | None
    chain_status: PublicationChainStatus

    @model_validator(mode="after")
    def enforce_publication_state(self) -> "Publication":
        if not self.authorized:
            if any(value is not None for value in (self.uri, self.content_hash, self.transaction_hash)):
                raise ValueError("unauthorized publication cannot contain public references")
            if self.chain_status is not PublicationChainStatus.NOT_SUBMITTED:
                raise ValueError("unauthorized publication must be NOT_SUBMITTED")
        if self.chain_status in {PublicationChainStatus.SUBMITTED, PublicationChainStatus.CONFIRMED} and (
            not self.authorized or self.uri is None or self.content_hash is None or self.transaction_hash is None
        ):
            raise ValueError(
                "submitted publication requires authorization, URI, content hash, and transaction hash"
            )
        return self


class Receipt(DomainModel):
    receipt_version: Literal["1.0"]
    receipt_id: Identifier
    task_spec: TaskSpec
    service_identity: ServiceIdentity
    submission_hash: Hex32
    verification_plan: VerificationPlan
    verification_result: VerificationResult
    evidence_manifest: tuple[EvidenceDescriptor, ...]
    created_at: UtcDatetime
    receipt_hash: Hex32
    publication: Publication

    @model_validator(mode="after")
    def enforce_receipt_links(self) -> "Receipt":
        task_id = self.task_spec.task_id
        if self.verification_plan.task_id != task_id or self.verification_result.task_id != task_id:
            raise ValueError("receipt task references must match task_spec.task_id")
        return self
