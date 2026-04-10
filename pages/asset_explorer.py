import streamlit as st
from components.kpi_card import kpi_card
from components.filter_strip import filter_strip
from components.asset_card import asset_card
from styles import PALETTE


def fmt_kes(v):
    try:
        return f"KES {v:,.0f}"
    except Exception:
        return "—"


def render():
    df = st.session_state.get("asset_df")
    if df is None or df.empty:
        st.warning("No data loaded.")
        return

    st.markdown("""
    <div class="page-header">
        <div class="page-title">Asset inventory explorer</div>
        <div class="page-subtitle">Search, filter, and inspect individual assets. Flag missing items and assign tags to untagged assets.</div>
    </div>
    """, unsafe_allow_html=True)

    fdf = filter_strip(df, key_prefix="explorer")

    search = st.text_input(
        "Search assets",
        placeholder="Tag number, description, building, department...",
        key="explorer_search"
    )

    if search:
        s = search.upper()
        mask = (
            fdf["ASSET TAG"].fillna("").str.upper().str.contains(s, na=False) |
            fdf["ASSET DESCRIPTION"].fillna("").str.upper().str.contains(s, na=False) |
            fdf["BUILDING"].fillna("").str.upper().str.contains(s, na=False) |
            fdf["DEPARTMENT"].fillna("").str.upper().str.contains(s, na=False)
        )
        fdf = fdf[mask]

    total_filtered = len(fdf)
    filtered_fmv = fdf["FAIR MARKET VALUE"].sum()
    missing_count = fdf["IS_MISSING"].sum()
    untagged_count = fdf["IS_UNTAGGED"].sum()

    st.markdown(f"""
    <div class="info-strip">
        Showing <b>{total_filtered:,} assets</b>
        &nbsp;|&nbsp; Total FMV: <b style="color:{PALETTE['accent']}">{fmt_kes(filtered_fmv)}</b>
        &nbsp;|&nbsp; Missing: <b style="color:{PALETTE['danger']}">{missing_count}</b>
        &nbsp;|&nbsp; Untagged: <b style="color:{PALETTE['warning']}">{untagged_count}</b>
    </div>
    """, unsafe_allow_html=True)

    PAGE_SIZE = 200
    page_key = "explorer_page"
    if page_key not in st.session_state:
        st.session_state[page_key] = 0

    total_pages = max(1, (total_filtered - 1) // PAGE_SIZE + 1)
    current_page = min(st.session_state[page_key], total_pages - 1)
    st.session_state[page_key] = current_page

    start = current_page * PAGE_SIZE
    end = start + PAGE_SIZE
    page_df = fdf.iloc[start:end]

    display_cols = ["ASSET TAG", "ASSET DESCRIPTION", "ASSET TYPE", "LOCATION",
                    "BUILDING", "DEPARTMENT", "CONDITION", "RESERVE PRICE",
                    "FAIR MARKET VALUE", "IS_MISSING", "IS_UNTAGGED"]
    display_df = page_df[[c for c in display_cols if c in page_df.columns]].copy()
    display_df.rename(columns={"RESERVE PRICE": "Reserve (KES)", "FAIR MARKET VALUE": "FMV (KES)"}, inplace=True)

    st.markdown(f'<div class="pagination-label">Showing {start+1}–{min(end, total_filtered):,} of {total_filtered:,} assets &nbsp;·&nbsp; Page {current_page+1} of {total_pages}</div>', unsafe_allow_html=True)

    p1, p2 = st.columns([1, 1])
    with p1:
        if st.button("← Previous", disabled=current_page == 0, key="prev_page"):
            st.session_state[page_key] -= 1
            st.rerun()
    with p2:
        if st.button("Next →", disabled=current_page >= total_pages - 1, key="next_page"):
            st.session_state[page_key] += 1
            st.rerun()

    st.dataframe(
        display_df,
        width='stretch',
        hide_index=True,
        column_config={
            "Reserve (KES)": st.column_config.NumberColumn(format="KES %d"),
            "FMV (KES)": st.column_config.NumberColumn(format="KES %d"),
            "IS_MISSING": st.column_config.CheckboxColumn("Missing"),
            "IS_UNTAGGED": st.column_config.CheckboxColumn("Untagged"),
        }
    )

    st.markdown("---")
    st.markdown('<div class="section-header">Asset detail card</div>', unsafe_allow_html=True)

    asset_tags = fdf["ASSET TAG"].tolist()
    selected_tag = st.selectbox("Select asset tag to inspect", ["— Select —"] + asset_tags, key="explorer_select_tag")

    if selected_tag != "— Select —":
        rows = fdf[fdf["ASSET TAG"] == selected_tag]
        if not rows.empty:
            asset_card(rows.iloc[0])

    missing_df = df[df["IS_MISSING"] == True]
    if not missing_df.empty:
        st.markdown("---")
        st.markdown(f'<div class="section-header" style="color:{PALETTE["danger"]}">Missing assets ({len(missing_df)})</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-subtitle">Assets flagged as not found during physical inspection.</div>', unsafe_allow_html=True)
        st.dataframe(
            missing_df[["ASSET TAG", "ASSET DESCRIPTION", "ASSET TYPE", "LOCATION",
                         "BUILDING", "DEPARTMENT", "FAIR MARKET VALUE"]].rename(
                columns={"FAIR MARKET VALUE": "FMV (KES)"}),
            width='stretch', hide_index=True,
            column_config={"FMV (KES)": st.column_config.NumberColumn(format="KES %d")}
        )

    st.markdown("---")
    st.markdown('<div class="section-header">Statistical summary</div>', unsafe_allow_html=True)

    if total_filtered > 0:
        fmv_vals = fdf["FAIR MARKET VALUE"].dropna()
        sc1, sc2, sc3, sc4 = st.columns(4)
        with sc1:
            kpi_card("Min FMV", fmt_kes(fmv_vals.min()))
        with sc2:
            kpi_card("Max FMV", fmt_kes(fmv_vals.max()))
        with sc3:
            kpi_card("Median FMV", fmt_kes(fmv_vals.median()))
        with sc4:
            kpi_card("Std deviation", fmt_kes(fmv_vals.std()))
