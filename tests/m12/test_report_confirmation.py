"""UI adoption never survives changed source, mapping, conditions or namespace."""

import pytest

from app.report_confirmation import (
    approved_payload,
    clear_approval,
    conversion_identity,
    remember_approval,
    track_identity,
)


def test_identity_is_stable_under_dictionary_order_not_values():
    assert conversion_identity("hash", "report.csv", {"a": "A", "b": "B"}, {}) == (
        conversion_identity("hash", "report.csv", {"b": "B", "a": "A"}, {})
    )


@pytest.mark.parametrize("change", ["hash", "filename", "mapping", "constants"])
def test_every_conversion_input_change_revokes_previous_approval(change):
    parameters = {
        "original_hash": "original",
        "filename": "report.csv",
        "mapping": {"transaction_hash": "tx"},
        "constants": {"token_decimals": "18"},
    }
    state = {}
    identity = conversion_identity(**parameters)
    remember_approval(state, "workspace:first", identity, b"confirmed-json")
    assert approved_payload(state, "workspace:first", identity) == b"confirmed-json"
    if change == "hash":
        parameters["original_hash"] = "changed"
    elif change == "filename":
        parameters["filename"] = "renamed.csv"
    elif change == "mapping":
        parameters["mapping"] = {"transaction_hash": "other-tx"}
    else:
        parameters["constants"] = {"token_decimals": "6"}
    assert approved_payload(state, "workspace:first", conversion_identity(**parameters)) is None
    assert not state
    # Returning to old controls does not resurrect the old approval.
    assert approved_payload(state, "workspace:first", identity) is None


def test_first_repair_and_workspaces_do_not_share_approval():
    state = {}
    remember_approval(state, "workspace:first", "identity", b"confirmed-json")
    assert approved_payload(state, "workspace:repair:task", "identity") is None
    assert approved_payload(state, "other:first", "identity") is None
    clear_approval(state, "workspace:first")
    assert approved_payload(state, "workspace:first", "identity") is None


def test_changed_inputs_clear_old_checkbox_even_when_returning_to_old_identity():
    state = {}
    track_identity(state, "first", "a")
    state["first:confirm:a"] = True
    remember_approval(state, "first", "a", b"json")
    track_identity(state, "first", "b")
    assert "first:confirm:a" not in state
    track_identity(state, "first", "a")
    assert "first:confirm:a" not in state
    assert approved_payload(state, "first", "a") is None
