from pathlib import Path

from streamlit.testing.v1 import AppTest

from app.styles import APP_CSS


def test_responsive_css_forces_narrow_layout_to_single_column() -> None:
    assert "@media (max-width:760px)" in APP_CSS
    assert 'div[data-testid="stHorizontalBlock"] { flex-direction:column !important' in APP_CSS
    assert 'div[data-testid="column"] { width:100% !important' in APP_CSS
    assert "overflow-wrap:anywhere" in APP_CSS
    assert "padding:.7rem .85rem 4rem" in APP_CSS


def test_page_starts_without_execution_controls_before_confirmation() -> None:
    app_path = Path(__file__).parents[2] / "app" / "streamlit_app.py"
    page = AppTest.from_file(str(app_path), default_timeout=20).run()

    assert not page.exception
    assert any(button.label == "生成可核对的任务候选" for button in page.button)
    assert not any("Attempt" in button.label for button in page.button)


def test_page_walks_fail_to_pass_without_overwriting_attempt_one() -> None:
    app_path = Path(__file__).parents[2] / "app" / "streamlit_app.py"
    page = AppTest.from_file(str(app_path), default_timeout=20).run()
    page.button[0].click().run(timeout=20)

    page.button[1].click().run(timeout=20)
    assert not any("Attempt" in button.label for button in page.button)

    page.checkbox[1].check()
    page.button[1].click().run(timeout=20)
    assert not page.exception
    assert any(button.label == "开始验收 · Attempt 1" for button in page.button)

    page.button[0].click().run(timeout=20)
    assert [metric.value for metric in page.metric] == ["110000", "2", "1"]

    next(radio for radio in page.radio if radio.label == "报表服务").set_value("服务 B · 完整交付")
    page.button[0].click().run(timeout=20)
    assert [metric.value for metric in page.metric] == ["110000", "2", "1", "110000", "2", "0"]
    assert not page.exception


def test_page_renders_inconclusive_as_evidence_shortfall() -> None:
    app_path = Path(__file__).parents[2] / "app" / "streamlit_app.py"
    page = AppTest.from_file(str(app_path), default_timeout=20).run()
    next(radio for radio in page.radio if radio.label == "独立证据").set_value("模拟证据不可用").run(timeout=20)
    page.button[0].click().run(timeout=20)
    page.checkbox[1].check()
    page.button[1].click().run(timeout=20)
    page.button[0].click().run(timeout=20)

    assert any("不能形成服务负面结论" in warning.value for warning in page.warning)
    assert [metric.value for metric in page.metric] == ["—", "—", "1"]


def test_live_mode_is_selectable_with_configured_rpc(monkeypatch) -> None:
    monkeypatch.setenv("ETH_RPC_URL", "https://unused.invalid")
    app_path = Path(__file__).parents[2] / "app" / "streamlit_app.py"
    page = AppTest.from_file(str(app_path), default_timeout=20).run()
    next(radio for radio in page.radio if radio.label == "独立证据").set_value("真实 Sepolia RPC").run(timeout=20)

    assert not page.exception
    assert not page.error
    assert next(radio for radio in page.radio if radio.label == "独立证据").value == "真实 Sepolia RPC"


def test_production_mode_is_locked_to_real_deepseek_and_rpc(monkeypatch) -> None:
    monkeypatch.setenv("APP_REQUIRE_LIVE", "true")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-only")
    monkeypatch.setenv("DEEPSEEK_MODEL", "deepseek-test")
    monkeypatch.setenv("ETH_RPC_URL", "https://unused.invalid")
    app_path = Path(__file__).parents[2] / "app" / "streamlit_app.py"
    page = AppTest.from_file(str(app_path), default_timeout=20).run()

    assert not page.exception
    assert page.selectbox[0].value == "DeepSeek 真实模型"
    assert list(page.selectbox[0].options) == ["DeepSeek 真实模型"]
    assert page.radio[0].value == "真实 Sepolia RPC"
