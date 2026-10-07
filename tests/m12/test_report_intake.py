"""AppTest injects upload bytes; it does not prove native browser file selection."""

import json
from dataclasses import dataclass
from pathlib import Path

from streamlit.testing.v1 import AppTest

from app.report_experience import strict_template_bytes

ROOT = Path(__file__).parents[2]
CSV = ROOT / "fixtures" / "m14" / "conversion" / "correct-token-units.csv"


@dataclass
class Upload:
    name: str
    payload: bytes

    def getvalue(self):
        return self.payload


def intake_harness():
    from pathlib import Path

    import streamlit as st

    from app.report_intake import render_report_intake

    payload = render_report_intake(
        st, st.session_state.get("test_upload"),
        directory=Path(st.session_state["test_directory"]), namespace="test:first",
    )
    st.session_state["intake_payload"] = payload
    st.button("继续", disabled=payload is None)


def page_for(tmp_path, upload):
    page = AppTest.from_function(intake_harness, default_timeout=20)
    page.session_state["test_directory"] = str(tmp_path)
    page.session_state["test_upload"] = upload
    return page.run()


def button(page, label):
    return next(item for item in page.button if item.label == label)


def adopt(page):
    page.checkbox[0].check().run()
    return button(page, "确认采用转换 JSON").click().run()


def test_ready_csv_requires_confirmation_before_any_private_persistence(tmp_path):
    page = page_for(tmp_path, Upload(CSV.name, CSV.read_bytes()))
    assert not page.exception
    assert page.session_state["intake_payload"] is None
    assert button(page, "确认采用转换 JSON").disabled
    assert button(page, "继续").disabled
    assert not list(tmp_path.iterdir())
    assert any("180674489737" in item.value for item in page.markdown)
    adopt(page)
    assert not page.exception
    assert page.session_state["intake_payload"] is not None
    assert not button(page, "继续").disabled
    assert len(list(tmp_path.rglob("*.*"))) == 3
    assert "uploaded_service" not in page.session_state
    assert "task" not in page.session_state


def test_changed_file_revokes_approval_even_when_normalized_json_is_identical(tmp_path):
    page = adopt(page_for(tmp_path, Upload(CSV.name, CSV.read_bytes())))
    page.session_state["test_upload"] = Upload("renamed.csv", CSV.read_bytes())
    page.run()
    assert not page.exception
    assert page.session_state["intake_payload"] is None
    assert not page.checkbox[0].value
    assert button(page, "继续").disabled


def test_mapping_change_and_return_require_fresh_checkbox(tmp_path):
    page = adopt(page_for(tmp_path, Upload(CSV.name, CSV.read_bytes())))
    next(item for item in page.selectbox if item.label == "日志序号").set_value("").run()
    assert not page.exception
    assert button(page, "继续").disabled
    assert not page.checkbox
    next(item for item in page.selectbox if item.label == "日志序号").set_value("日志序号").run()
    assert not page.exception
    assert not page.checkbox[0].value
    assert button(page, "确认采用转换 JSON").disabled


def test_missing_event_identity_never_has_an_adoption_or_row_override(tmp_path):
    data = CSV.read_text(encoding="utf-8").splitlines()
    rows = [line.split(",") for line in data]
    index = rows[0].index("交易哈希")
    payload = "\n".join(",".join(row[:index] + row[index + 1:]) for row in rows).encode("utf-8")
    page = page_for(tmp_path, Upload("missing-event.csv", payload))
    assert not page.exception
    assert button(page, "继续").disabled
    assert any("交易哈希" in item.value for item in page.warning)
    assert not any(item.label == "确认采用转换 JSON" for item in page.button)
    assert all(item.label.startswith("整表共用") for item in page.text_input)
    assert not list(tmp_path.iterdir())


def test_derived_summary_is_explicit_and_large_integer_never_displayed_as_float(tmp_path):
    data = CSV.read_text(encoding="utf-8").splitlines()
    payload = "\n".join(",".join(line.split(",")[:-2]) for line in data).encode("utf-8")
    page = page_for(tmp_path, Upload("detail-only.csv", payload))
    assert not page.exception
    assert any("明细派生，非原作者声明" in item.value for item in page.markdown)  # noqa: RUF001
    assert button(page, "确认采用转换 JSON").disabled


def test_scientific_amount_blocks_adoption_without_changing_original(tmp_path):
    payload = CSV.read_bytes().replace(b"0.000000180674489737", b"1.80674489737e-7")
    page = page_for(tmp_path, Upload("scientific.csv", payload))
    assert not page.exception
    assert button(page, "继续").disabled
    assert any("科学计数法" in item.value for item in page.error)
    assert not list(tmp_path.iterdir())


def test_strict_json_keeps_original_bytes_without_new_confirmation(tmp_path):
    payload = strict_template_bytes()
    page = page_for(tmp_path, Upload("report.json", payload))
    assert not page.exception
    assert page.session_state["intake_payload"] == payload
    assert not page.checkbox
    assert not button(page, "继续").disabled
    assert not list(tmp_path.iterdir())


def test_failed_private_retention_does_not_adopt_or_expose_execution(tmp_path, monkeypatch):
    def fail(*_args, **_kwargs):
        raise OSError("test: private storage unavailable")

    monkeypatch.setattr("app.report_intake.persist_confirmed_conversion", fail)
    page = adopt(page_for(tmp_path, Upload(CSV.name, CSV.read_bytes())))
    assert not page.exception
    assert page.session_state["intake_payload"] is None
    assert button(page, "继续").disabled
    assert any("私有留档失败" in item.value for item in page.error)


def test_removed_upload_does_not_restore_previous_adoption(tmp_path):
    page = adopt(page_for(tmp_path, Upload(CSV.name, CSV.read_bytes())))
    page.session_state["test_upload"] = None
    page.run()
    assert button(page, "继续").disabled
    page.session_state["test_upload"] = Upload(CSV.name, CSV.read_bytes())
    page.run()
    assert not page.exception
    assert not page.checkbox[0].value
    assert button(page, "继续").disabled


def test_explicit_constants_can_fill_missing_common_field_but_changes_revoke_adoption(tmp_path):
    page = page_for(tmp_path, Upload(CSV.name, CSV.read_bytes()))
    next(item for item in page.selectbox if item.label == "链编号").set_value("").run()
    assert button(page, "继续").disabled
    next(item for item in page.text_input if item.label.startswith("整表共用链编号")).set_value("11155111").run()
    assert not page.exception
    adopt(page)
    assert not button(page, "继续").disabled
    next(item for item in page.text_input if item.label.startswith("整表共用链编号")).set_value("1").run()
    assert not page.exception
    assert not page.checkbox[0].value
    assert button(page, "继续").disabled


def test_duplicate_rows_and_original_summary_survive_ui_adoption(tmp_path):
    lines = CSV.read_bytes().splitlines()
    payload = b"\n".join([*lines, lines[1]])
    page = adopt(page_for(tmp_path, Upload("duplicate.csv", payload)))
    assert not page.exception
    normalized = json.loads(page.session_state["intake_payload"])
    assert normalized["claimed_total_base_units"] == "180674489737"
    assert normalized["claimed_count"] == 1
    assert len(normalized["transfers"]) == 2
    assert normalized["transfers"][0] == normalized["transfers"][1]
