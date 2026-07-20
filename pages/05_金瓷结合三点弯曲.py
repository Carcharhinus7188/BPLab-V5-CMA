import streamlit as st

st.title("金瓷结合三点弯曲试验")
st.info("CMA原始记录填写页面")

st.text_input("记录编号")
st.text_input("样品编号")
st.text_input("检测人员")

if st.button("保存"):
    st.success("已保存")
