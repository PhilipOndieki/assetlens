import streamlit as st

PALETTE = {
    "bg_primary": "#0D1B2A",
    "bg_secondary": "#1B2E45",
    "bg_card": "#162236",
    "accent": "#C9A84C",
    "accent_dim": "#9E7B30",
    "success": "#2ECC71",
    "warning": "#F39C12",
    "danger": "#E74C3C",
    "text_primary": "#F0F4F8",
    "text_muted": "#8899AA",
    "border": "#243550",
}

PLOTLY_TEMPLATE = {
    "layout": {
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {"color": PALETTE["text_primary"], "family": "DM Sans"},
        "title": {"font": {"color": PALETTE["accent"], "size": 16, "family": "Playfair Display"}},
        "xaxis": {
            "gridcolor": "rgba(201,168,76,0.15)",
            "linecolor": PALETTE["border"],
            "tickfont": {"color": PALETTE["text_muted"]},
            "title": {"font": {"color": PALETTE["text_muted"]}},
            "zerolinecolor": PALETTE["border"],
        },
        "yaxis": {
            "gridcolor": "rgba(201,168,76,0.15)",
            "linecolor": PALETTE["border"],
            "tickfont": {"color": PALETTE["text_muted"]},
            "title": {"font": {"color": PALETTE["text_muted"]}},
            "zerolinecolor": PALETTE["border"],
        },
        "legend": {
            "bgcolor": "rgba(22,34,54,0.8)",
            "bordercolor": PALETTE["border"],
            "borderwidth": 1,
            "font": {"color": PALETTE["text_primary"]},
            "orientation": "v",
            "xanchor": "right",
            "x": 1,
            "yanchor": "top",
            "y": 1,
        },
        "hoverlabel": {
            "bgcolor": PALETTE["bg_card"],
            "bordercolor": PALETTE["accent"],
            "font": {"color": PALETTE["text_primary"], "family": "DM Sans"},
        },
        "colorway": [
            "#C9A84C", "#2ECC71", "#3498DB", "#E74C3C",
            "#9B59B6", "#F39C12", "#1ABC9C", "#E67E22",
        ],
    }
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
    /* ── Root Variables ── */
    ... rest of CSS unchanged ...
    </style>""", unsafe_allow_html=True)
    st.markdown("""
                
        <style>
    /* ── Root Variables ── */
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

    /* ── Global ── */
    html, body, .stApp {
        background-color: var(--bg-primary) !important;
        font-family: 'DM Sans', sans-serif;
        color: var(--text-primary);
    }

    section[data-testid="stSidebar"] {
        background-color: #111F30 !important;
        border-right: 1px solid var(--border);
    }

    section[data-testid="stSidebar"] * {
        color: var(--text-primary) !important;
    }

    .block-container {
        padding: 1.5rem 2rem 3rem 2rem !important;
        max-width: 1400px !important;
    }

    /* ── Typography ── */
    h1, h2, h3 { font-family: 'Playfair Display', serif !important; }

    /* ── KPI Cards ── */
    .kpi-card {
        background: var(--bg-card);
        border-top: 3px solid var(--accent);
        border-radius: 2px;
        padding: 18px 20px 14px 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.35);
        height: 100%;
    }
    .kpi-label {
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        color: var(--text-muted);
        margin-bottom: 6px;
    }
    .kpi-value {
        font-family: 'DM Sans', sans-serif;
        font-size: 26px;
        font-weight: 700;
        color: var(--text-primary);
        line-height: 1.1;
    }
    .kpi-delta {
        font-size: 12px;
        color: var(--text-muted);
        margin-top: 4px;
    }
    .kpi-delta.positive { color: var(--success); }
    .kpi-delta.negative { color: var(--danger); }
    .kpi-delta.neutral  { color: var(--accent); }

    /* ── Section Headers ── */
    .section-header {
        font-family: 'Playfair Display', serif;
        font-size: 22px;
        font-weight: 600;
        color: var(--accent);
        letter-spacing: 0.8px;
        margin: 28px 0 6px 0;
        padding-bottom: 8px;
        border-bottom: 1px solid var(--border);
    }
    .section-subtitle {
        font-size: 13px;
        color: var(--text-muted);
        margin-bottom: 18px;
    }

    /* ── Page Header ── */
    .page-header {
        background: linear-gradient(135deg, #162236 0%, #1B2E45 100%);
        border-left: 4px solid var(--accent);
        border-radius: 2px;
        padding: 24px 28px;
        margin-bottom: 28px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.3);
    }
    .page-title {
        font-family: 'Playfair Display', serif;
        font-size: 28px;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0 0 6px 0;
    }
    .page-subtitle {
        font-size: 13px;
        color: var(--text-muted);
        margin: 0;
    }

    /* ── Report Header Badge ── */
    .jkuat-badge {
        display: inline-flex;
        align-items: center;
        gap: 10px;
        background: var(--accent);
        color: #0D1B2A;
        font-family: 'Playfair Display', serif;
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 1.5px;
        padding: 6px 14px;
        border-radius: 2px;
        text-transform: uppercase;
    }

    /* ── Insight Captions ── */
    .chart-caption {
        font-size: 12px;
        color: var(--text-muted);
        font-style: italic;
        margin-top: -8px;
        margin-bottom: 18px;
        padding-left: 2px;
    }

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
    .stButton > button:hover {
        background: var(--accent-dim) !important;
    }

    /* ── Divider ── */
    hr {
        border: none !important;
        border-top: 1px solid var(--border) !important;
        margin: 28px 0 !important;
    }

    /* ── Dataframe ── */
    .stDataFrame {
        border: 1px solid var(--border);
    }

    /* ── Selectbox / Multiselect ── */
    .stMultiSelect > div, .stSelectbox > div {
        background-color: var(--bg-secondary) !important;
        border: 1px solid var(--border) !important;
    }

    /* ── Text Input ── */
    .stTextInput > div > div > input {
        background-color: var(--bg-secondary) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border) !important;
        border-radius: 0 !important;
    }

    /* ── Metric overrides ── */
    [data-testid="metric-container"] {
        background: var(--bg-card);
        border-top: 3px solid var(--accent);
        padding: 16px;
    }

    /* ── Sidebar summary card ── */
    .sidebar-summary {
        background: #0D1B2A;
        border: 1px solid var(--border);
        border-left: 3px solid var(--accent);
        padding: 12px 14px;
        margin-bottom: 16px;
        font-size: 12px;
    }
    .sidebar-summary .s-label { color: var(--text-muted); font-size: 10px; letter-spacing: 1px; text-transform: uppercase; }
    .sidebar-summary .s-value { color: var(--text-primary); font-weight: 600; font-size: 14px; }

    /* ── Asset detail card ── */
    .asset-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-top: 3px solid var(--accent);
        padding: 20px;
        border-radius: 2px;
    }
    .asset-card-field { margin-bottom: 8px; font-size: 13px; }
    .asset-card-label { color: var(--text-muted); font-size: 11px; text-transform: uppercase; letter-spacing: 0.8px; }
    .asset-card-value { color: var(--text-primary); font-weight: 500; }

    /* ── Completeness table row highlighting ── */
    .low-completeness { color: var(--danger) !important; font-weight: 600; }

    /* ── Campus section banner ── */
    .campus-banner {
        background: linear-gradient(90deg, rgba(201,168,76,0.15) 0%, rgba(22,34,54,0) 100%);
        border-left: 4px solid var(--accent);
        padding: 12px 18px;
        margin: 24px 0 16px 0;
    }
    .campus-banner h2 {
        font-family: 'Playfair Display', serif;
        font-size: 20px;
        color: var(--accent);
        margin: 0;
    }

    /* ── Report export section ── */
    .report-block {
        background: var(--bg-card);
        border: 1px solid var(--border);
        padding: 24px;
        margin-bottom: 20px;
    }
    .report-block h3 {
        font-family: 'Playfair Display', serif;
        color: var(--accent);
        font-size: 16px;
        margin-top: 0;
        border-bottom: 1px solid var(--border);
        padding-bottom: 8px;
    }

    /* ── Timestamp ── */
    .timestamp {
        font-size: 11px;
        color: var(--text-muted);
        text-align: right;
        margin-top: -12px;
        margin-bottom: 10px;
    }

    /* ── Hide Streamlit chrome ── */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)
