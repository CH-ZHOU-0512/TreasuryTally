"""Business-only presentation; test exports below are explicit byte doubles."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from tests.reporting.conftest import report_input
from trust_receipt.reporting import build_business_report

ROOT = Path(__file__).parents[2]


def harness():
    import streamlit as st

    from app.business_report import render_business_report

    render_business_report(
        st, st.session_state["report"], graph=st.session_state.get("graph"),
        exports=st.session_state.get("exports"), receipt_json="original-json-test-bytes",
    )


def page_for(report, **kwargs):
    page = AppTest.from_function(harness, default_timeout=15)
    page.session_state["report"] = report
    for key, value in kwargs.items():
        page.session_state[key] = value
    return page.run()


@pytest.mark.parametrize("case", sorted(path.stem for path in (ROOT / "fixtures/m1/cases").glob("*.json")))
def test_each_verdict_preserves_exact_business_amounts_without_technical_directory(case):
    item = report_input(case)
    view = build_business_report(item.receipt, item.submission, fund_flow=item.fund_flow, source_mode="fixture")
    page = page_for(view)
    assert not page.exception
    assert [metric.value for metric in page.metric] == [
        view.current.claimed.display,
        view.current.calculated.display if view.current.calculated else "无法确定",
        view.current.difference.display if view.current.difference else "无法确定",
    ]
    assert not page.expander and not page.json
    assert len(page.get("download_button")) == 1
    assert not any("Offline explanation" in item.value for item in page.markdown)


def test_pass_does_not_render_empty_problem_cards():
    item = report_input("correct-basic")
    view = build_business_report(item.receipt, item.submission, fund_flow=item.fund_flow)
    assert view.outcome.value == "PASS"
    page = page_for(view)
    assert not page.exception
    assert not any(item.value == "#### 需要处理的差异" for item in page.markdown)


def test_many_same_kind_findings_are_summarized_without_mutating_report():
    item = report_input()
    view = build_business_report(item.receipt, item.submission, fund_flow=item.fund_flow)
    repeated = view.current.model_copy(update={"findings": (view.current.findings[0],) * 200})
    view = view.model_copy(update={"current": repeated})
    page = page_for(view)
    assert not page.exception
    assert len(view.current.findings) == 200
    bodies = [element.proto.body for element in page.get("html")]
    assert sum("finding-card" in body for body in bodies) == 1
    assert any("200 条" in body for body in bodies)


def test_export_is_lazy_and_cached_without_new_verification():
    item = report_input()
    view = build_business_report(item.receipt, item.submission, fund_flow=item.fund_flow)
    calls = []

    def export(_view):
        calls.append(_view.current.receipt_hash)
        return b"explicit-test-output-not-a-real-docx"

    page = page_for(view, exports=(export, export))
    assert not calls
    next(item for item in page.button if item.label == "生成Word 报告").click().run()
    assert not page.exception and len(calls) == 1
    page.run()
    assert len(calls) == 1
    assert len(page.get("download_button")) == 2
