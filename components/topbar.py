import streamlit as st

PAGES = [
    ("executive_summary",  "Executive Summary"),
    ("campus_breakdown",   "Campus Breakdown"),
    ("asset_explorer",     "Asset Explorer"),
    ("valuation_editor",   "Valuation Editor"),
    ("pending_valuation",  "Pending Valuation"),
    ("export_report",      "Export Report"),
]

VALUER_NAME = "Kenval realtors"
REF = "JKUAT/VAL/2025/001"

def render_topbar():
    active = st.session_state.get("active_page", "executive_summary")

    # Static brand + badge bar (purely visual)
    st.markdown(f"""
    <div class="topbar">
        <div class="brand">
            <div class="brand-monogram">AL</div>
            <div>
                <div class="brand-name">AssetLens</div>
                <div class="brand-sub">JKUAT · 2025</div>
            </div>
        </div>
        <div class="topbar-right">
            <span class="topbar-badge">{VALUER_NAME}</span>
            <span class="topbar-badge">{REF}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Functional nav buttons rendered as a horizontal strip below the brand bar
    cols = st.columns(len(PAGES))
    for col, (key, label) in zip(cols, PAGES):
        with col:
            is_active = key == active
            # Highlight active page via button label prefix
            btn_label = f"▸ {label}" if is_active else label
            if st.button(btn_label, key=f"nav_btn_{key}", use_container_width=True):
                st.session_state["active_page"] = key
                st.rerun()