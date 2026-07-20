
import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="BPLab AI CMA",
    page_icon="🧪",
    layout="centered"
)

st.title("大连标普检测有限公司")
st.subheader("DALIAN BIAOPU TESTING CO., LTD.")
st.caption("CMA电子原始记录系统（轻量版）")

# 检测项目
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

project = st.selectbox("检测项目", projects)

st.divider()

st.subheader("样品基本信息")

record_no = st.text_input(
    "记录编号",
    value=f"BP-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
)

sample_name = st.text_input("样品名称")
sample_no = st.text_input("样品编号")
operator = st.text_input("检测人员")

st.subheader("检测数据")

if project == "翘曲变形试验":
    h1 = st.number_input("H1/mm", value=0.0)
    h2 = st.number_input("H2/mm", value=0.0)

    if st.button("计算"):
        delta = h1 - h2
        st.success(f"ΔH = {delta:.4f} mm")

else:
    st.info("当前项目已建立入口，具体CMA字段将在对应实验页面中填写。")

st.divider()

if st.button("保存记录"):
    st.success("记录已保存（测试模式）")

if st.button("生成原始记录"):
    st.success("原始记录生成接口已连接")
