"""Standalone read-only verification for a public Receipt 1.0 artifact."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import urlparse

import httpx

from trust_receipt.m9 import (
    PublicReceiptReference,
    PublicReferenceKind,
    PublicVerificationStatus,
    ReceiptRevision,
    ResolvedPublicReceipt,
    verify_public_reference,
)


class _SingleArtifactResolver:
    def __init__(self, resolved: ResolvedPublicReceipt) -> None:
        self._resolved = resolved

    def resolve(self, reference: PublicReceiptReference) -> ResolvedPublicReceipt:
        del reference
        return self._resolved


def _read_public_bytes(location: str, timeout_seconds: float) -> bytes:
    local_path = Path(location)
    if local_path.is_file():
        return local_path.read_bytes()
    parsed = urlparse(location)
    if parsed.scheme in {"http", "https"}:
        response = httpx.get(location, timeout=timeout_seconds, follow_redirects=True)
        response.raise_for_status()
        return response.content
    if parsed.scheme:
        raise ValueError("receipt location must be a local path or an HTTP(S) URI")
    return local_path.read_bytes()


def _load_revision(path: Path | None) -> ReceiptRevision | None:
    return ReceiptRevision.model_validate_json(path.read_bytes()) if path is not None else None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipt", help="local public JSON path or HTTP(S) URI")
    parser.add_argument("--kind", choices=[kind.value for kind in PublicReferenceKind], required=True)
    parser.add_argument("--value", help="reference value; defaults to receipt location for URI")
    parser.add_argument("--attempt", type=int, choices=(1, 2), required=True)
    parser.add_argument("--expected-content-hash")
    parser.add_argument("--feedback-transaction-hash")
    parser.add_argument("--revision", type=Path)
    parser.add_argument("--parent-revision", type=Path)
    parser.add_argument("--timeout-seconds", type=float, default=30.0)
    args = parser.parse_args()

    kind = PublicReferenceKind(args.kind)
    value = args.value or (args.receipt if kind is PublicReferenceKind.URI else None)
    if value is None:
        parser.error("--value is required unless --kind URI is used")
    try:
        payload = _read_public_bytes(args.receipt, args.timeout_seconds)
        resolved = ResolvedPublicReceipt(
            payload=payload,
            attempt=args.attempt,
            expected_content_hash=args.expected_content_hash,
            feedback_transaction_hash=args.feedback_transaction_hash,
            revision=_load_revision(args.revision),
            parent_revision=_load_revision(args.parent_revision),
            evidence_refs=(args.receipt,),
        )
        result = verify_public_reference(
            PublicReceiptReference(kind=kind, value=value),
            _SingleArtifactResolver(resolved),
        )
    except (httpx.HTTPError, OSError, ValueError) as exc:
        print(json.dumps({"status": "INCONCLUSIVE", "reason": type(exc).__name__}, sort_keys=True))
        return 2
    print(json.dumps(result.model_dump(mode="json"), ensure_ascii=False, sort_keys=True))
    if result.status is PublicVerificationStatus.VERIFIED:
        return 0
    return 2 if result.status is PublicVerificationStatus.INCONCLUSIVE else 1


if __name__ == "__main__":
    raise SystemExit(main())
