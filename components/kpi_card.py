import streamlit as st
from styles import PALETTE


def kpi_card(label: str, value: str, delta: str = "", delta_class: str = "neutral"):
    delta_html = ""
    if delta:
        delta_html = f"<div class='kpi-delta {delta_class}'>{delta}</div>"
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)
