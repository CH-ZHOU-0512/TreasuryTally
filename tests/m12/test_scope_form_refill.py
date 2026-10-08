"""Native upload and actual scope controls; all candidates are explicit offline doubles."""
# ruff: noqa: RUF001 -- Exact frozen Chinese UI labels.

from pathlib import Path

from streamlit.testing.v1 import AppTest

from app.report_experience import contract_example_bytes
from app.scope_draft import blank_manual_candidate
from app.scope_request import GUIDED, RAW
from tests.m12.test_conversion_page_flow import button
from trust_receipt.orchestration import load_vertical_demo_fixture
from trust_receipt.orchestration.m5 import candidate_from_fixture

ROOT = Path(__file__).parents[2]


def control(items, prefix):
    return next(item for item in items if item.label.startswith(prefix))


def native_page(monkeypatch):
    page = AppTest.from_file(str(ROOT / "app" / "streamlit_app.py"), default_timeout=30).run()
    control(page.file_uploader, "服务商报表").set_value(
        ("synthetic.json", contract_example_bytes(ROOT), "application/json")
    ).run()
    candidate = candidate_from_fixture(load_vertical_demo_fixture(ROOT))
    calls = []

    def draft(request):
        calls.append(request)
        return candidate  # Repeated ID deliberately tests repeated valid model output.

    monkeypatch.setattr(page.session_state["runtime"].workflow, "draft_task", draft)
    request = (
        f"请核对网络链编号 {candidate.chain_id} 的代币 {candidate.token_address}；"
        f"付款账户 {'、'.join(candidate.treasury_addresses)}，"
        f"收款账户 {'、'.join(candidate.recipient_addresses)}，"
        f"起始区块 {candidate.start_block} 至结束区块 {candidate.end_block}（含两端），"
        "排除资金账户间的内部互转，记录上限 200。"
    )
    return page, candidate, request, calls


def assert_candidate_controls(page, candidate):
    assert control(page.number_input, "核对哪条链").value == candidate.chain_id
    assert control(page.text_input, "核对哪种代币").value == candidate.token_address
    assert control(page.number_input, "起始区块").value == candidate.start_block
    assert control(page.number_input, "结束区块").value == candidate.end_block
    assert control(page.text_area, "资金账户").value == "\n".join(candidate.treasury_addresses)
    assert control(page.text_area, "资助对象").value == "\n".join(candidate.recipient_addresses)
    assert control(page.checkbox, "排除资金账户").value is True


def test_complete_natural_language_in_default_guided_mode_can_draft(monkeypatch):
    page, candidate, request, calls = native_page(monkeypatch)
    assert control(page.radio, "范围填写方式").value == GUIDED
    control(page.text_area, "说明要核对的范围").set_value(request).run()
    assert not page.exception and "uploaded_service" in page.session_state
    assert not button(page, "整理核对范围").disabled
    button(page, "整理核对范围").click().run()
    assert not page.exception and calls == [request]
    assert_candidate_controls(page, candidate)
    assert "task" not in page.session_state


def test_same_candidate_preserves_edits_on_rerun_then_requires_confirmation(monkeypatch):
    page, candidate, request, calls = native_page(monkeypatch)
    control(page.text_area, "说明要核对的范围").set_value(request).run()
    button(page, "整理核对范围").click().run()
    control(page.number_input, "起始区块").set_value(0)
    button(page, "确认范围，继续").click().run()
    page.run()
    assert control(page.number_input, "起始区块").value == 0
    assert "task" not in page.session_state and calls == [request]
    control(page.number_input, "起始区块").set_value(candidate.start_block)
    control(page.checkbox, "我已核对以上").check()
    button(page, "确认范围，继续").click().run()
    assert not page.exception and "task" in page.session_state
    assert page.session_state["task"].start_block == candidate.start_block
    assert page.session_state["scope-request"] == request and calls == [request]


def test_missing_candidate_numbers_remain_empty_and_cannot_be_confirmed(monkeypatch):
    page, _candidate, request, calls = native_page(monkeypatch)
    monkeypatch.setattr(page.session_state["runtime"].workflow, "draft_task",
                        lambda _request: blank_manual_candidate())
    control(page.text_area, "说明要核对的范围").set_value(request).run()
    button(page, "整理核对范围").click().run()
    for prefix in ("核对哪条链", "起始区块", "结束区块"):
        assert control(page.number_input, prefix).value is None
    control(page.checkbox, "我已核对以上").check()
    button(page, "确认范围，继续").click().run()
    assert not page.exception and "task" not in page.session_state and not calls
    assert any("请补齐链编号和起止区块" in item.value for item in page.error)


def test_regenerating_same_candidate_resets_invalid_old_fields_and_confirmation(monkeypatch):
    page, candidate, request, calls = native_page(monkeypatch)
    control(page.radio, "范围填写方式").set_value(RAW).run()
    control(page.text_area, "说明要核对的范围").set_value(request).run()
    button(page, "整理核对范围").click().run()
    assert_candidate_controls(page, candidate)
    control(page.number_input, "核对哪条链").set_value(1)
    control(page.text_input, "核对哪种代币").set_value("0x" + "a" * 40)
    control(page.checkbox, "我已核对以上").check()
    button(page, "确认范围，继续").click().run()
    assert not page.exception and "task" not in page.session_state
    assert any("任务未确认" in item.value for item in page.error)
    button(page, "整理核对范围").click().run()
    assert not page.exception and calls == [request, request]
    assert_candidate_controls(page, candidate)
    assert control(page.checkbox, "我已核对以上").value is False
    assert "task" not in page.session_state
