import streamlit as st
import os

st.set_page_config(
    page_title="AssetLens — JKUAT",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from styles import inject_css
from data_loader import load_data

inject_css()

DATA_FILE = "PHILIP_JKUAT_ASSET_REGISTER.xlsx"

# ── Session state init ──
if "active_page" not in st.session_state:
    st.session_state["active_page"] = "executive_summary"

if "asset_df" not in st.session_state or "pending_df" not in st.session_state:
    if os.path.exists(DATA_FILE):
        asset_df, pending_df = load_data(DATA_FILE)
        st.session_state["asset_df"] = asset_df
        st.session_state["pending_df"] = pending_df
    else:
        st.session_state["asset_df"] = None
        st.session_state["pending_df"] = None

# ── Handle file upload if no data file ──
if st.session_state["asset_df"] is None:
    st.markdown("""
    <div class="page-header">
        <div class="page-title">AssetLens — JKUAT Asset Valuation Dashboard</div>
        <div class="page-subtitle">Upload the asset register Excel file to begin.</div>
    </div>
    """, unsafe_allow_html=True)
    uploaded = st.file_uploader("Upload asset_snippet_visualize.xlsx", type=["xlsx"])
    if uploaded:
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
            tmp.write(uploaded.read())
            tmp_path = tmp.name
        asset_df, pending_df = load_data(tmp_path)
        st.session_state["asset_df"] = asset_df
        st.session_state["pending_df"] = pending_df
        st.rerun()
    st.stop()

# ── Navigation via sidebar buttons (rendered as topbar via CSS) ──
from components.topbar import render_topbar, PAGES
render_topbar()

# ── Page dispatcher ──
active = st.session_state.get("active_page", "executive_summary")

page_map = {p[0]: p[0] for p in PAGES}

if active == "executive_summary":
    from pages.executive_summary import render
elif active == "campus_breakdown":
    from pages.campus_breakdown import render
elif active == "asset_explorer":
    from pages.asset_explorer import render
elif active == "valuation_editor":
    from pages.valuation_editor import render
elif active == "pending_valuation":
    from pages.pending_valuation import render
elif active == "export_report":
    from pages.export_report import render
else:
    from pages.executive_summary import render

render()
