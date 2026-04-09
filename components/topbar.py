import streamlit as st

PAGES = [
    ("executive_summary",  "Executive Summary"),
    ("campus_breakdown",   "Campus Breakdown"),
    ("asset_explorer",     "Asset Explorer"),
    ("valuation_editor",   "Valuation Editor"),
    ("pending_valuation",  "Pending Valuation"),
    ("export_report",      "Export Report"),
]

VALUER_NAME = "Philip Barongo Ondieki"
REF = "JKUAT/VAL/2025/001"


def render_topbar():
    active = st.session_state.get("active_page", "executive_summary")

    nav_items = ""
    for key, label in PAGES:
        active_class = "active" if key == active else ""
        nav_items += f"""
        <div class="nav-item {active_class}" onclick="setPage('{key}')" id="nav-{key}">
            {label}
        </div>"""

    st.markdown(f"""
    <div class="topbar">
        <div class="brand">
            <div class="brand-monogram">AL</div>
            <div>
                <div class="brand-name">AssetLens</div>
                <div class="brand-sub">JKUAT · 2025</div>
            </div>
        </div>
        <nav class="topbar-nav">{nav_items}</nav>
        <div class="topbar-right">
            <span class="topbar-badge">{VALUER_NAME}</span>
            <span class="topbar-badge">{REF}</span>
        </div>
    </div>
    <script>
    function setPage(key) {{
        const inp = window.parent.document.querySelectorAll('input[data-testid="stTextInput"]');
        // Use Streamlit's component communication via query params
        const url = new URL(window.parent.location.href);
        url.searchParams.set('page', key);
        window.parent.history.replaceState(null, '', url);
        // Trigger via hidden button
        const btn = window.parent.document.getElementById('nav-trigger-' + key);
        if (btn) btn.click();
    }}
    </script>
    """, unsafe_allow_html=True)

    for key, label in PAGES:
        col_id = f"nav_btn_{key}"
        if st.sidebar.button(label, key=col_id, help=f"Go to {label}"):
            st.session_state["active_page"] = key
            st.rerun()
