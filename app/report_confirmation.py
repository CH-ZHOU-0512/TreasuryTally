"""Document-session approval state; this is not a domain authorization token."""

from __future__ import annotations

import json
from collections.abc import MutableMapping

from trust_receipt.hashing import content_hash


def conversion_identity(
    original_hash: str,
    filename: str,
    mapping: dict[str, str],
    constants: dict[str, str],
) -> str:
    """Bind an approval to every editable conversion input, including provenance."""
    payload = json.dumps(
        [original_hash, filename, mapping, constants],
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return content_hash(payload)


def clear_approval(state: MutableMapping, namespace: str) -> None:
    state.pop(f"{namespace}:approved", None)


def approved_payload(state: MutableMapping, namespace: str, identity: str) -> bytes | None:
    """A stale UI confirmation must never produce an executable report payload."""
    approved = state.get(f"{namespace}:approved")
    if approved is None:
        return None
    if approved[0] != identity:
        clear_approval(state, namespace)
        return None
    return approved[1]


def remember_approval(
    state: MutableMapping, namespace: str, identity: str, payload: bytes,
) -> None:
    """Called by the UI only after ready validation and explicit persistence."""
    state[f"{namespace}:approved"] = (identity, payload)
