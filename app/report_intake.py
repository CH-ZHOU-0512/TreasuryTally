"""Shared first/repair upload preview, mapping and explicit adoption UI."""

from __future__ import annotations

from pathlib import Path

from app.report_confirmation import (
    approved_payload,
    clear_approval,
    conversion_identity,
    remember_approval,
    track_identity,
)
from trust_receipt.hashing import content_hash
from trust_receipt.services.conversion_storage import persist_confirmed_conversion
from trust_receipt.services.report_conversion import (
    CONSTANT_FIELDS,
    CONVERSION_FIELDS,
    ConversionInputError,
    convert_report_table,
    read_report_table,
    suggest_field_mapping,
)

FIELD_LABELS = {
    "chain_id": "链编号",
    "token_address": "代币合约地址",
    "transaction_hash": "交易哈希",
    "log_index": "日志序号",
    "block_number": "区块号",
    "block_hash": "区块哈希（可选）",
    "from_address": "付款地址",
    "to_address": "收款地址",
    "amount_base_units": "金额（最小单位整数）",
    "amount": "金额（代币单位十进制）",
    "token_decimals": "代币精度",
    "claimed_total_base_units": "原报表声明总额（最小单位）",
    "claimed_count": "原报表声明笔数",
    "source": "记录来源（未提供时标为服务自报）",
    "amount_base_units_or_amount": "金额与明确单位",
}


def render_report_intake(st, uploaded, *, directory: Path, namespace: str) -> bytes | None:
    """Return only original JSON or an explicitly adopted, ready conversion.

    This component never creates a signer, freezes a task or requests an attempt.
    Namespace includes workspace and first/repair task context supplied by the page.
    """
    if uploaded is None:
        clear_approval(st.session_state, namespace)
        st.session_state.pop(f"{namespace}:table", None)
        return None
    original = uploaded.getvalue()
    filename = uploaded.name
    if Path(filename).suffix.lower() == ".json":
        clear_approval(st.session_state, namespace)
        return original

    source_identity = conversion_identity(content_hash(original), filename, {}, {})
    cache_key = f"{namespace}:table"
    cache = st.session_state.get(cache_key)
    try:
        if cache is None or cache[0] != source_identity:
            clear_approval(st.session_state, namespace)
            with st.spinner("正在读取原始表格，识别转账列…"):
                table = read_report_table(original, filename)
            st.session_state[cache_key] = (source_identity, table)
        else:
            table = cache[1]
    except (ValueError, OSError) as error:
        clear_approval(st.session_state, namespace)
        st.error(f"无法转换这份报表：{error}")
        st.caption("请保留原文件，修正后重新上传。支持受限 CSV 或单工作表 XLSX，不会替换为样例。")
        return None

    st.write(f"原文件：{filename} · {table.input_format.upper()} · {len(table.rows)} 行明细")
    with st.expander("查看原始表格与来源"):
        st.dataframe(
            [dict(zip(table.headers, row, strict=True)) for row in table.rows],
            hide_index=True, width="stretch",
        )
        st.caption(f"读取编码：{table.encoding} · 原文件 SHA-256")
        st.code(table.original_hash, language=None)
    try:
        suggested = suggest_field_mapping(table)
        mapping_notice = None
    except ConversionInputError as error:
        suggested = {}
        mapping_notice = str(error)
    initial = convert_report_table(table)
    with st.expander("检查字段对应与缺失条件", expanded=not initial.ready):
        if mapping_notice:
            st.warning(mapping_notice)
        st.caption("两种金额列只能选一种。普通“金额”列需你明确其单位；不会自动猜测。")
        st.caption("缺事件哈希、日志序号、区块、双方地址或金额，请修正原文件；这里不补造明细。")
        mapping = {}
        columns = st.columns(2)
        options = ("", *table.headers)
        for index, field in enumerate(CONVERSION_FIELDS):
            with columns[index % 2]:
                selected = st.selectbox(
                    FIELD_LABELS[field], options,
                    index=options.index(suggested.get(field, "")),
                    format_func=lambda value: value if value else "未提供 / 不使用此列",
                    key=f"{namespace}:map:{source_identity}:{field}",
                )
                if selected:
                    mapping[field] = selected
        st.caption("仅当原表没有相应列时，明确补充整表共用条件；默认不填任何值。")
        constants = {}
        for field in CONSTANT_FIELDS:
            value = st.text_input(
                f"整表共用{FIELD_LABELS[field]}（原表缺失时填写）",
                key=f"{namespace}:constant:{source_identity}:{field}",
                help="若已选择对应列，请留空。不能同时使用列和共用条件。",
            )
            if value.strip():
                constants[field] = value.strip()

    identity = conversion_identity(table.original_hash, filename, mapping, constants)
    track_identity(st.session_state, namespace, identity)
    candidate_cache_key = f"{namespace}:candidate"
    cache = st.session_state.get(candidate_cache_key)
    if cache is None or cache[0] != identity:
        with st.spinner("正在校验字段与金额精度，生成 JSON 候选…"):
            candidate = convert_report_table(table, mapping=mapping, constants=constants)
        st.session_state[candidate_cache_key] = (identity, candidate)
    else:
        candidate = cache[1]
    if candidate.missing_fields:
        st.warning("还缺少：" + "、".join(FIELD_LABELS.get(field, field) for field in candidate.missing_fields))
    for issue in candidate.issues:
        st.error(issue)
    for warning in candidate.warnings:
        st.caption(warning)
    if not candidate.ready:
        clear_approval(st.session_state, namespace)
        st.info("转换未完成。请修正字段对应或原文件；现在不能整理范围或执行核对。")
        return None

    report = candidate.report
    st.info("JSON 候选已生成，尚未链上核验。请检查预览，再明确采用。")
    st.write(
        f"总额（最小单位）：{report.claimed_total_base_units} · "
        + ("明细派生，非原作者声明" if "claimed_total_base_units" in candidate.derived_fields else "保留原报表声明")
    )
    st.write(
        f"笔数：{report.claimed_count} · "
        + ("明细派生，非原作者声明" if "claimed_count" in candidate.derived_fields else "保留原报表声明")
    )
    with st.expander("查看完整 JSON 候选与字段来源"):
        st.json(report.model_dump(mode="json"))
        st.json({"列映射": candidate.field_mapping, "用户补充": candidate.constants,
                 "明细派生字段": candidate.derived_fields})
        st.code(content_hash(candidate.json_payload), language=None)
    st.download_button(
        "下载 JSON 候选（不是验收回执）", candidate.json_payload,
        "converted-report-candidate.json", "application/json", key=f"{namespace}:download",
    )
    adopted = approved_payload(st.session_state, namespace, identity)
    if adopted is not None:
        st.success("已采用这份转换 JSON。原文件与转换来源已私有留档；接下来仍需确认范围并核对。")
        return adopted
    confirmed = st.checkbox(
        "我已检查原表、字段、金额单位和汇总来源，明确采用这份 JSON；作者身份仍未验证",
        key=f"{namespace}:confirm:{identity}",
    )
    if st.button(
        "确认采用转换 JSON", disabled=not confirmed, type="primary",
        use_container_width=True, key=f"{namespace}:adopt",
    ):
        try:
            normalized = persist_confirmed_conversion(original, candidate, directory, confirmed=confirmed)
            remember_approval(st.session_state, namespace, identity, normalized)
            st.rerun()
        except (ValueError, OSError) as error:
            clear_approval(st.session_state, namespace)
            st.error(f"转换尚未采用：私有留档失败，{error}")
    return None
