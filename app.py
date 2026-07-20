from __future__ import annotations

import json
import time
from datetime import date
from typing import Any

import streamlit as st

from schemas import COMMON_FIELDS, EXPERIMENTS
from calculations import calculate, final_result
from word_export import export_doc

st.set_page_config(
    page_title="BPLab CMA原始记录系统",
    page_icon="🧪",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# 轻量化样式：不加载图片、动画和复杂前端组件，适配较旧平板。
st.markdown(
    """
<style>
.block-container{max-width:760px;padding-top:.65rem;padding-bottom:2rem;padding-left:.75rem;padding-right:.75rem}
.stApp{background:#f7f9fb}
h1{font-size:1.48rem!important;margin:.1rem 0!important}
h2,h3{font-size:1.08rem!important}
[data-testid="stCaptionContainer"]{color:#60717c}
.stButton button,.stDownloadButton button{min-height:44px;width:100%}
.stTextInput input,.stNumberInput input,.stDateInput input{min-height:42px}
div[data-baseweb="select"]{min-height:42px}
textarea{min-height:88px!important}
hr{margin:.6rem 0!important}
@media(max-width:700px){
  .block-container{padding-left:.55rem;padding-right:.55rem}
  h1{font-size:1.34rem!important}
  .stRadio>div{gap:.15rem}
}
</style>
""",
    unsafe_allow_html=True,
)

st.title("大连标普检测有限公司")
st.caption("DALIAN BIAOPU TESTING CO., LTD.｜CMA电子原始记录系统（轻量版，无Logo）")

codes = list(EXPERIMENTS)
code = st.selectbox(
    "检测项目",
    codes,
    format_func=lambda c: EXPERIMENTS[c]["name"],
)
conf = EXPERIMENTS[code]
st.caption(f"检测依据：{conf.get('std', '')}")
record_key = f"record_{code}"


def initial_field(field: tuple[Any, ...]) -> Any:
    """Return the default value declared by a schema field."""
    _key, _label, field_type, default, *_rest = field
    if field_type == "date":
        return default or str(date.today())
    return default


def make_new_record() -> dict[str, Any]:
    common = {field[0]: initial_field(field) for field in COMMON_FIELDS}
    common["record_no"] = (
        f"BP-{date.today().strftime('%Y%m%d')}-{int(time.time()) % 100000:05d}"
    )

    setup = {
        field[0]: initial_field(field) for field in conf.get("setup", [])
    }
    checks = {name: True for name in conf.get("checks", [])}

    rows: list[dict[str, Any]] = []
    for index in range(conf["n"]):
        row = {
            field[0]: initial_field(field) for field in conf["row_fields"]
        }
        if code == "shock":
            row["sample_id"] = row.get("sample_id") or f"T{index + 1}"
        else:
            row["sample_id"] = row.get("sample_id") or f"S{index + 1}"
        if code == "hv":
            row["sample_id"] = f"S{(index // 2) + 1}"
            row["face"] = f"面{(index % 2) + 1}"
        rows.append(row)

    auxiliary: list[dict[str, Any]] = []
    if conf.get("aux"):
        for label in conf["aux"]["rows"]:
            item = {
                field[0]: initial_field(field)
                for field in conf["aux"]["fields"]
            }
            item["_label"] = label
            auxiliary.append(item)

    return {
        "common": common,
        "setup": setup,
        "checks": checks,
        "rows": rows,
        "aux": auxiliary,
        "anomalies": [
            {
                "time": "",
                "sample": "",
                "description": "",
                "impact": "",
                "action": "",
                "responsible": "",
                "reviewer": "",
            }
            for _ in range(4)
        ],
        "archives": {name: False for name in conf.get("archives", [])},
    }


if record_key not in st.session_state:
    st.session_state[record_key] = make_new_record()
record = st.session_state[record_key]

# 草稿导入放在折叠区，避免旧平板首屏过长。
with st.expander("导入JSON草稿（可选）", expanded=False):
    uploaded = st.file_uploader(
        "选择此前下载的JSON草稿",
        type=["json"],
        key=f"upload_{code}",
    )
    if uploaded is not None:
        try:
            payload = json.load(uploaded)
            if payload.get("experiment") != code:
                st.error("草稿所属检测项目与当前项目不一致。")
            elif not isinstance(payload.get("record"), dict):
                st.error("草稿格式不正确。")
            else:
                st.session_state[record_key] = payload["record"]
                record = st.session_state[record_key]
                st.success("草稿已导入。")
        except (ValueError, TypeError, json.JSONDecodeError) as exc:
            st.error(f"草稿读取失败：{exc}")

steps = [
    "1 基本信息",
    "2 设备与过程",
    "3 原始数据",
    "4 辅助数据",
    "5 异常归档",
    "6 结果导出",
]
step = st.selectbox("填写步骤", steps)


def field_widget(
    field: tuple[Any, ...], current: Any, widget_key: str
) -> Any:
    key, label, field_type, _default, *rest = field
    full_key = f"{widget_key}_{key}"

    if field_type == "text":
        return st.text_input(label, value="" if current is None else str(current), key=full_key)
    if field_type == "area":
        return st.text_area(
            label,
            value="" if current is None else str(current),
            height=88,
            key=full_key,
        )
    if field_type == "number":
        try:
            numeric = float(current or 0)
        except (TypeError, ValueError):
            numeric = 0.0
        return st.number_input(
            label,
            value=numeric,
            step=0.001,
            format="%.4f",
            key=full_key,
        )
    if field_type == "date":
        try:
            value = date.fromisoformat(str(current)) if current else date.today()
        except ValueError:
            value = date.today()
        return str(st.date_input(label, value=value, key=full_key))
    if field_type == "select":
        options = list(rest[0])
        selected = current if current in options else options[0]
        return st.selectbox(
            label,
            options,
            index=options.index(selected),
            key=full_key,
        )
    return current


def render_form(
    fields: list[tuple[Any, ...]],
    target: dict[str, Any],
    prefix: str,
    heading: str,
) -> None:
    st.subheader(heading)
    if not fields:
        st.info("本项目没有该部分填写项。")
        return
    with st.form(prefix):
        values: dict[str, Any] = {}
        for index, field in enumerate(fields):
            values[field[0]] = field_widget(
                field,
                target.get(field[0], initial_field(field)),
                f"{prefix}_{index}",
            )
        submitted = st.form_submit_button("保存本步骤", use_container_width=True)
    if submitted:
        target.update(values)
        st.success("已保存。")


if step.startswith("1"):
    render_form(
        COMMON_FIELDS,
        record["common"],
        f"common_{code}",
        "委托、样品、环境和人员信息",
    )

elif step.startswith("2"):
    render_form(
        conf.get("setup", []),
        record["setup"],
        f"setup_{code}",
        "设备、参数和使用前确认",
    )
    st.subheader("关键过程控制点")
    with st.form(f"checks_{code}"):
        values = {
            name: st.checkbox(
                name,
                value=bool(record["checks"].get(name, True)),
                key=f"check_{code}_{index}",
            )
            for index, name in enumerate(conf.get("checks", []))
        }
        submitted = st.form_submit_button("保存过程确认", use_container_width=True)
    if submitted:
        record["checks"].update(values)
        st.success("过程确认已保存。")

elif step.startswith("3"):
    st.subheader("逐个样品录入")
    st.caption("每次只加载一个样品，降低旧平板页面负担。")
    row_index = st.selectbox(
        "选择样品/试样",
        range(len(record["rows"])),
        format_func=lambda index: (
            f"{index + 1}｜{record['rows'][index].get('sample_id', '')}"
        ),
    )
    row = record["rows"][row_index]
    with st.form(f"row_{code}_{row_index}"):
        values = {
            field[0]: field_widget(
                field,
                row.get(field[0], initial_field(field)),
                f"row_{code}_{row_index}_{index}",
            )
            for index, field in enumerate(conf["row_fields"])
        }
        submitted = st.form_submit_button("保存该样品数据", use_container_width=True)
    if submitted:
        row.update(values)
        st.success(f"第{row_index + 1}个样品已保存。")

    completed = sum(
        any(
            value not in ("", 0, 0.0, None)
            for field_name, value in item.items()
            if field_name not in ("sample_id", "face")
        )
        for item in record["rows"]
    )
    ratio = completed / max(1, len(record["rows"]))
    st.progress(ratio)
    st.caption(f"已录入 {completed}/{len(record['rows'])} 个")

elif step.startswith("4"):
    if not conf.get("aux"):
        st.info("本项目没有单独的辅助数据表。")
    else:
        auxiliary_conf = conf["aux"]
        st.subheader(auxiliary_conf["name"])
        aux_index = st.selectbox(
            "选择记录点",
            range(len(record["aux"])),
            format_func=lambda index: (
                f"{index + 1}｜{record['aux'][index].get('_label', '')}"
            ),
        )
        item = record["aux"][aux_index]
        st.caption(item.get("_label", ""))
        with st.form(f"aux_{code}_{aux_index}"):
            values = {
                field[0]: field_widget(
                    field,
                    item.get(field[0], initial_field(field)),
                    f"aux_{code}_{aux_index}_{index}",
                )
                for index, field in enumerate(auxiliary_conf["fields"])
            }
            submitted = st.form_submit_button(
                "保存该辅助记录", use_container_width=True
            )
        if submitted:
            item.update(values)
            st.success("辅助记录已保存。")

elif step.startswith("5"):
    st.subheader("异常、偏离与处理")
    anomaly_index = st.selectbox(
        "异常记录序号",
        range(len(record["anomalies"])),
        format_func=lambda index: f"第{index + 1}条",
    )
    anomaly = record["anomalies"][anomaly_index]
    anomaly_fields = [
        ("time", "发生时间", "text", ""),
        ("sample", "涉及样品", "text", ""),
        ("description", "异常/偏离描述", "area", ""),
        ("impact", "影响评估", "text", ""),
        ("action", "处理措施及结果", "area", ""),
        ("responsible", "责任人", "text", ""),
        ("reviewer", "复核人", "text", ""),
    ]
    with st.form(f"anomaly_{code}_{anomaly_index}"):
        values = {
            field[0]: field_widget(
                field,
                anomaly.get(field[0], ""),
                f"anomaly_{code}_{anomaly_index}_{index}",
            )
            for index, field in enumerate(anomaly_fields)
        }
        submitted = st.form_submit_button("保存异常记录", use_container_width=True)
    if submitted:
        anomaly.update(values)
        st.success("异常记录已保存。")

    st.subheader("附件归档确认")
    with st.form(f"archives_{code}"):
        values = {
            name: st.checkbox(
                name,
                value=bool(record["archives"].get(name, False)),
                key=f"archive_{code}_{index}",
            )
            for index, name in enumerate(conf.get("archives", []))
        }
        submitted = st.form_submit_button("保存归档状态", use_container_width=True)
    if submitted:
        record["archives"].update(values)
        st.success("归档状态已保存。")

else:
    calculated_rows = calculate(code, record["rows"], record["setup"])
    overall = final_result(calculated_rows)

    st.subheader("结果汇总")
    st.metric("最终结果", overall)
    counts = {
        result_name: sum(
            row.get("result") == result_name for row in calculated_rows
        )
        for result_name in [
            "符合",
            "不符合",
            "仅记录",
            "需复测",
            "需复检",
            "需重制",
        ]
    }
    summary = "；".join(
        f"{name}：{count}" for name, count in counts.items() if count
    )
    if summary:
        st.write(summary)

    required = [
        ("record_no", "记录编号"),
        ("sample_name", "样品名称"),
        ("sample_no", "样品编号/批号"),
        ("operator", "检测人员"),
        ("reviewer", "复核人员"),
    ]
    missing = [
        label
        for field_name, label in required
        if not str(record["common"].get(field_name, "")).strip()
    ]
    unchecked = [
        name for name, checked in record["checks"].items() if not checked
    ]
    if missing:
        st.warning("尚未填写：" + "、".join(missing))
    if unchecked:
        st.warning("未确认控制点：" + "、".join(unchecked))

    draft = {"experiment": code, "record": record}
    draft_bytes = json.dumps(
        draft,
        ensure_ascii=False,
        indent=2,
    ).encode("utf-8")
    st.download_button(
        "下载JSON草稿",
        draft_bytes,
        file_name=f"{record['common'].get('record_no', 'record')}_{code}.json",
        mime="application/json",
        use_container_width=True,
    )

    try:
        document, _result = export_doc(
            code,
            conf,
            record["common"],
            record["setup"],
            record["checks"],
            calculated_rows,
            record["aux"],
            record["anomalies"],
            record["archives"],
        )
        st.download_button(
            "生成并下载CMA原始记录Word",
            document,
            file_name=(
                f"{record['common'].get('record_no', 'record')}_"
                f"{conf['name']}.docx"
            ),
            mime=(
                "application/vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            ),
            use_container_width=True,
        )
    except (FileNotFoundError, IndexError, KeyError, ValueError) as exc:
        st.error(f"Word生成失败：{exc}")

    if st.button("清空本项目，建立新记录", use_container_width=True):
        st.session_state[record_key] = make_new_record()
        st.rerun()

st.caption(
    "系统不添加Logo；Word输出以templates目录内CMA原始记录表为版式基础。"
    "免费云端不作为唯一长期存储，请下载Word与JSON草稿归档。"
)
