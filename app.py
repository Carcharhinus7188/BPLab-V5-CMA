import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="BPLab AI CMA",
    page_icon="🧪",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 企业信息
st.title("大连标普检测有限公司")
st.subheader("DALIAN BIAOPU TESTING CO., LTD.")
st.caption("CMA电子原始记录系统（轻量版）")

st.divider()

# 实验项目
projects = [
    "表面粗糙度试验",
    "翘曲变形试验",
    "弯曲性能试验",
    "X射线内部质量分析",
    "金瓷结合三点弯曲试验",
    "金瓷裂纹萌生试验",
    "热膨胀系数试验",
    "维氏硬度试验",
    "陶瓷牙耐急冷急热试验",
    "厚度测量",
    "色稳定性试验"
]

project = st.selectbox("检测项目 / Test Item", projects)

st.divider()

# 基础信息
st.subheader("样品信息 / Sample Information")

record_no = st.text_input(
    "记录编号 / Record No.",
    value=f"BP-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
)

sample_name = st.text_input("样品名称 / Sample Name")
sample_no = st.text_input("样品编号 / Sample ID")
operator = st.text_input("检测人员 / Operator")

st.divider()

# 项目数据
st.subheader("原始数据 / Raw Data")

if project == "翘曲变形试验":
    h1 = st.number_input("H1 (mm)", value=0.0, format="%.4f")
    h2 = st.number_input("H2 (mm)", value=0.0, format="%.4f")

    if st.button("计算 ΔH / Calculate"):
        delta = h1 - h2
        st.success(f"ΔH = {delta:.4f} mm")

elif project == "表面粗糙度试验":
    ra1 = st.number_input("Ra1 (μm)", value=0.0)
    ra2 = st.number_input("Ra2 (μm)", value=0.0)
    ra3 = st.number_input("Ra3 (μm)", value=0.0)

    if st.button("计算平均值 / Calculate Average"):
        avg = (ra1 + ra2 + ra3) / 3
        st.success(f"平均Ra = {avg:.4f} μm")

else:
    st.info("该项目页面框架已建立，后续加载对应CMA原始记录字段。")

st.divider()

col1, col2 = st.columns(2)

with col1:
    if st.button("保存记录 / Save"):
        st.success("记录已保存")

with col2:
    if st.button("生成原始记录 / Export"):
        st.success("原始记录生成接口已准备")
