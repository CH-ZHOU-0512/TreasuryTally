"""Stable port for a future commitment anchor implementation."""

from typing import Protocol

from trust_receipt.models import CommitmentAnchor, DeliveryCommitment, TaskCommitment


class CommitmentAnchorPort(Protocol):
    def read_task_anchor(self, commitment: TaskCommitment) -> CommitmentAnchor: ...

    def read_delivery_anchor(self, commitment: DeliveryCommitment) -> CommitmentAnchor: ...
