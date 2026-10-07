from pathlib import Path

from streamlit.testing.v1 import AppTest


def button(page, label):
    return next(item for item in page.button if item.label == label)


def test_page_history_drilldown_and_next_manual_choice():
    page = AppTest.from_file(str(Path(__file__).parents[2] / "app" / "streamlit_app.py"), default_timeout=20).run()
    button(page, "生成可核对的任务候选").click().run()
    # Existing scope confirmation uses two explicit acknowledgements.
    page.checkbox[1].check()
    button(page, "确认并冻结 TaskSpec").click().run()
    button(page, "开始验收 · Attempt 1").click().run()
    next(item for item in page.radio if item.label == "报表服务").set_value("服务 B · 完整交付")
    button(page, "补交或换源 · Attempt 2（最后一次）").click().run()  # noqa: RUF001
    page.toggle[0].set_value(True).run()
    assert not page.exception
    assert any(metric.label == "修复后通过" and metric.value == "1" for metric in page.metric)
    assert any(metric.label == "未通过" and metric.value == "1" for metric in page.metric)
    assert len(next(item for item in page.selectbox if item.label == "来源回执").options) == 2
    choice = next(item for item in page.radio if item.label == "人工选择服务")
    choice.set_value(choice.options[1]).run()
    button(page, "确认选择").click().run()
    assert not page.exception
    button(page, "开始下一次报表验收").click().run()
    button(page, "生成可核对的任务候选").click().run()
    page.checkbox[1].check()
    button(page, "确认并冻结 TaskSpec").click().run()
    assert next(item for item in page.radio if item.label == "报表服务").value == "服务 B · 完整交付"
    assert not page.exception
