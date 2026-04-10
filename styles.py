import streamlit as st

PALETTE = {
    "bg_primary":   "#0D1B2A",
    "bg_secondary": "#1B2E45",
    "bg_card":      "#162236",
    "accent":       "#C9A84C",
    "accent_dim":   "#9E7B30",
    "success":      "#2ECC71",
    "warning":      "#F39C12",
    "danger":       "#E74C3C",
    "text_primary": "#F0F4F8",
    "text_muted":   "#8899AA",
    "border":       "#243550",
}

CHART_COLORS = [
    "#C9A84C", "#2ECC71", "#3498DB", "#E74C3C",
    "#9B59B6", "#F39C12", "#1ABC9C", "#E67E22",
    "#27AE60", "#2980B9", "#8E44AD", "#D35400",
]


def inject_css():
    st.markdown(
        '<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=Playfair+Display:wght@400;600;700&display=swap" rel="stylesheet">',
        unsafe_allow_html=True,
    )
    st.markdown("""<style>

    :root {
        --bg-primary: #0D1B2A;
        --bg-secondary: #1B2E45;
        --bg-card: #162236;
        --accent: #C9A84C;
        --accent-dim: #9E7B30;
        --success: #2ECC71;
        --warning: #F39C12;
        --danger: #E74C3C;
        --text-primary: #F0F4F8;
        --text-muted: #8899AA;
        --border: #243550;
    }

    html, body, .stApp {
        background-color: var(--bg-primary) !important;
        font-family: 'DM Sans', sans-serif;
        color: var(--text-primary);
    }

    section[data-testid="stSidebar"] {
        background-color: #111F30 !important;
        border-right: 1px solid var(--border);
        width: 220px !important;
    }

    section[data-testid="stSidebar"] * {
        color: var(--text-primary) !important;
        font-size: 13px !important;
    }

    section[data-testid="stSidebar"] .stButton > button {
        width: 100%;
        text-align: left;
        background: transparent !important;
        color: var(--text-muted) !important;
        border: none !important;
        padding: 8px 12px !important;
        font-size: 13px !important;
        font-weight: 400 !important;
        text-transform: none !important;
        letter-spacing: 0 !important;
        border-radius: 4px !important;
    }

    section[data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(201,168,76,0.1) !important;
        color: var(--accent) !important;
    }

    .block-container {
        padding: 0 2rem 3rem 2rem !important;
        max-width: 1600px !important;
    }

    h1, h2, h3 { font-family: 'Playfair Display', serif !important; }

    /* ── Topbar ── */
    .topbar {
        background: var(--bg-card);
        border-bottom: 1px solid var(--border);
        padding: 0 2rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        height: 56px;
        margin: 0 -2rem 2.5rem -2rem;
        gap: 2rem;
        position: sticky;
        top: 0;
        z-index: 100;
    }

    .brand { display: flex; align-items: center; gap: 10px; }
    .brand-monogram {
        width: 30px; height: 30px;
        background: var(--accent);
        border-radius: 4px;
        display: flex; align-items: center; justify-content: center;
        font-size: 12px; font-weight: 700; color: #0D1B2A;
    }
    .brand-name { font-size: 14px; font-weight: 600; color: var(--text-primary); }
    .brand-sub { font-size: 11px; color: var(--text-muted); margin-top: 1px; }

    .topbar-nav { display: flex; align-items: center; gap: 0; flex: 1; justify-content: center; }
    .nav-item {
        padding: 0 18px; height: 56px;
        display: flex; align-items: center;
        font-size: 13px; color: var(--text-muted);
        cursor: pointer;
        border-bottom: 2px solid transparent;
        white-space: nowrap;
        transition: color 0.15s;
    }
    .nav-item:hover { color: var(--text-primary); }
    .nav-item.active { color: var(--accent); border-bottom-color: var(--accent); font-weight: 500; }

    .topbar-right { display: flex; align-items: center; gap: 8px; }
    .topbar-badge {
        background: var(--bg-secondary);
        border: 0.5px solid var(--border);
        border-radius: 4px;
        padding: 4px 10px;
        font-size: 11px;
        color: var(--text-muted);
        white-space: nowrap;
    }

    /* ── Page header ── */
    .page-header {
        background: linear-gradient(135deg, #162236 0%, #1B2E45 100%);
        border-left: 4px solid var(--accent);
        border-radius: 0;
        padding: 24px 28px;
        margin-bottom: 2.5rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.3);
    }
    .page-title {
        font-family: 'Playfair Display', serif;
        font-size: 28px; font-weight: 700;
        color: var(--text-primary); margin: 0 0 6px 0;
    }
    .page-subtitle { font-size: 13px; color: var(--text-muted); margin: 0; }
    .timestamp { font-size: 11px; color: var(--text-muted); text-align: right; margin-top: -12px; margin-bottom: 10px; }

    /* ── Section headers ── */
    .section-header {
        font-family: 'Playfair Display', serif;
        font-size: 22px; font-weight: 600;
        color: var(--accent);
        letter-spacing: 0.8px;
        margin: 2.5rem 0 6px 0;
        padding-bottom: 8px;
        border-bottom: 1px solid var(--border);
    }
    .section-subtitle { font-size: 13px; color: var(--text-muted); margin-bottom: 1.5rem; }

    /* ── KPI cards ── */
    .kpi-card {
        background: var(--bg-card);
        border-top: 3px solid var(--accent);
        border-radius: 2px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.35);
        height: 100%;
    }
    .kpi-label { font-size: 11px; font-weight: 600; letter-spacing: 1.2px; text-transform: uppercase; color: var(--text-muted); margin-bottom: 6px; }
    .kpi-value { font-family: 'DM Sans', sans-serif; font-size: 26px; font-weight: 700; color: var(--text-primary); line-height: 1.1; }
    .kpi-delta { font-size: 12px; color: var(--text-muted); margin-top: 4px; }
    .kpi-delta.positive { color: var(--success); }
    .kpi-delta.negative { color: var(--danger); }
    .kpi-delta.warning  { color: var(--warning); }
    .kpi-delta.neutral  { color: var(--accent); }

    /* ── Filter strip ── */
    .filter-strip {
        background: var(--bg-card);
        border: 1px solid var(--border);
        padding: 1rem 1.5rem;
        margin-bottom: 2rem;
    }

    /* ── Info strip ── */
    .info-strip {
        background: var(--bg-card);
        border-left: 3px solid var(--accent);
        padding: 10px 16px;
        margin-bottom: 1rem;
        font-size: 13px;
    }

    /* ── Pagination ── */
    .pagination-label { font-size: 12px; color: var(--text-muted); margin-bottom: 6px; }

    /* ── Chart caption ── */
    .chart-caption { font-size: 12px; color: var(--text-muted); font-style: italic; margin-top: -8px; margin-bottom: 1.5rem; padding-left: 2px; }

    /* ── Asset card ── */
    .asset-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-top: 3px solid var(--accent);
        padding: 1.5rem;
        border-radius: 2px;
        margin-bottom: 1rem;
    }
    .asset-card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; }
    .asset-tag-label { font-family: 'Playfair Display', serif; font-size: 18px; color: var(--accent); }
    .asset-card-desc { font-size: 15px; color: var(--text-primary); margin-bottom: 1rem; }
    .asset-card-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; }
    .acf { margin-bottom: 8px; font-size: 13px; }
    .acl { color: var(--text-muted); font-size: 11px; text-transform: uppercase; letter-spacing: 0.8px; display: block; }
    .acv { color: var(--text-primary); font-weight: 500; }

    /* ── Status badges ── */
    .status-badge {
        padding: 3px 10px; font-size: 11px; font-weight: 600;
        letter-spacing: 0.5px; border-radius: 2px;
    }
    .status-badge.danger { background: rgba(231,76,60,0.2); border: 1px solid #E74C3C; color: #E74C3C; }
    .status-badge.warning { background: rgba(243,156,18,0.2); border: 1px solid #F39C12; color: #F39C12; }
    .condition-badge { background: rgba(201,168,76,0.15); border: 1px solid var(--accent); color: var(--accent); padding: 3px 12px; font-size: 12px; font-weight: 600; letter-spacing: 0.5px; }

    /* ── Edit form ── */
    .edit-form { background: var(--bg-secondary); border: 1px solid var(--border); padding: 1.5rem; margin-top: 1rem; }

    /* ── Campus banner ── */
    .campus-banner { background: linear-gradient(90deg, rgba(201,168,76,0.15) 0%, rgba(22,34,54,0) 100%); border-left: 4px solid var(--accent); padding: 12px 18px; margin: 2.5rem 0 1.5rem 0; }
    .campus-banner h2 { font-family: 'Playfair Display', serif; font-size: 20px; color: var(--accent); margin: 0; }

    /* ── Report block ── */
    .report-block { background: var(--bg-card); border: 1px solid var(--border); padding: 1.5rem; margin-bottom: 1.5rem; }
    .report-block h3 { font-family: 'Playfair Display', serif; color: var(--accent); font-size: 16px; margin-top: 0; border-bottom: 1px solid var(--border); padding-bottom: 8px; }

    /* ── JKUAT badge ── */
    .jkuat-badge { display: inline-flex; align-items: center; gap: 10px; background: var(--accent); color: #0D1B2A; font-family: 'Playfair Display', serif; font-size: 13px; font-weight: 700; letter-spacing: 1.5px; padding: 6px 14px; border-radius: 2px; text-transform: uppercase; }

    /* ── Buttons ── */
    .stButton > button {
        background: var(--accent) !important;
        color: #0D1B2A !important;
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 700 !important;
        font-size: 13px !important;
        letter-spacing: 0.5px !important;
        border: none !important;
        border-radius: 0 !important;
        padding: 10px 24px !important;
        text-transform: uppercase !important;
    }
    .stButton > button:hover { background: var(--accent-dim) !important; }
    .stButton > button:disabled { background: var(--border) !important; color: var(--text-muted) !important; }
                
    /* ── Nav strip buttons — override global button style ── */
    div[data-testid="stHorizontalBlock"] .stButton > button {
        background: var(--bg-card) !important;
        color: var(--text-muted) !important;
        font-weight: 400 !important;
        text-transform: none !important;
        letter-spacing: 0 !important;
        border-bottom: 2px solid transparent !important;
        border-radius: 0 !important;
        padding: 0 18px !important;
        height: 56px !important;
        font-size: 13px !important;
        box-shadow: none !important;
    }
    div[data-testid="stHorizontalBlock"] .stButton > button:hover {
        background: var(--bg-card) !important;
        color: var(--text-primary) !important;
    }
                
    /* ── Divider ── */
    hr { border: none !important; border-top: 1px solid var(--border) !important; margin: 2.5rem 0 !important; }

    /* ── Dataframe ── */
    .stDataFrame { border: 1px solid var(--border); }

    /* ── Inputs ── */
    .stMultiSelect > div, .stSelectbox > div { background-color: var(--bg-secondary) !important; border: 1px solid var(--border) !important; }
    .stTextInput > div > div > input { background-color: var(--bg-secondary) !important; color: var(--text-primary) !important; border: 1px solid var(--border) !important; border-radius: 0 !important; }
    .stNumberInput > div > div > input { background-color: var(--bg-secondary) !important; color: var(--text-primary) !important; border: 1px solid var(--border) !important; border-radius: 0 !important; }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] { background: var(--bg-card); border-bottom: 1px solid var(--border); gap: 0; }
    .stTabs [data-baseweb="tab"] { background: transparent; color: var(--text-muted); font-size: 13px; padding: 10px 20px; border-bottom: 2px solid transparent; }
    .stTabs [aria-selected="true"] { color: var(--accent) !important; border-bottom-color: var(--accent) !important; }

    /* ── Hide chrome ── */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }
                

    </style>""", unsafe_allow_html=True)
