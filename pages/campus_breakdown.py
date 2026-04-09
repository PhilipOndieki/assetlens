import streamlit as st
from components.kpi_card import kpi_card
from components.filter_strip import filter_strip
from charts.campus import building_asset_count, building_fmv, condition_heatmap
from styles import PALETTE


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

    st.markdown("""
    <div class="page-header">
        <div class="page-title">Campus & building breakdown</div>
        <div class="page-subtitle">Asset distribution, FMV concentration, and condition profile per campus and building.</div>
    </div>
    """, unsafe_allow_html=True)

    fdf = filter_strip(df, key_prefix="campus")

    if fdf.empty:
        st.info("No assets match the current filters.")
        return

    active_campuses = sorted(fdf["LOCATION"].dropna().unique().tolist())

    for campus in active_campuses:
        cdf = fdf[fdf["LOCATION"] == campus]
        if cdf.empty:
            continue

        total_c = len(cdf)
        fmv_c = cdf["FAIR MARKET VALUE"].sum()
        avg_fmv_c = cdf["FAIR MARKET VALUE"].mean()
        common_type = cdf["ASSET TYPE"].value_counts().idxmax() if total_c > 0 else "—"

        st.markdown(f'<div class="campus-banner"><h2>🏛 {campus}</h2></div>', unsafe_allow_html=True)

        k1, k2, k3, k4 = st.columns(4)
        with k1:
            kpi_card("Total assets", f"{total_c:,}")
        with k2:
            kpi_card("Total FMV", fmt_kes(fmv_c))
        with k3:
            kpi_card("Avg FMV / asset", fmt_kes(avg_fmv_c))
        with k4:
            label = common_type[:28] if len(str(common_type)) > 28 else common_type
            kpi_card("Dominant asset type", str(label))

        ca, cb = st.columns(2)
        with ca:
            fig_a = building_asset_count(cdf, campus)
            st.plotly_chart(fig_a, use_container_width=True)
            top_b = cdf.groupby("BUILDING").size().idxmax()
            top_bc = cdf.groupby("BUILDING").size().max()
            st.markdown(f'<div class="chart-caption">📌 {str(top_b)[:50]} has the most assets ({top_bc}) in this campus.</div>', unsafe_allow_html=True)
        with cb:
            fig_b = building_fmv(cdf, campus)
            st.plotly_chart(fig_b, use_container_width=True)
            top_fmv_b = cdf.groupby("BUILDING")["FAIR MARKET VALUE"].sum().idxmax()
            top_fmv_v = cdf.groupby("BUILDING")["FAIR MARKET VALUE"].sum().max()
            st.markdown(f'<div class="chart-caption">📌 {str(top_fmv_b)[:50]} leads in FMV with {fmt_kes(top_fmv_v)}.</div>', unsafe_allow_html=True)

        fig_c = condition_heatmap(cdf, campus)
        st.plotly_chart(fig_c, use_container_width=True)
        st.markdown("---")

    st.markdown('<div class="section-header">Portfolio summary table</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Grouped by campus → building → asset type.</div>', unsafe_allow_html=True)

    summary = (
        fdf.groupby(["LOCATION", "BUILDING", "ASSET TYPE"])
        .agg(Count=("ASSET TAG", "count"),
             Total_FMV=("FAIR MARKET VALUE", "sum"),
             Avg_FMV=("FAIR MARKET VALUE", "mean"),
             Total_Reserve=("RESERVE PRICE", "sum"))
        .reset_index()
    )
    summary["FMV/Reserve Ratio"] = (summary["Total_FMV"] / summary["Total_Reserve"]).round(2)
    summary.rename(columns={
        "LOCATION": "Campus", "BUILDING": "Building", "ASSET TYPE": "Asset Type",
        "Total_FMV": "Total FMV (KES)", "Avg_FMV": "Avg FMV (KES)",
        "Total_Reserve": "Total Reserve (KES)"
    }, inplace=True)

    st.dataframe(
        summary.style.background_gradient(subset=["Total FMV (KES)"], cmap="YlOrBr")
        .format({"Total FMV (KES)": "KES {:,.0f}", "Avg FMV (KES)": "KES {:,.0f}",
                 "Total Reserve (KES)": "KES {:,.0f}", "FMV/Reserve Ratio": "{:.2f}"}),
        use_container_width=True, hide_index=True,
    )
