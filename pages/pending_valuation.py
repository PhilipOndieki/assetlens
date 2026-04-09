import streamlit as st
import pandas as pd
from datetime import date
from data_loader import load_sidecar, save_sidecar
from components.kpi_card import kpi_card
from export import export_pending_excel
from styles import PALETTE


def fmt_kes(v):
    try:
        if pd.isna(v):
            return "—"
        return f"KES {v:,.0f}"
    except Exception:
        return "—"


def render():
    pending_df = st.session_state.get("pending_df")
    asset_df = st.session_state.get("asset_df")

    if pending_df is None:
        pending_df = pd.DataFrame()

    st.markdown("""
    <div class="page-header">
        <div class="page-title">Pending valuation</div>
        <div class="page-subtitle">Assets missing Fair Market Value or Reserve Price. Enter values to move them into the main register.</div>
    </div>
    """, unsafe_allow_html=True)

    sidecar = load_sidecar()
    pending_values = sidecar.get("pending_values", {})
    total_pending = len(pending_df)
    valued_count = len(pending_values)
    remaining = max(0, total_pending - valued_count)

    k1, k2, k3 = st.columns(3)
    with k1:
        kpi_card("Pending valuation", f"{total_pending:,}", "Assets without FMV or Reserve")
    with k2:
        kpi_card("Valued this session", f"{valued_count:,}", "", "positive" if valued_count > 0 else "neutral")
    with k3:
        kpi_card("Remaining", f"{remaining:,}", "", "warning" if remaining > 0 else "positive")

    if total_pending > 0:
        progress_val = min(1.0, valued_count / total_pending) if total_pending > 0 else 0.0
        st.progress(progress_val)
        st.markdown(f'<div class="pagination-label">{total_pending} assets pending &nbsp;·&nbsp; {valued_count} valued this session</div>', unsafe_allow_html=True)

    st.markdown("---")

    if pending_df.empty:
        st.success("All assets have been valued. No pending items.")
        return

    campuses = sorted(pending_df["LOCATION"].dropna().unique().tolist())
    asset_types = sorted(pending_df["ASSET TYPE"].dropna().unique().tolist())

    c1, c2 = st.columns(2)
    with c1:
        sel_campus = st.multiselect("Filter campus", campuses, default=campuses, key="pend_campus")
    with c2:
        sel_type = st.multiselect("Filter asset type", asset_types, default=asset_types, key="pend_type")

    fdf = pending_df[
        pending_df["LOCATION"].isin(sel_campus) &
        pending_df["ASSET TYPE"].isin(sel_type)
    ]

    st.markdown('<div class="section-header">Pending assets</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Enter FMV and Reserve Price, then click "Move to register" to add to the main asset register.</div>', unsafe_allow_html=True)

    display_cols = ["ASSET TAG", "ASSET DESCRIPTION", "ASSET TYPE", "LOCATION",
                    "BUILDING", "DEPARTMENT", "CONDITION"]
    fdf_display = fdf[[c for c in display_cols if c in fdf.columns]].copy()
    st.dataframe(fdf_display, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown('<div class="section-header">Value an asset</div>', unsafe_allow_html=True)

    tags = fdf["ASSET TAG"].tolist()
    selected_tag = st.selectbox("Select asset to value", ["— Select —"] + tags, key="pend_select")

    if selected_tag != "— Select —":
        row = fdf[fdf["ASSET TAG"] == selected_tag].iloc[0]

        st.markdown(f"""
        <div class="asset-card">
            <div class="asset-card-header">
                <span class="asset-tag-label">{row.get('ASSET TAG','—')}</span>
            </div>
            <div class="asset-card-desc">{row.get('ASSET DESCRIPTION','—')}</div>
            <div class="asset-card-grid">
                <div class="acf"><span class="acl">Asset Type</span><span class="acv">{row.get('ASSET TYPE','—')}</span></div>
                <div class="acf"><span class="acl">Campus</span><span class="acv">{row.get('LOCATION','—')}</span></div>
                <div class="acf"><span class="acl">Building</span><span class="acv">{str(row.get('BUILDING','—'))[:50]}</span></div>
                <div class="acf"><span class="acl">Condition</span><span class="acv">{row.get('CONDITION','—')}</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        existing = pending_values.get(selected_tag, {})
        pv1, pv2 = st.columns(2)
        with pv1:
            fmv_input = st.number_input(
                "Fair Market Value (KES)",
                value=float(existing.get("fmv", 0) or 0),
                min_value=0.0, step=100.0,
                key=f"pend_fmv_{selected_tag}"
            )
        with pv2:
            res_input = st.number_input(
                "Reserve Price (KES)",
                value=float(existing.get("reserve", 0) or 0),
                min_value=0.0, step=100.0,
                key=f"pend_res_{selected_tag}"
            )

        col_save, col_move = st.columns(2)

        with col_save:
            if st.button("Save values (keep in pending)", key=f"save_pend_{selected_tag}"):
                sidecar = load_sidecar()
                sidecar["pending_values"][selected_tag] = {"fmv": fmv_input, "reserve": res_input}
                save_sidecar(sidecar)
                st.success("Values saved. Asset remains in pending until moved.")
                st.rerun()

        with col_move:
            move_enabled = fmv_input > 0 and res_input > 0
            if st.button(
                "Move to register",
                key=f"move_pend_{selected_tag}",
                disabled=not move_enabled,
                help="Both FMV and Reserve must be greater than 0" if not move_enabled else ""
            ):
                sidecar = load_sidecar()
                if selected_tag in sidecar["pending_values"]:
                    del sidecar["pending_values"][selected_tag]

                new_row = row.to_dict()
                new_row["FAIR MARKET VALUE"] = fmv_input
                new_row["RESERVE PRICE"] = res_input
                new_row["FMV_RESERVE_RATIO"] = round(fmv_input / res_input, 2) if res_input > 0 else 0
                new_row["IS_UNTAGGED"] = str(new_row.get("ASSET TAG", "")).upper() == "UNTAGGED"
                new_row["IS_MISSING"] = False

                sidecar["new_assets"].append(new_row)
                save_sidecar(sidecar)

                st.session_state["asset_df"] = pd.concat(
                    [st.session_state["asset_df"], pd.DataFrame([new_row])],
                    ignore_index=True
                )
                mask = st.session_state["pending_df"]["ASSET TAG"] != selected_tag
                st.session_state["pending_df"] = st.session_state["pending_df"][mask].reset_index(drop=True)

                st.success(f"Asset {selected_tag} moved to main register.")
                st.rerun()

    st.markdown("---")
    st.markdown('<div class="section-header">Export pending list</div>', unsafe_allow_html=True)

    with st.spinner("Preparing pending export..."):
        pending_bytes = export_pending_excel(pending_df)
    st.download_button(
        label="Download pending valuation list (.xlsx)",
        data=pending_bytes,
        file_name=f"JKUAT_Pending_Valuation_{date.today().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )
