
import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="BPLab CMA原始记录系统",
    page_icon="🧪",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Android 14 原装浏览器强制亮色 + 轻量优化
st.markdown("""
<style>
:root {
    color-scheme: light !important;
}

html, body {
    background:#ffffff !important;
    color:#222222 !important;
}

.stApp {
    background:#ffffff !important;
}

[data-testid="stAppViewContainer"] {
    background:#ffffff !important;
}

[data-testid="stHeader"] {
    background:#ffffff !important;
}

[data-testid="stToolbar"] {
    display:none !important;
}

section[data-testid="stSidebar"] {
    display:none !important;
}

input, textarea, button, select {
    color-scheme:light !important;
    background:#ffffff !important;
    color:#222222 !important;
    font-size:16px !important;
}

.stButton button {
    min-height:48px !important;
    width:100% !important;
}

.block-container {
    max-width:720px !important;
    padding-top:1rem !important;
}
</style>
""", unsafe_allow_html=True)

st.title("大连标普检测有限公司")
st.caption("DALIAN BIAOPU TESTING CO., LTD.")
st.subheader("BPLab CMA电子原始记录系统")

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

st.subheader("基本信息")

st.text_input("记录编号", value=f"BP-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
st.text_input("样品名称")
st.text_input("样品编号")
st.text_input("检测人员")

st.divider()

st.info(f"当前项目：{project}")

if project == "翘曲变形试验":
    st.subheader("原始数据")
    h1 = st.number_input("H1/mm", min_value=0.0)
    h2 = st.number_input("H2/mm", min_value=0.0)

    if st.button("计算"):
        st.success(f"ΔH={h1-h2:.4f} mm")

else:
    st.write("该实验页面已建立，等待对应CMA原始记录字段加载。")

if st.button("保存记录"):
    st.success("记录保存接口正常")

if st.button("生成CMA原始记录"):
    st.success("Word原始记录输出接口正常")
