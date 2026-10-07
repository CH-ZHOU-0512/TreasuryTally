"""Amount precision, provenance, integrity and history regression coverage."""

import pytest

from tests.reporting.conftest import ROOT, report_input
from trust_receipt.hashing import receipt_hash
from trust_receipt.m9.revisions import build_receipt_revision
from trust_receipt.models import VerificationOutcome
from trust_receipt.reporting import ReportAttemptInput, build_business_report
from trust_receipt.reporting.formatting import format_amount


@pytest.mark.parametrize("case", sorted(path.stem for path in (ROOT / "fixtures/m1/cases").glob("*.json")))
def test_all_cases_keep_original_verdict_and_exact_totals(case):
    item = report_input(case)
    original_bytes = item.receipt.model_dump_json()
    view = build_business_report(item.receipt, item.submission, fund_flow=item.fund_flow, source_mode="fixture")
    assert view.outcome == item.receipt.verification_result.outcome
    assert view.current.claimed.base_units == item.submission.claimed_total_base_units
    if view.current.calculated:
        assert view.current.calculated.base_units == item.receipt.verification_result.calculated_total_base_units
    assert len(view.current.flow_rows) == len(item.fund_flow.edges)
    assert item.receipt.model_dump_json() == original_bytes
    assert view.source_mode_label.startswith("离线")
    assert "不认证原作者" in view.current.identity_label
    assert view.current.evidence_as_of is not None


@pytest.mark.parametrize(
    "amount,decimals,display",
    [
        ("1", 18, "0.000000000000000001"),
        ("321794352786", 18, "0.000000321794352786"),
        ("123456789012345678901234567890123456", 18, "123,456,789,012,345,678.901234567890123456"),
        ("0", 18, "0"),
        ("-1", 18, "-0.000000000000000001"),
    ],
)
def test_lossless_display(amount, decimals, display):
    assert format_amount(amount, decimals, signed=True).display == display


def test_decimal_error_does_not_expose_comparable_difference():
    item = report_input("decimal-unit-error")
    view = build_business_report(item.receipt, item.submission, fund_flow=item.fund_flow)
    assert view.current.difference is None
    assert "精度" in view.current.difference_reason


@pytest.mark.parametrize("mixed", (False, True))
def test_wrong_or_mixed_token_never_labels_claim_as_confirmed_asset(mixed):
    wrong = "0x" + "f" * 40

    def transform(fixture):
        records = fixture.submission.transfers
        changed = tuple(record.model_copy(update={"token_address": wrong}) for record in records)
        if mixed:
            changed = (records[0], *changed)
        submission = fixture.submission.model_copy(update={"transfers": changed})
        return fixture.model_copy(update={"submission": submission})

    item = report_input("correct-basic", transform=transform)
    view = build_business_report(item.receipt, item.submission, fund_flow=item.fund_flow)
    assert view.current.difference is None
    assert "混合代币" in view.current.claimed.unit if mixed else "ffffff" in view.current.claimed.unit
    assert view.scope.token.short not in view.current.claimed.unit


def test_inconclusive_is_not_failed_or_zero():
    case = next(path.stem for path in (ROOT / "fixtures/m1/cases").glob("*.json") if "insufficient" in path.stem)
    item = report_input(case)
    view = build_business_report(item.receipt, item.submission, fund_flow=item.fund_flow)
    assert view.outcome == VerificationOutcome.INCONCLUSIVE
    assert view.current.difference is None
    assert view.current.calculated is None
    assert "服务失败" in view.current.uncertainties[0]


def test_tampered_receipt_and_unbound_flow_rejected(failing_input):
    item = failing_input
    bad = item.receipt.model_copy(update={"receipt_id": "tampered"})
    with pytest.raises(ValueError, match="integrity"):
        build_business_report(bad, item.submission)
    wrong_flow = item.fund_flow.model_copy(update={"claimed_total_base_units": "1"})
    with pytest.raises(ValueError, match="fund flow"):
        build_business_report(item.receipt, item.submission, fund_flow=wrong_flow)


def test_private_notes_and_ai_explanation_not_copied(failing_input):
    item = failing_input
    findings = tuple(
        f.model_copy(update={"explanation": "API_KEY=private DO NOT EXPORT https://rpc.invalid/key"})
        for f in item.receipt.verification_result.findings
    )
    result = item.receipt.verification_result.model_copy(update={"findings": findings})
    draft = item.receipt.model_copy(update={"verification_result": result})
    receipt = draft.model_copy(update={"receipt_hash": receipt_hash(draft)})
    dump = build_business_report(receipt, item.submission, fund_flow=item.fund_flow).model_dump_json()
    assert "API_KEY" not in dump and "rpc.invalid" not in dump and "DO NOT EXPORT" not in dump


def test_two_attempts_keep_original_and_require_verified_relation(failing_input):
    # Reuse the original scope and missing report; a later inconclusive retry is
    # sufficient to exercise immutable history without inventing a PASS.
    first = failing_input
    second = report_input(attempt=2)
    parent = build_receipt_revision(first.receipt, attempt=1)
    child = build_receipt_revision(second.receipt, attempt=2, parent=parent)
    view = build_business_report(
        second.receipt, second.submission, fund_flow=second.fund_flow, previous=first, revisions=(parent, child)
    )
    assert view.repair_verified
    assert view.previous.outcome == VerificationOutcome.FAIL
    assert view.current.attempt == 2
    assert "第三次" in view.next_step
    unverified = build_business_report(
        second.receipt, second.submission, previous=ReportAttemptInput(first.receipt, first.submission)
    )
    assert not unverified.repair_verified
    assert "未核实" in unverified.repair_label
