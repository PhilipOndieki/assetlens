import streamlit as st
from datetime import date, datetime
from components.kpi_card import kpi_card
from components.filter_strip import filter_strip
from charts.portfolio import asset_count_by_campus, asset_type_donut, top_buildings_by_fmv, fmv_treemap
from charts.distribution import completeness_bar, fmv_boxplot
from data_loader import get_completeness
from styles import PALETTE

VALUER_NAME = "Kenval realtors"
REF = "JKUAT/VAL/2025/001"


def fmt_kes(v):
    try:
        return f"KES {v:,.0f}"
    except Exception:
        return "—"


def pct(v, t):
    return f"{(v / t * 100):.1f}%" if t > 0 else "0%"


def render():
    df = st.session_state.get("asset_df")
    if df is None or df.empty:
        st.warning("No data loaded.")
        return

    ts = datetime.now().strftime("%d %b %Y, %H:%M")
    st.markdown(f"""
    <div class="page-header">
        <div class="page-title">JKUAT Asset Valuation Report — 2025</div>
        <div class="page-subtitle">
            Prepared by: {VALUER_NAME} &nbsp;|&nbsp;
            Date: {date.today().strftime('%d %B %Y')} &nbsp;|&nbsp;
            Ref: {REF}
        </div>
    </div>
    <div class="timestamp">Last refreshed: {ts}</div>
    """, unsafe_allow_html=True)

    fdf = filter_strip(df, key_prefix="exec")

    total = len(fdf)
    if total == 0:
        st.info("No assets match the current filters.")
        return

    total_fmv = fdf["FAIR MARKET VALUE"].sum()
    total_reserve = fdf["RESERVE PRICE"].sum()
    gap = total_fmv - total_reserve
    gap_class = "positive" if gap >= 0 else "negative"
    gap_label = f"{'▲ Surplus' if gap >= 0 else '▼ Deficit'}"
    missing_count = fdf["IS_MISSING"].sum()
    untagged_count = fdf["IS_UNTAGGED"].sum()

    st.markdown('<div class="section-header">Key performance indicators</div>', unsafe_allow_html=True)
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        kpi_card("Total assets", f"{total:,}", f"Across {fdf['LOCATION'].nunique()} campuses")
    with c2:
        kpi_card("Fair market value", fmt_kes(total_fmv))
    with c3:
        kpi_card("Reserve price", fmt_kes(total_reserve))
    with c4:
        kpi_card("FMV vs reserve gap", fmt_kes(abs(gap)), gap_label, gap_class)
    with c5:
        kpi_card("Missing assets", f"{missing_count:,}", "Flagged by valuers",
                 "negative" if missing_count > 0 else "positive")
    with c6:
        kpi_card("Untagged assets", f"{untagged_count:,}", "Awaiting tagging",
                 "warning" if untagged_count > 0 else "positive")

    st.markdown("---")
    st.markdown('<div class="section-header">Portfolio overview</div>', unsafe_allow_html=True)

    col_a, col_b = st.columns([3, 2])
    with col_a:
        grp_campus = fdf.groupby("LOCATION").size()
        fig1 = asset_count_by_campus(fdf)
        st.plotly_chart(fig1, width='stretch')
        top_campus = grp_campus.idxmax()
        st.markdown(f'<div class="chart-caption">📌 {top_campus} holds the largest inventory — {grp_campus.max():,} assets ({pct(grp_campus.max(), total)} of portfolio).</div>', unsafe_allow_html=True)
    with col_b:
        grp_type = fdf.groupby("ASSET TYPE").size()
        fig2 = asset_type_donut(fdf)
        st.plotly_chart(fig2, width='stretch')
        top_type = grp_type.idxmax()
        st.markdown(f'<div class="chart-caption">📌 {top_type} is the dominant category at {pct(grp_type.max(), total)} of total inventory.</div>', unsafe_allow_html=True)

    st.markdown("---")
    col_c, col_d = st.columns([2, 3])
    with col_c:
        grp_bldg = fdf.groupby("BUILDING")["FAIR MARKET VALUE"].sum()
        fig3 = top_buildings_by_fmv(fdf)
        st.plotly_chart(fig3, width='stretch')
        top_bldg = grp_bldg.idxmax()
        st.markdown(f'<div class="chart-caption">📌 {str(top_bldg)[:50]} holds the highest FMV at {fmt_kes(grp_bldg.max())}.</div>', unsafe_allow_html=True)
    with col_d:
        fig4 = fmv_treemap(fdf)
        st.plotly_chart(fig4, width='stretch')
        st.markdown('<div class="chart-caption">📌 Treemap shows FMV concentration across the portfolio — larger blocks indicate higher value concentration.</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="section-header">Data quality</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Column-level completeness. Columns below 80% are flagged in red.</div>', unsafe_allow_html=True)

    completeness = get_completeness(fdf)
    fig5 = completeness_bar(completeness)
    st.plotly_chart(fig5, width='stretch')

    low = completeness[completeness["Completeness (%)"] < 80]
    if not low.empty:
        cols_list = ", ".join(low["Column"].tolist())
        st.markdown(f'<div style="color:{PALETTE["danger"]}; font-size:13px;">⚠️ {len(low)} column(s) below 80%: <b>{cols_list}</b></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="section-header">FMV distribution</div>', unsafe_allow_html=True)
    fig6 = fmv_boxplot(fdf)
    st.plotly_chart(fig6, width='stretch')
    st.markdown('<div class="chart-caption">📌 Box plot shows FMV spread per asset type — outliers indicate high-value items requiring individual verification.</div>', unsafe_allow_html=True)
