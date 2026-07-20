
import streamlit as st
from core.calculation import warp_delta

st.header("02 翘曲变形试验")

h1=st.number_input("H1/mm")
h2=st.number_input("H2/mm")

if st.button("计算"):
    st.success(f"ΔH={warp_delta(h1,h2):.3f} mm")
