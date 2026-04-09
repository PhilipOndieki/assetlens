import streamlit as st
import pandas as pd
from datetime import date
from export import export_to_excel, export_pending_excel
from styles import PALETTE

VALUER_NAME = "Philip Barongo Ondieki"
REF = "JKUAT/VAL/2025/001"


def fmt_kes(v):
    try:
        return f"KES {v:,.0f}"
    except Exception:
        return "—"


def render():
    df = st.session_state.get("asset_df")
    pending_df = st.session_state.get("pending_df", pd.DataFrame())

    if df is None or df.empty:
        st.warning("No data loaded.")
        return

    today_str = date.today().strftime("%d %B %Y")
    total_assets = len(df)
    total_fmv = df["FAIR MARKET VALUE"].sum()
    total_reserve = df["RESERVE PRICE"].sum()
    gap = total_fmv - total_reserve
    gap_word = "surplus" if gap >= 0 else "deficit"
    buildings_count = df["BUILDING"].nunique()
    missing_count = df["IS_MISSING"].sum()

    st.markdown(f"""
    <div class="page-header">
        <div class="page-title">Valuation report export</div>
        <div class="page-subtitle">Auto-generated professional valuation report. Download as Excel with 5 sheets.</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="report-block">
        <div style="display:flex;align-items:center;gap:16px;margin-bottom:16px;">
            <span class="jkuat-badge">🏛 JKUAT</span>
            <div>
                <div style="font-family:'Playfair Display',serif;font-size:20px;color:{PALETTE['text_primary']};font-weight:700;">
                    ASSET VALUATION REPORT — 2025
                </div>
                <div style="color:{PALETTE['text_muted']};font-size:12px;margin-top:3px;">
                    Jomo Kenyatta University of Agriculture and Technology
                </div>
            </div>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;font-size:12px;color:{PALETTE['text_muted']};">
            <div><b style="color:{PALETTE['accent']}">Prepared by</b><br>{VALUER_NAME}</div>
            <div><b style="color:{PALETTE['accent']}">Date of valuation</b><br>{today_str}</div>
            <div><b style="color:{PALETTE['accent']}">Reference no.</b><br>{REF}</div>
            <div style="margin-top:8px"><b style="color:{PALETTE['accent']}">Campuses covered</b><br>{', '.join(sorted(df['LOCATION'].unique().tolist()))}</div>
            <div style="margin-top:8px"><b style="color:{PALETTE['accent']}">Buildings covered</b><br>{buildings_count}</div>
            <div style="margin-top:8px"><b style="color:{PALETTE['accent']}">Standards</b><br>IVS 2022 · Kenya Valuers Act Cap 532</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-header">Executive narrative</div>', unsafe_allow_html=True)

    top_bldg = df.groupby("BUILDING")["FAIR MARKET VALUE"].sum().idxmax()
    top_bldg_fmv = df.groupby("BUILDING")["FAIR MARKET VALUE"].sum().max()

    narrative = f"""A total of **{total_assets:,} assets** were inventoried and valued across 
**{df['LOCATION'].nunique()} campuses** spanning **{buildings_count} buildings**. The aggregate 
**Fair Market Value** as at {today_str} is **KES {total_fmv:,.0f}**, against a 
**Reserve Price** of **KES {total_reserve:,.0f}**, representing a valuation 
**{gap_word} of KES {abs(gap):,.0f}**.

All {total_assets:,} assets carry independently verified Fair Market Values and Reserve Prices 
sourced directly from the asset register. An additional **{len(pending_df)} assets** remain 
pending valuation and are excluded from the totals above. **{missing_count} assets** have been 
flagged as missing during physical inspection.

The largest single concentration of value is in **{str(top_bldg)[:80]}**, which accounts for 
**KES {top_bldg_fmv:,.0f}** of the total portfolio valuation."""

    st.markdown(f'<div class="report-block">{narrative.replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-header" style="font-size:16px">Campus summary</div>', unsafe_allow_html=True)
        campus_summary = df.groupby("LOCATION").agg(
            Buildings=("BUILDING", "nunique"),
            Assets=("ASSET TAG", "count"),
            Total_FMV=("FAIR MARKET VALUE", "sum"),
            Total_Reserve=("RESERVE PRICE", "sum"),
        ).reset_index()
        campus_summary.rename(columns={"LOCATION": "Campus",
                                        "Total_FMV": "Total FMV (KES)",
                                        "Total_Reserve": "Total Reserve (KES)"}, inplace=True)
        st.dataframe(
            campus_summary.style.format({"Total FMV (KES)": "KES {:,.0f}", "Total Reserve (KES)": "KES {:,.0f}"}),
            use_container_width=True, hide_index=True,
        )

        st.markdown('<div class="section-header" style="font-size:16px;margin-top:18px">Asset type breakdown</div>', unsafe_allow_html=True)
        type_summary = df.groupby("ASSET TYPE").agg(
            Count=("ASSET TAG", "count"),
            Total_FMV=("FAIR MARKET VALUE", "sum"),
        ).reset_index()
        type_summary["% of Portfolio"] = (type_summary["Count"] / total_assets * 100).round(1)
        type_summary.rename(columns={"ASSET TYPE": "Asset Type", "Total_FMV": "Total FMV (KES)"}, inplace=True)
        st.dataframe(
            type_summary.style.format({"Total FMV (KES)": "KES {:,.0f}", "% of Portfolio": "{:.1f}%"}),
            use_container_width=True, hide_index=True,
        )

    with col2:
        st.markdown('<div class="section-header" style="font-size:16px">Condition summary</div>', unsafe_allow_html=True)
        cond_summary = df.groupby("CONDITION").agg(
            Count=("ASSET TAG", "count"),
            Total_FMV=("FAIR MARKET VALUE", "sum"),
        ).reset_index()
        cond_summary["% of Total"] = (cond_summary["Count"] / total_assets * 100).round(1)
        cond_summary.rename(columns={"CONDITION": "Condition", "Total_FMV": "Total FMV (KES)"}, inplace=True)
        st.dataframe(
            cond_summary.style.format({"Total FMV (KES)": "KES {:,.0f}", "% of Total": "{:.1f}%"}),
            use_container_width=True, hide_index=True,
        )

        st.markdown('<div class="section-header" style="font-size:16px;margin-top:18px">Missing & untagged</div>', unsafe_allow_html=True)
        status_df = pd.DataFrame({
            "Status": ["Fully tagged & present", "Missing (flagged)", "Untagged"],
            "Count": [
                total_assets - missing_count - int(df["IS_UNTAGGED"].sum()),
                missing_count,
                int(df["IS_UNTAGGED"].sum()),
            ]
        })
        st.dataframe(status_df, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown(f"""
    <div class="report-block">
        <h3>Valuer's declaration</h3>
        <div style="font-size:13px;color:{PALETTE['text_muted']};line-height:1.8;">
            I, <b style="color:{PALETTE['text_primary']}">{VALUER_NAME}</b>, a registered valuer
            practising in Kenya, hereby declare that the valuations contained in this report have
            been carried out in accordance with the <i>Kenya Valuers Act Cap 532</i> and the
            <i>International Valuation Standards (IVS) 2022</i>. The values stated represent my
            professional opinion of the Fair Market Value and Reserve Price of the listed assets
            as at <b style="color:{PALETTE['text_primary']}">{today_str}</b>.
        </div>
        <div style="margin-top:24px;display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;font-size:12px;">
            <div>
                <div style="color:{PALETTE['text_muted']}">Signed</div>
                <div style="border-bottom:1px solid {PALETTE['border']};height:28px;margin-top:6px;width:180px;"></div>
                <div style="color:{PALETTE['text_primary']};margin-top:4px">{VALUER_NAME}</div>
            </div>
            <div>
                <div style="color:{PALETTE['text_muted']}">Date</div>
                <div style="border-bottom:1px solid {PALETTE['border']};height:28px;margin-top:6px;width:120px;"></div>
                <div style="color:{PALETTE['text_primary']};margin-top:4px">{today_str}</div>
            </div>
            <div>
                <div style="color:{PALETTE['text_muted']}">Reference</div>
                <div style="color:{PALETTE['text_primary']};margin-top:10px;font-weight:600">{REF}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-header">Download</div>', unsafe_allow_html=True)
    ex1, ex2 = st.columns(2)
    with ex1:
        with st.spinner("Building Excel report..."):
            excel_bytes = export_to_excel(df, pending_df, VALUER_NAME)
        st.download_button(
            label="Download full report (.xlsx) — 5 sheets",
            data=excel_bytes,
            file_name=f"JKUAT_Asset_Valuation_Report_{date.today().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
    with ex2:
        csv_bytes = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download flat CSV (.csv)",
            data=csv_bytes,
            file_name=f"JKUAT_Assets_{date.today().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True,
        )
