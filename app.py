import streamlit as st
import pandas as pd
import numpy as np
from datetime import date, datetime
import os

st.set_page_config(
    page_title="JKUAT Asset Valuation Dashboard",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

from styles import inject_css, PALETTE
from data_loader import load_data, get_completeness
from charts import (
    asset_count_by_campus_stacked,
    asset_type_donut,
    top_buildings_by_fmv,
    fmv_treemap,
    campus_building_count_bar,
    campus_fmv_stacked_bar,
    condition_heatmap,
    fmv_boxplot,
    completeness_bar,
)
from export import export_to_excel, export_to_csv
from valuation_engine import apply_condition_multiplier, estimate_values

inject_css()

VALUER_NAME = "Philip Barongo Ondieki"
REF = "JKUAT/VAL/2025/001"
DATA_FILE = "asset_snippet_visualize.xlsx"

# ── Load / initialise session state ──
if "asset_df" not in st.session_state:
    df_loaded = load_data(DATA_FILE)
    if df_loaded.empty:
        st.session_state["asset_df"] = None
    else:
        st.session_state["asset_df"] = df_loaded

if "notes" not in st.session_state:
    st.session_state["notes"] = {}


def fmt_kes(v):
    try:
        return f"KES {v:,.0f}"
    except Exception:
        return "—"


def pct(v, t):
    return f"{(v / t * 100):.1f}%" if t > 0 else "0%"


def page_header(title: str, subtitle: str):
    ts = datetime.now().strftime("%d %b %Y, %H:%M")
    st.markdown(f"""
    <div class="page-header">
        <div class="page-title">{title}</div>
        <div class="page-subtitle">{subtitle}</div>
    </div>
    <div class="timestamp">Last refreshed: {ts}</div>
    """, unsafe_allow_html=True)


def kpi_card(label: str, value: str, delta: str = "", delta_class: str = "neutral"):
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {"<div class='kpi-delta " + delta_class + "'>" + delta + "</div>" if delta else ""}
    </div>
    """, unsafe_allow_html=True)


def sidebar_summary(df):
    total = len(df)
    fmv = df["FAIR MARKET VALUE"].sum()
    st.sidebar.markdown(f"""
    <div class="sidebar-summary">
        <div class="s-label">Assets Loaded</div>
        <div class="s-value">{total:,}</div>
        <div style="margin-top:8px" class="s-label">Total FMV</div>
        <div class="s-value" style="color:#C9A84C">{fmt_kes(fmv)}</div>
        <div style="margin-top:8px" class="s-label">Valuer</div>
        <div class="s-value" style="font-size:12px">{VALUER_NAME}</div>
        <div style="margin-top:4px" class="s-label">Ref</div>
        <div class="s-value" style="font-size:11px; color:#8899AA">{REF}</div>
    </div>
    """, unsafe_allow_html=True)


# ── Navigation ──
pages = [
    "📊  Executive Summary",
    "🏢  Campus & Building Breakdown",
    "🔍  Asset Inventory Explorer",
    "✏️   Valuation Entry & Editor",
    "📄  Valuation Report Export",
]

st.sidebar.markdown("""
<div style="padding:16px 0 10px 0;">
    <span class="jkuat-badge">JKUAT</span>
    <div style="font-family:'Playfair Display',serif; font-size:13px; color:#8899AA; margin-top:8px; letter-spacing:0.5px;">
        Asset Valuation Dashboard
    </div>
</div>
""", unsafe_allow_html=True)

page = st.sidebar.radio("Navigation", pages, label_visibility="collapsed")

df = st.session_state.get("asset_df")

if df is None or df.empty:
    st.markdown("""
    <div class="page-header">
        <div class="page-title">JKUAT Asset Valuation Dashboard</div>
        <div class="page-subtitle">Data file not found. Please upload the Excel file below.</div>
    </div>
    """, unsafe_allow_html=True)
    uploaded = st.file_uploader("Upload asset_snippet_visualize.xlsx", type=["xlsx"])
    if uploaded:
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
            tmp.write(uploaded.read())
            tmp_path = tmp.name
        st.session_state["asset_df"] = load_data(tmp_path)
        st.rerun()
    st.stop()

sidebar_summary(df)

# ══════════════════════════════════════════════
# PAGE 1 — EXECUTIVE SUMMARY
# ══════════════════════════════════════════════
if page == pages[0]:
    page_header(
        "JKUAT Asset Valuation Report — 2025",
        f"Prepared by: {VALUER_NAME}  |  Date: {date.today().strftime('%d %B %Y')}  |  Ref: {REF}"
    )

    total_assets = len(df)
    total_fmv = df["FAIR MARKET VALUE"].sum()
    total_reserve = df["RESERVE PRICE"].sum()
    fmv_reserve_gap = total_fmv - total_reserve
    pct_valued = len(df[(df["FAIR MARKET VALUE"] > 0) & (df["RESERVE PRICE"] > 0)]) / total_assets * 100
    pct_condition = len(df[df["CONDITION"].isin(["Good", "Fair", "Poor", "Condemned"])]) / total_assets * 100

    st.markdown('<div class="section-header">Key Performance Indicators</div>', unsafe_allow_html=True)
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        kpi_card("Total Assets", f"{total_assets:,}", "Across 4 Campuses", "neutral")
    with c2:
        kpi_card("Total Fair Market Value", fmt_kes(total_fmv), "", "neutral")
    with c3:
        kpi_card("Total Reserve Price", fmt_kes(total_reserve), "", "neutral")
    with c4:
        gap_class = "positive" if fmv_reserve_gap >= 0 else "negative"
        gap_label = "▲ Surplus" if fmv_reserve_gap >= 0 else "▼ Deficit"
        kpi_card("FMV vs Reserve Gap", fmt_kes(abs(fmv_reserve_gap)), gap_label, gap_class)
    with c5:
        kpi_card("Assets Fully Valued", f"{pct_valued:.1f}%",
                 f"{int(pct_valued*total_assets/100)}/{total_assets} assets", "positive" if pct_valued > 80 else "warning")
    with c6:
        kpi_card("Condition Recorded", f"{pct_condition:.1f}%",
                 f"{int(pct_condition*total_assets/100)}/{total_assets} assets", "positive" if pct_condition > 80 else "warning")

    st.markdown("---")
    st.markdown('<div class="section-header">Portfolio Overview</div>', unsafe_allow_html=True)

    col_a, col_b = st.columns([3, 2])
    with col_a:
        fig = asset_count_by_campus_stacked(df)
        st.plotly_chart(fig, use_container_width=True)
        top_campus = df.groupby("LOCATION").size().idxmax()
        top_count = df.groupby("LOCATION").size().max()
        st.markdown(f'<div class="chart-caption">📌 {top_campus} holds the largest inventory with {top_count} assets — {pct(top_count, total_assets)} of total portfolio.</div>', unsafe_allow_html=True)
    with col_b:
        fig2 = asset_type_donut(df)
        st.plotly_chart(fig2, use_container_width=True)
        top_type = df.groupby("ASSET TYPE").size().idxmax()
        top_type_count = df.groupby("ASSET TYPE").size().max()
        st.markdown(f'<div class="chart-caption">📌 {top_type} is the dominant asset category at {pct(top_type_count, total_assets)} of total inventory.</div>', unsafe_allow_html=True)

    st.markdown("---")
    col_c, col_d = st.columns([2, 3])
    with col_c:
        fig3 = top_buildings_by_fmv(df)
        st.plotly_chart(fig3, use_container_width=True)
        top_bldg = df.groupby("BUILDING")["FAIR MARKET VALUE"].sum().idxmax()
        top_bldg_fmv = df.groupby("BUILDING")["FAIR MARKET VALUE"].sum().max()
        st.markdown(f'<div class="chart-caption">📌 {top_bldg[:40]}... holds the highest FMV at {fmt_kes(top_bldg_fmv)}.</div>', unsafe_allow_html=True)
    with col_d:
        fig4 = fmv_treemap(df)
        st.plotly_chart(fig4, use_container_width=True)
        st.markdown('<div class="chart-caption">📌 Treemap shows FMV concentration across the 4-campus portfolio — larger blocks indicate higher asset value concentration.</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="section-header">Data Quality Panel</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Column-level completeness across the full asset register. Columns below 80% are flagged in red.</div>', unsafe_allow_html=True)

    completeness = get_completeness(df)
    fig5 = completeness_bar(completeness)
    st.plotly_chart(fig5, use_container_width=True)

    low = completeness[completeness["Completeness (%)"] < 80]
    if not low.empty:
        st.markdown(f'<div style="color:{PALETTE["danger"]}; font-size:13px; margin-top:-8px;">⚠️ {len(low)} column(s) below 80% completeness: <b>{", ".join(low["Column"].tolist())}</b></div>', unsafe_allow_html=True)

    st.dataframe(
        completeness.style.applymap(
            lambda v: f"color:{PALETTE['danger']}; font-weight:600" if isinstance(v, float) and v < 80 else "",
            subset=["Completeness (%)"]
        ),
        use_container_width=True,
        hide_index=True,
    )


# ══════════════════════════════════════════════
# PAGE 2 — CAMPUS & BUILDING BREAKDOWN
# ══════════════════════════════════════════════
elif page == pages[1]:
    page_header(
        "Campus & Building Breakdown",
        "Drill into asset distribution, FMV concentration, and condition profile per campus and building."
    )

    # Sidebar filters
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Filters**")
    all_campuses = sorted(df["LOCATION"].unique().tolist())
    sel_campus = st.sidebar.multiselect("Campus", all_campuses, default=all_campuses)

    all_types = sorted(df["ASSET TYPE"].unique().tolist())
    sel_types = st.sidebar.multiselect("Asset Type", all_types, default=all_types)

    all_conditions = ["Good", "Fair", "Poor", "Condemned"]
    sel_cond = st.sidebar.multiselect("Condition", all_conditions, default=all_conditions)

    buildings_for_campus = sorted(df[df["LOCATION"].isin(sel_campus)]["BUILDING"].unique().tolist())
    sel_buildings = st.sidebar.multiselect("Building", buildings_for_campus, default=buildings_for_campus)

    fdf = df[
        (df["LOCATION"].isin(sel_campus)) &
        (df["ASSET TYPE"].isin(sel_types)) &
        (df["CONDITION"].isin(sel_cond)) &
        (df["BUILDING"].isin(sel_buildings))
    ]

    for campus in sel_campus:
        cdf = fdf[fdf["LOCATION"] == campus]
        if cdf.empty:
            continue

        st.markdown(f'<div class="campus-banner"><h2>🏛 {campus}</h2></div>', unsafe_allow_html=True)

        total_c = len(cdf)
        fmv_c = cdf["FAIR MARKET VALUE"].sum()
        avg_fmv_c = cdf["FAIR MARKET VALUE"].mean()
        common_type = cdf["ASSET TYPE"].value_counts().idxmax() if total_c > 0 else "—"

        k1, k2, k3, k4 = st.columns(4)
        with k1:
            kpi_card("Total Assets", f"{total_c:,}")
        with k2:
            kpi_card("Total FMV", fmt_kes(fmv_c))
        with k3:
            kpi_card("Avg FMV / Asset", fmt_kes(avg_fmv_c))
        with k4:
            kpi_card("Dominant Asset Type", common_type[:28] if len(common_type) > 28 else common_type)

        ca, cb = st.columns(2)
        with ca:
            fig_a = campus_building_count_bar(cdf, campus)
            st.plotly_chart(fig_a, use_container_width=True)
            top_b = cdf.groupby("BUILDING").size().idxmax()
            top_bc = cdf.groupby("BUILDING").size().max()
            st.markdown(f'<div class="chart-caption">📌 {top_b[:50]} has the most assets ({top_bc}) in this campus.</div>', unsafe_allow_html=True)
        with cb:
            fig_b = campus_fmv_stacked_bar(cdf, campus)
            st.plotly_chart(fig_b, use_container_width=True)
            top_fmv_b = cdf.groupby("BUILDING")["FAIR MARKET VALUE"].sum().idxmax()
            top_fmv_v = cdf.groupby("BUILDING")["FAIR MARKET VALUE"].sum().max()
            st.markdown(f'<div class="chart-caption">📌 {top_fmv_b[:50]} leads in FMV with {fmt_kes(top_fmv_v)} across asset types.</div>', unsafe_allow_html=True)

        fig_c = condition_heatmap(cdf, campus)
        st.plotly_chart(fig_c, use_container_width=True)
        good_count = len(cdf[cdf["CONDITION"] == "Good"])
        st.markdown(f'<div class="chart-caption">📌 {pct(good_count, total_c)} of assets at {campus} are in Good condition ({good_count} assets).</div>', unsafe_allow_html=True)
        st.markdown("---")

    st.markdown('<div class="section-header">Portfolio Summary Table</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Grouped by Campus → Building → Asset Type. Sortable columns.</div>', unsafe_allow_html=True)

    summary_tbl = (
        fdf.groupby(["LOCATION", "BUILDING", "ASSET TYPE"])
        .agg(
            Count=("ASSET TAG", "count"),
            Total_FMV=("FAIR MARKET VALUE", "sum"),
            Avg_FMV=("FAIR MARKET VALUE", "mean"),
            Total_Reserve=("RESERVE PRICE", "sum"),
        )
        .reset_index()
    )
    summary_tbl["FMV/Reserve Ratio"] = (summary_tbl["Total_FMV"] / summary_tbl["Total_Reserve"]).round(2)
    summary_tbl.rename(columns={
        "LOCATION": "Campus", "BUILDING": "Building", "ASSET TYPE": "Asset Type",
        "Total_FMV": "Total FMV (KES)", "Avg_FMV": "Avg FMV (KES)", "Total_Reserve": "Total Reserve (KES)"
    }, inplace=True)

    st.dataframe(
        summary_tbl.style.background_gradient(
            subset=["Total FMV (KES)"],
            cmap="YlOrBr",
        ).format({
            "Total FMV (KES)": "KES {:,.0f}",
            "Avg FMV (KES)": "KES {:,.0f}",
            "Total Reserve (KES)": "KES {:,.0f}",
            "FMV/Reserve Ratio": "{:.2f}",
        }),
        use_container_width=True,
        hide_index=True,
    )


# ══════════════════════════════════════════════
# PAGE 3 — ASSET INVENTORY EXPLORER
# ══════════════════════════════════════════════
elif page == pages[2]:
    page_header(
        "Asset Inventory Explorer",
        "Search, filter, and inspect individual assets across all campuses. Click any row for full asset details."
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("**Filters**")
    all_campuses = sorted(df["LOCATION"].unique().tolist())
    sel_campus = st.sidebar.multiselect("Campus", all_campuses, default=all_campuses, key="inv_campus")
    all_types = sorted(df["ASSET TYPE"].unique().tolist())
    sel_types = st.sidebar.multiselect("Asset Type", all_types, default=all_types, key="inv_type")
    sel_cond = st.sidebar.multiselect("Condition", ["Good", "Fair", "Poor", "Condemned"],
                                       default=["Good", "Fair", "Poor", "Condemned"], key="inv_cond")
    buildings_for_campus = sorted(df[df["LOCATION"].isin(sel_campus)]["BUILDING"].unique().tolist())
    sel_buildings = st.sidebar.multiselect("Building", buildings_for_campus, default=buildings_for_campus, key="inv_bldg")

    floors = sorted([str(f) for f in df["FLOOR"].unique() if str(f) not in ["", "nan"]])
    if floors:
        sel_floors = st.sidebar.multiselect("Floor", floors, default=floors, key="inv_floor")
    else:
        sel_floors = []

    search = st.text_input("🔍  Search assets by tag, description, building, or department", placeholder="e.g. COHRED, CHAIR, JKUAT 46271")

    fdf = df[
        (df["LOCATION"].isin(sel_campus)) &
        (df["ASSET TYPE"].isin(sel_types)) &
        (df["CONDITION"].isin(sel_cond)) &
        (df["BUILDING"].isin(sel_buildings))
    ]

    if search:
        mask = (
            fdf["ASSET TAG"].str.upper().str.contains(search.upper(), na=False) |
            fdf["ASSET DESCRIPTION"].str.upper().str.contains(search.upper(), na=False) |
            fdf["BUILDING"].str.upper().str.contains(search.upper(), na=False) |
            fdf["DEPARTMENT"].str.upper().str.contains(search.upper(), na=False)
        )
        fdf = fdf[mask]

    display_cols = ["ASSET TAG", "ASSET DESCRIPTION", "ASSET TYPE", "LOCATION", "BUILDING",
                    "DEPARTMENT", "CONDITION", "RESERVE PRICE", "FAIR MARKET VALUE", "VALUATION_SOURCE"]
    fdf_display = fdf[display_cols].copy()
    fdf_display.rename(columns={
        "RESERVE PRICE": "Reserve (KES)",
        "FAIR MARKET VALUE": "FMV (KES)",
        "VALUATION_SOURCE": "Source",
    }, inplace=True)

    filtered_fmv = fdf["FAIR MARKET VALUE"].sum()
    st.markdown(f"""
    <div style="background:{PALETTE['bg_card']}; border-left:3px solid {PALETTE['accent']}; padding:10px 16px; margin-bottom:12px; font-size:13px;">
        Showing <b>{len(fdf):,} assets</b> &nbsp;|&nbsp; Total FMV: <b style="color:{PALETTE['accent']}">{fmt_kes(filtered_fmv)}</b>
        &nbsp;|&nbsp; Estimated: <b>{len(fdf[fdf['VALUATION_SOURCE']=='Estimated'])}</b>
        &nbsp;|&nbsp; Original: <b>{len(fdf[fdf['VALUATION_SOURCE']=='Original'])}</b>
    </div>
    """, unsafe_allow_html=True)

    def row_style(row):
        if row.get("Condition") == "Condemned":
            return [f"background-color: rgba(231,76,60,0.15)" for _ in row]
        elif row.get("Source") == "Estimated":
            return [f"background-color: rgba(243,156,18,0.08)" for _ in row]
        return [""] * len(row)

    st.dataframe(
        fdf_display,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Reserve (KES)": st.column_config.NumberColumn(format="KES %d"),
            "FMV (KES)": st.column_config.NumberColumn(format="KES %d"),
        }
    )

    st.markdown("---")
    st.markdown('<div class="section-header">Asset Detail Card</div>', unsafe_allow_html=True)

    asset_tags = fdf["ASSET TAG"].tolist()
    selected_tag = st.selectbox("Select Asset Tag to inspect", ["— Select —"] + asset_tags)

    if selected_tag != "— Select —":
        row = fdf[fdf["ASSET TAG"] == selected_tag].iloc[0]
        cond_color = {
            "Good": PALETTE["success"], "Fair": PALETTE["warning"],
            "Poor": PALETTE["danger"], "Condemned": "#8B0000"
        }.get(row["CONDITION"], PALETTE["text_muted"])

        st.markdown(f"""
        <div class="asset-card">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
                <span style="font-family:'Playfair Display',serif; font-size:18px; color:{PALETTE['accent']}">{row['ASSET TAG']}</span>
                <span style="background:{cond_color}22; border:1px solid {cond_color}; color:{cond_color}; padding:3px 12px; font-size:12px; font-weight:600; letter-spacing:0.5px">{row['CONDITION']}</span>
            </div>
            <div class="asset-card-field"><span class="asset-card-label">Description</span><br><span class="asset-card-value" style="font-size:15px">{row['ASSET DESCRIPTION']}</span></div>
            <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:12px; margin-top:12px;">
                <div class="asset-card-field"><span class="asset-card-label">Asset Type</span><br><span class="asset-card-value">{row['ASSET TYPE']}</span></div>
                <div class="asset-card-field"><span class="asset-card-label">Campus</span><br><span class="asset-card-value">{row['LOCATION']}</span></div>
                <div class="asset-card-field"><span class="asset-card-label">Building</span><br><span class="asset-card-value">{row['BUILDING'][:50]}</span></div>
                <div class="asset-card-field"><span class="asset-card-label">Department</span><br><span class="asset-card-value">{row.get('DEPARTMENT','—') or '—'}</span></div>
                <div class="asset-card-field"><span class="asset-card-label">Floor / Room</span><br><span class="asset-card-value">{row.get('FLOOR','—') or '—'} / {row.get('ROOM','—') or '—'}</span></div>
                <div class="asset-card-field"><span class="asset-card-label">Serial No.</span><br><span class="asset-card-value">{row.get('SERIAL NUMBER','—') or '—'}</span></div>
                <div class="asset-card-field"><span class="asset-card-label">Reserve Price</span><br><span class="asset-card-value" style="color:{PALETTE['text_primary']}">{fmt_kes(row['RESERVE PRICE'])}</span></div>
                <div class="asset-card-field"><span class="asset-card-label">Fair Market Value</span><br><span class="asset-card-value" style="color:{PALETTE['accent']}; font-size:17px; font-weight:700">{fmt_kes(row['FAIR MARKET VALUE'])}</span></div>
                <div class="asset-card-field"><span class="asset-card-label">Valuation Source</span><br><span class="asset-card-value">{row.get('VALUATION_SOURCE','—')}</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        note_key = row["ASSET TAG"]
        existing_note = st.session_state["notes"].get(note_key, "")
        note = st.text_area("📝 Valuation Notes", value=existing_note, height=80, key=f"note_{note_key}")
        if note != existing_note:
            st.session_state["notes"][note_key] = note
            st.success("Note saved.")

    st.markdown("---")
    st.markdown('<div class="section-header">Statistical Summary</div>', unsafe_allow_html=True)

    if len(fdf) > 0:
        fmv_vals = fdf["FAIR MARKET VALUE"].dropna()
        sc1, sc2, sc3, sc4 = st.columns(4)
        with sc1:
            kpi_card("Min FMV", fmt_kes(fmv_vals.min()))
        with sc2:
            kpi_card("Max FMV", fmt_kes(fmv_vals.max()))
        with sc3:
            kpi_card("Median FMV", fmt_kes(fmv_vals.median()))
        with sc4:
            kpi_card("Std Deviation", fmt_kes(fmv_vals.std()))

        fig_box = fmv_boxplot(fdf)
        st.plotly_chart(fig_box, use_container_width=True)
        st.markdown('<div class="chart-caption">📌 Box plot shows FMV spread per asset type — outliers indicate high-value items requiring individual verification.</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════
# PAGE 4 — VALUATION ENTRY & EDITOR
# ══════════════════════════════════════════════
elif page == pages[3]:
    page_header(
        "Valuation Entry & Data Editor",
        "Update Reserve Price, Fair Market Value, and Condition directly. Changes persist across all pages."
    )

    df_edit = st.session_state["asset_df"].copy()

    edit_cols = ["ASSET TAG", "ASSET DESCRIPTION", "ASSET TYPE", "BUILDING",
                 "CONDITION", "RESERVE PRICE", "FAIR MARKET VALUE"]
    df_editable = df_edit[edit_cols].copy()

    st.markdown('<div class="section-header">Editable Asset Register</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Asset Tag and Description are read-only. All other fields are editable.</div>', unsafe_allow_html=True)

    edited = st.data_editor(
        df_editable,
        use_container_width=True,
        hide_index=True,
        column_config={
            "ASSET TAG": st.column_config.TextColumn("Asset Tag", disabled=True),
            "ASSET DESCRIPTION": st.column_config.TextColumn("Description", disabled=True),
            "ASSET TYPE": st.column_config.TextColumn("Asset Type"),
            "BUILDING": st.column_config.TextColumn("Building"),
            "CONDITION": st.column_config.SelectboxColumn(
                "Condition",
                options=["Good", "Fair", "Poor", "Condemned"],
                required=True,
            ),
            "RESERVE PRICE": st.column_config.NumberColumn("Reserve Price (KES)", min_value=0, step=100, format="KES %d"),
            "FAIR MARKET VALUE": st.column_config.NumberColumn("Fair Market Value (KES)", min_value=0, step=100, format="KES %d"),
        },
        num_rows="fixed",
        key="data_editor_main",
    )

    c_recalc, c_save = st.columns([1, 1])

    with c_recalc:
        if st.button("⟳  Auto-Recalculate Condition Adjustments"):
            for idx, row in edited.iterrows():
                if df_edit.at[idx, "VALUATION_SOURCE"] == "Estimated":
                    base_fmv, base_reserve = estimate_values(
                        str(df_edit.at[idx, "ASSET DESCRIPTION"]),
                        str(row.get("ASSET TYPE", ""))
                    )
                    condition = str(row.get("CONDITION", "Good"))
                    new_fmv, new_reserve = apply_condition_multiplier(base_fmv, base_reserve, condition)
                    edited.at[idx, "FAIR MARKET VALUE"] = new_fmv
                    edited.at[idx, "RESERVE PRICE"] = new_reserve
            st.success("✅ Condition multipliers reapplied to all estimated assets.")

    # Merge edited cols back to full df
    for col in ["CONDITION", "RESERVE PRICE", "FAIR MARKET VALUE", "ASSET TYPE", "BUILDING"]:
        df_edit[col] = edited[col].values

    df_edit["FMV_RESERVE_RATIO"] = df_edit.apply(
        lambda r: round(r["FAIR MARKET VALUE"] / r["RESERVE PRICE"], 2)
        if r["RESERVE PRICE"] and r["RESERVE PRICE"] > 0 else 0.0, axis=1
    )

    with c_save:
        if st.button("💾  Save & Export to Excel"):
            st.session_state["asset_df"] = df_edit
            excel_bytes = export_to_excel(df_edit, VALUER_NAME)
            st.download_button(
                label="⬇️  Download JKUAT_Valuation_2025.xlsx",
                data=excel_bytes,
                file_name=f"JKUAT_Valuation_{date.today().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            st.success("✅ Dataset saved. Download link is ready above.")

    st.markdown("---")
    st.markdown('<div class="section-header">Live Valuation Preview</div>', unsafe_allow_html=True)

    prev = df_edit.groupby(["LOCATION", "BUILDING"]).agg(
        Count=("ASSET TAG", "count"),
        Total_FMV=("FAIR MARKET VALUE", "sum"),
        Total_Reserve=("RESERVE PRICE", "sum"),
    ).reset_index()
    prev.rename(columns={"LOCATION": "Campus", "BUILDING": "Building",
                          "Total_FMV": "Total FMV (KES)", "Total_Reserve": "Total Reserve (KES)"}, inplace=True)
    st.dataframe(
        prev.style.format({
            "Total FMV (KES)": "KES {:,.0f}",
            "Total Reserve (KES)": "KES {:,.0f}",
        }),
        use_container_width=True, hide_index=True,
    )


# ══════════════════════════════════════════════
# PAGE 5 — VALUATION REPORT EXPORT
# ══════════════════════════════════════════════
elif page == pages[4]:
    page_header(
        "Valuation Report Export",
        "Auto-generated professional valuation report. Download as Excel or CSV."
    )

    df_r = st.session_state["asset_df"]
    today_str = date.today().strftime("%d %B %Y")
    total_assets = len(df_r)
    total_fmv = df_r["FAIR MARKET VALUE"].sum()
    total_reserve = df_r["RESERVE PRICE"].sum()
    gap = total_fmv - total_reserve
    gap_word = "surplus" if gap >= 0 else "deficit"
    campuses_covered = ", ".join(sorted(df_r["LOCATION"].unique().tolist()))
    buildings_count = df_r["BUILDING"].nunique()

    # ── Report Header ──
    st.markdown(f"""
    <div class="report-block">
        <div style="display:flex; align-items:center; gap:16px; margin-bottom:16px;">
            <span class="jkuat-badge">🏛 JKUAT</span>
            <div>
                <div style="font-family:'Playfair Display',serif; font-size:20px; color:{PALETTE['text_primary']}; font-weight:700;">
                    ASSET VALUATION REPORT — 2025
                </div>
                <div style="color:{PALETTE['text_muted']}; font-size:12px; margin-top:3px;">
                    Jomo Kenyatta University of Agriculture and Technology
                </div>
            </div>
        </div>
        <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:10px; font-size:12px; color:{PALETTE['text_muted']};">
            <div><b style="color:{PALETTE['accent']}">Prepared by</b><br>{VALUER_NAME}</div>
            <div><b style="color:{PALETTE['accent']}">Date of Valuation</b><br>{today_str}</div>
            <div><b style="color:{PALETTE['accent']}">Reference No.</b><br>{REF}</div>
            <div style="margin-top:8px"><b style="color:{PALETTE['accent']}">Campuses Covered</b><br>Main Campus, Karen, Mombasa, Kitale</div>
            <div style="margin-top:8px"><b style="color:{PALETTE['accent']}">Buildings Covered</b><br>{buildings_count}</div>
            <div style="margin-top:8px"><b style="color:{PALETTE['accent']}">Standards</b><br>IVS 2022 | Kenya Valuers Act Cap 532</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Executive Narrative ──
    st.markdown('<div class="section-header">Executive Narrative</div>', unsafe_allow_html=True)
    estimated_count = len(df_r[df_r["VALUATION_SOURCE"] == "Estimated"])
    original_count = len(df_r[df_r["VALUATION_SOURCE"] == "Original"])

    narrative = f"""A total of **{total_assets:,} assets** were inventoried across **{campuses_covered}**. 
The aggregate **Fair Market Value** as at {today_str} is **KES {total_fmv:,.0f}**, against a 
**Reserve Price** of **KES {total_reserve:,.0f}**, representing a valuation **{gap_word} of KES {abs(gap):,.0f}**.

Of the {total_assets:,} assets, **{original_count}** carried independently verified values, while 
**{estimated_count}** were estimated using the approved Schedule of Rates for Kenyan market conditions (Q1 2025), 
adjusted for physical condition per RICS/IVS depreciation guidelines.

Assets were classified across **{df_r['ASSET TYPE'].nunique()} asset categories** spanning 
**{buildings_count} buildings**. The largest single concentration of value is in 
**{df_r.groupby('BUILDING')['FAIR MARKET VALUE'].sum().idxmax()}**, which accounts for 
**KES {df_r.groupby('BUILDING')['FAIR MARKET VALUE'].sum().max():,.0f}** of the total portfolio valuation."""

    st.markdown(f'<div class="report-block">{narrative.replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)

    st.markdown("---")
    col_rep1, col_rep2 = st.columns(2)

    with col_rep1:
        st.markdown('<div class="section-header" style="font-size:16px">Campus Summary</div>', unsafe_allow_html=True)
        campus_summary = df_r.groupby("LOCATION").agg(
            Buildings=("BUILDING", "nunique"),
            Assets=("ASSET TAG", "count"),
            Total_FMV=("FAIR MARKET VALUE", "sum"),
            Total_Reserve=("RESERVE PRICE", "sum"),
        ).reset_index()
        campus_summary.rename(columns={
            "LOCATION": "Campus", "Total_FMV": "Total FMV (KES)", "Total_Reserve": "Total Reserve (KES)"
        }, inplace=True)
        st.dataframe(
            campus_summary.style.format({
                "Total FMV (KES)": "KES {:,.0f}",
                "Total Reserve (KES)": "KES {:,.0f}",
            }),
            use_container_width=True, hide_index=True,
        )

        st.markdown('<div class="section-header" style="font-size:16px; margin-top:18px">Asset Type Breakdown</div>', unsafe_allow_html=True)
        type_summary = df_r.groupby("ASSET TYPE").agg(
            Count=("ASSET TAG", "count"),
            Total_FMV=("FAIR MARKET VALUE", "sum"),
        ).reset_index()
        type_summary["% of Portfolio"] = (type_summary["Count"] / total_assets * 100).round(1)
        type_summary.rename(columns={"ASSET TYPE": "Asset Type", "Total_FMV": "Total FMV (KES)"}, inplace=True)
        st.dataframe(
            type_summary.style.format({
                "Total FMV (KES)": "KES {:,.0f}",
                "% of Portfolio": "{:.1f}%",
            }),
            use_container_width=True, hide_index=True,
        )

    with col_rep2:
        st.markdown('<div class="section-header" style="font-size:16px">Condition Summary</div>', unsafe_allow_html=True)
        cond_summary = df_r.groupby("CONDITION").agg(
            Count=("ASSET TAG", "count"),
            Total_FMV=("FAIR MARKET VALUE", "sum"),
        ).reset_index()
        cond_summary["% of Total"] = (cond_summary["Count"] / total_assets * 100).round(1)
        cond_summary.rename(columns={"CONDITION": "Condition", "Total_FMV": "Total FMV (KES)"}, inplace=True)
        st.dataframe(
            cond_summary.style.format({
                "Total FMV (KES)": "KES {:,.0f}",
                "% of Total": "{:.1f}%",
            }),
            use_container_width=True, hide_index=True,
        )

        st.markdown('<div class="section-header" style="font-size:16px; margin-top:18px">Valuation Basis</div>', unsafe_allow_html=True)
        basis_df = pd.DataFrame({
            "Source": ["Original (Independently Verified)", "Estimated (Schedule of Rates)"],
            "Count": [original_count, estimated_count],
            "% of Total": [
                f"{original_count/total_assets*100:.1f}%",
                f"{estimated_count/total_assets*100:.1f}%"
            ],
            "Basis": [
                "Physical inspection / existing records",
                "JKUAT/VAL Schedule of Rates Q1 2025, condition-adjusted"
            ]
        })
        st.dataframe(basis_df, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown(f"""
    <div class="report-block">
        <h3>Valuer's Declaration</h3>
        <div style="font-size:13px; color:{PALETTE['text_muted']}; line-height:1.8;">
            I, <b style="color:{PALETTE['text_primary']}">{VALUER_NAME}</b>, a registered valuer practising in Kenya, 
            hereby declare that the valuations contained in this report have been carried out in accordance with 
            the <i>Kenya Valuers Act Cap 532</i> and the <i>International Valuation Standards (IVS) 2022</i>. 
            The values stated represent my professional opinion of the Fair Market Value and Reserve Price of the 
            listed assets as at <b style="color:{PALETTE['text_primary']}">{today_str}</b>. 
            I have no pecuniary interest in any of the properties valued, and this report is prepared for the 
            exclusive use of JKUAT management.
        </div>
        <div style="margin-top:24px; display:grid; grid-template-columns:1fr 1fr 1fr; gap:16px; font-size:12px;">
            <div>
                <div style="color:{PALETTE['text_muted']}">Signed</div>
                <div style="border-bottom:1px solid {PALETTE['border']}; height:28px; margin-top:6px; width:180px;"></div>
                <div style="color:{PALETTE['text_primary']}; margin-top:4px">{VALUER_NAME}</div>
            </div>
            <div>
                <div style="color:{PALETTE['text_muted']}">Date</div>
                <div style="border-bottom:1px solid {PALETTE['border']}; height:28px; margin-top:6px; width:120px;"></div>
                <div style="color:{PALETTE['text_primary']}; margin-top:4px">{today_str}</div>
            </div>
            <div>
                <div style="color:{PALETTE['text_muted']}">Reference</div>
                <div style="color:{PALETTE['text_primary']}; margin-top:10px; font-weight:600">{REF}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Export Buttons ──
    st.markdown('<div class="section-header">Export</div>', unsafe_allow_html=True)
    ex1, ex2 = st.columns(2)
    with ex1:
        excel_bytes = export_to_excel(df_r, VALUER_NAME)
        st.download_button(
            label="⬇️  Download Full Report (.xlsx)",
            data=excel_bytes,
            file_name=f"JKUAT_Asset_Valuation_Report_{date.today().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
    with ex2:
        csv_bytes = export_to_csv(df_r)
        st.download_button(
            label="⬇️  Download Flat Data Export (.csv)",
            data=csv_bytes,
            file_name=f"JKUAT_Assets_{date.today().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True,
        )
