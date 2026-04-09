import streamlit as st
import pandas as pd
from datetime import date
from data_loader import load_sidecar, save_sidecar
from export import export_to_excel
from styles import PALETTE

VALUER_NAME = "Philip Barongo Ondieki"

ASSET_TYPES = [
    "FURNITURE AND FITTINGS", "COMPUTER AND ICT EQUIPMENT",
    "LABORATORY EQUIPMENT", "OFFICE EQUIPMENT", "PLANT AND MACHINERY",
    "CONSTRUCTION EQUIPMENTS", "KITCHEN AND CATERING EQUIPMENT",
    "FIRE SAFETY EQUIPMENT",
]

CONDITIONS = ["GOOD", "NEW", "SERVICEABLE", "FAIR", "POOR", "FAULTY", "BROKEN", "OBSOLETE", "OLD"]

CAMPUSES = ["JKUAT MAIN CAMPUS", "JKUAT KAREN", "JKUAT MOMBASA", "JKUAT KITALE"]


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
        <div class="page-title">Valuation editor</div>
        <div class="page-subtitle">Edit existing assets, add new unregistered assets, and export the full register.</div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["Edit register", "Add new asset", "Export"])

    with tab1:
        st.markdown('<div class="section-header">Editable asset register</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-subtitle">Asset Tag is read-only. All other fields are editable. Changes are saved to session_data.json automatically.</div>', unsafe_allow_html=True)

        PAGE_SIZE = 200
        page_key = "editor_page"
        if page_key not in st.session_state:
            st.session_state[page_key] = 0

        total = len(df)
        total_pages = max(1, (total - 1) // PAGE_SIZE + 1)
        current_page = min(st.session_state[page_key], total_pages - 1)
        st.session_state[page_key] = current_page

        start = current_page * PAGE_SIZE
        end = start + PAGE_SIZE

        st.markdown(f'<div class="pagination-label">Showing {start+1}–{min(end, total):,} of {total:,} assets &nbsp;·&nbsp; Page {current_page+1} of {total_pages}</div>', unsafe_allow_html=True)

        p1, p2 = st.columns(2)
        with p1:
            if st.button("← Previous", disabled=current_page == 0, key="editor_prev"):
                st.session_state[page_key] -= 1
                st.rerun()
        with p2:
            if st.button("Next →", disabled=current_page >= total_pages - 1, key="editor_next"):
                st.session_state[page_key] += 1
                st.rerun()

        edit_cols = ["ASSET TAG", "ASSET DESCRIPTION", "ASSET TYPE", "BUILDING",
                     "CONDITION", "RESERVE PRICE", "FAIR MARKET VALUE"]
        page_slice = df.iloc[start:end][edit_cols].copy()

        edited = st.data_editor(
            page_slice,
            use_container_width=True,
            hide_index=True,
            column_config={
                "ASSET TAG": st.column_config.TextColumn("Asset Tag", disabled=True),
                "ASSET DESCRIPTION": st.column_config.TextColumn("Description"),
                "ASSET TYPE": st.column_config.SelectboxColumn("Asset Type", options=ASSET_TYPES),
                "BUILDING": st.column_config.TextColumn("Building"),
                "CONDITION": st.column_config.SelectboxColumn("Condition", options=CONDITIONS),
                "RESERVE PRICE": st.column_config.NumberColumn("Reserve (KES)", min_value=0, step=100, format="KES %d"),
                "FAIR MARKET VALUE": st.column_config.NumberColumn("FMV (KES)", min_value=0, step=100, format="KES %d"),
            },
            num_rows="fixed",
            key="data_editor_main",
        )

        if st.button("Save edits to register", key="save_edits"):
            sidecar = load_sidecar()
            changed = 0
            for i, (_, edited_row) in enumerate(edited.iterrows()):
                tag = edited_row["ASSET TAG"]
                orig_row = df[df["ASSET TAG"] == tag]
                if orig_row.empty:
                    continue
                row_edits = {}
                for col in ["ASSET DESCRIPTION", "ASSET TYPE", "BUILDING", "CONDITION",
                             "RESERVE PRICE", "FAIR MARKET VALUE"]:
                    orig_val = orig_row.iloc[0][col]
                    new_val = edited_row[col]
                    if str(orig_val) != str(new_val):
                        row_edits[col] = new_val
                if row_edits:
                    sidecar.setdefault("row_edits", {})[tag] = row_edits
                    idx = df[df["ASSET TAG"] == tag].index
                    if len(idx):
                        for field, val in row_edits.items():
                            st.session_state["asset_df"].loc[idx[0], field] = val
                    changed += 1
            save_sidecar(sidecar)
            if changed:
                st.success(f"Saved edits for {changed} asset(s).")
                st.rerun()
            else:
                st.info("No changes detected.")

    with tab2:
        st.markdown('<div class="section-header">Add unregistered asset</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-subtitle">Fill all required fields. The asset will immediately appear in all charts and KPIs.</div>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            new_tag = st.text_input("Asset Tag (JKUAT##### or UNTAGGED)", key="new_tag")
            new_desc = st.text_input("Asset Description *", key="new_desc")
            new_type = st.selectbox("Asset Type *", ASSET_TYPES, key="new_type")
            new_location = st.selectbox("Campus *", CAMPUSES, key="new_location")
            buildings = sorted(df[df["LOCATION"] == new_location]["BUILDING"].dropna().unique().tolist())
            new_building = st.selectbox("Building *", buildings if buildings else ["UNASSIGNED"], key="new_building")
        with c2:
            new_dept = st.text_input("Department", key="new_dept")
            new_floor = st.text_input("Floor", key="new_floor")
            new_room = st.text_input("Room", key="new_room")
            new_cond = st.selectbox("Condition *", CONDITIONS, key="new_cond")
            new_fmv = st.number_input("Fair Market Value (KES) *", min_value=0.0, step=100.0, key="new_fmv")
            new_res = st.number_input("Reserve Price (KES) *", min_value=0.0, step=100.0, key="new_res")

        if st.button("Add asset to register", key="add_asset_btn"):
            import re
            errors = []
            tag_clean = new_tag.strip().upper()
            if not tag_clean:
                errors.append("Asset Tag is required.")
            elif tag_clean != "UNTAGGED" and not re.match(r"^JKUAT\d+$", tag_clean):
                errors.append("Tag must be UNTAGGED or match JKUAT##### format.")
            elif tag_clean != "UNTAGGED" and tag_clean in df["ASSET TAG"].str.upper().values:
                errors.append(f"Tag {tag_clean} already exists.")
            if not new_desc.strip():
                errors.append("Description is required.")
            if new_fmv <= 0:
                errors.append("Fair Market Value must be greater than 0.")
            if new_res <= 0:
                errors.append("Reserve Price must be greater than 0.")

            if errors:
                for e in errors:
                    st.error(e)
            else:
                new_row = {
                    "ASSET TAG": tag_clean,
                    "ASSET DESCRIPTION": new_desc.strip(),
                    "SERIAL NUMBER": "",
                    "MODEL NUMBER": "",
                    "ASSET TYPE": new_type,
                    "LOCATION": new_location,
                    "BUILDING": new_building,
                    "DEPARTMENT": new_dept.strip(),
                    "FLOOR": new_floor.strip(),
                    "ROOM": new_room.strip(),
                    "USER": "",
                    "CONDITION": new_cond,
                    "RESERVE PRICE": new_res,
                    "FAIR MARKET VALUE": new_fmv,
                    "FMV_RESERVE_RATIO": round(new_fmv / new_res, 2) if new_res > 0 else 0,
                    "IS_UNTAGGED": tag_clean == "UNTAGGED",
                    "IS_MISSING": False,
                }
                sidecar = load_sidecar()
                sidecar["new_assets"].append(new_row)
                save_sidecar(sidecar)

                import pandas as pd
                st.session_state["asset_df"] = pd.concat(
                    [st.session_state["asset_df"], pd.DataFrame([new_row])],
                    ignore_index=True
                )
                st.success(f"Asset {tag_clean} added to register.")
                st.rerun()

    with tab3:
        st.markdown('<div class="section-header">Export</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-subtitle">Download full register with all edits applied.</div>', unsafe_allow_html=True)

        ex1, ex2 = st.columns(2)
        with ex1:
            with st.spinner("Generating Excel export..."):
                excel_bytes = export_to_excel(
                    st.session_state["asset_df"],
                    st.session_state.get("pending_df", pd.DataFrame()),
                    VALUER_NAME
                )
            st.download_button(
                label="Download full report (.xlsx)",
                data=excel_bytes,
                file_name=f"JKUAT_Asset_Valuation_{date.today().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
        with ex2:
            csv_bytes = st.session_state["asset_df"].to_csv(index=False).encode("utf-8")
            st.download_button(
                label="Download flat CSV (.csv)",
                data=csv_bytes,
                file_name=f"JKUAT_Assets_{date.today().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True,
            )

        st.markdown("---")
        st.markdown('<div class="section-header">Live valuation preview</div>', unsafe_allow_html=True)
        prev = st.session_state["asset_df"].groupby(["LOCATION", "BUILDING"]).agg(
            Count=("ASSET TAG", "count"),
            Total_FMV=("FAIR MARKET VALUE", "sum"),
            Total_Reserve=("RESERVE PRICE", "sum"),
        ).reset_index()
        prev.rename(columns={"LOCATION": "Campus", "BUILDING": "Building",
                              "Total_FMV": "Total FMV (KES)", "Total_Reserve": "Total Reserve (KES)"}, inplace=True)
        st.dataframe(
            prev.style.format({"Total FMV (KES)": "KES {:,.0f}", "Total Reserve (KES)": "KES {:,.0f}"}),
            use_container_width=True, hide_index=True,
        )
