import streamlit as st
import json
from styles import PALETTE
from data_loader import load_sidecar, save_sidecar


def fmt_kes(v):
    try:
        return f"KES {v:,.0f}"
    except Exception:
        return "—"


def asset_card(row, asset_df_key: str = "asset_df"):
    tag = str(row.get("ASSET TAG", "—"))
    is_missing = bool(row.get("IS_MISSING", False))
    is_untagged = bool(row.get("IS_UNTAGGED", False))
    condition = str(row.get("CONDITION", "—"))

    border_color = PALETTE["danger"] if is_missing else PALETTE["accent"]
    missing_badge = (
        f"<span class='status-badge danger'>MISSING</span>" if is_missing else ""
    )
    untagged_badge = (
        f"<span class='status-badge warning'>UNTAGGED</span>" if is_untagged else ""
    )

    st.markdown(f"""
    <div class="asset-card" style="border-left: 3px solid {border_color};">
        <div class="asset-card-header">
            <span class="asset-tag-label">{tag}</span>
            <div style="display:flex;gap:6px;align-items:center;">
                {missing_badge}{untagged_badge}
                <span class="condition-badge">{condition}</span>
            </div>
        </div>
        <div class="asset-card-desc">{row.get('ASSET DESCRIPTION','—')}</div>
        <div class="asset-card-grid">
            <div class="acf"><span class="acl">Asset Type</span><span class="acv">{row.get('ASSET TYPE','—')}</span></div>
            <div class="acf"><span class="acl">Campus</span><span class="acv">{row.get('LOCATION','—')}</span></div>
            <div class="acf"><span class="acl">Building</span><span class="acv">{str(row.get('BUILDING','—'))[:50]}</span></div>
            <div class="acf"><span class="acl">Department</span><span class="acv">{row.get('DEPARTMENT','—') or '—'}</span></div>
            <div class="acf"><span class="acl">Floor / Room</span><span class="acv">{row.get('FLOOR','—') or '—'} / {row.get('ROOM','—') or '—'}</span></div>
            <div class="acf"><span class="acl">Serial No.</span><span class="acv">{row.get('SERIAL NUMBER','—') or '—'}</span></div>
            <div class="acf"><span class="acl">Reserve Price</span><span class="acv">{fmt_kes(row.get('RESERVE PRICE',0))}</span></div>
            <div class="acf"><span class="acl">Fair Market Value</span><span class="acv" style="color:{PALETTE['accent']};font-size:17px;font-weight:700">{fmt_kes(row.get('FAIR MARKET VALUE',0))}</span></div>
            <div class="acf"><span class="acl">FMV/Reserve Ratio</span><span class="acv">{row.get('FMV_RESERVE_RATIO','—')}</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        if is_untagged:
            new_tag = st.text_input(
                "Assign tag number (JKUAT#####)",
                key=f"tag_input_{tag}",
                placeholder="e.g. JKUAT12589"
            )
            if st.button("Confirm tag", key=f"tag_btn_{tag}"):
                import re
                df = st.session_state[asset_df_key]
                if not re.match(r"^JKUAT\d+$", new_tag.strip().upper()):
                    st.error("Tag must match format JKUAT##### (e.g. JKUAT12589)")
                elif new_tag.strip().upper() in df["ASSET TAG"].str.upper().values:
                    st.error(f"Tag {new_tag} already exists in the register.")
                else:
                    sidecar = load_sidecar()
                    sidecar["tag_updates"][tag] = new_tag.strip().upper()
                    save_sidecar(sidecar)
                    idx = df[df["ASSET TAG"] == tag].index
                    if len(idx):
                        st.session_state[asset_df_key].loc[idx[0], "ASSET TAG"] = new_tag.strip().upper()
                        st.session_state[asset_df_key].loc[idx[0], "IS_UNTAGGED"] = False
                    st.success(f"Asset tagged as {new_tag.strip().upper()} successfully")
                    st.rerun()

    with col_b:
        if is_missing:
            if st.button("Unflag missing", key=f"unflag_{tag}"):
                sidecar = load_sidecar()
                if tag in sidecar["missing_flags"]:
                    sidecar["missing_flags"].remove(tag)
                save_sidecar(sidecar)
                df = st.session_state[asset_df_key]
                idx = df[df["ASSET TAG"] == tag].index
                if len(idx):
                    st.session_state[asset_df_key].loc[idx[0], "IS_MISSING"] = False
                st.rerun()
        else:
            if st.button("Flag as missing", key=f"flag_{tag}"):
                sidecar = load_sidecar()
                if tag not in sidecar["missing_flags"]:
                    sidecar["missing_flags"].append(tag)
                save_sidecar(sidecar)
                df = st.session_state[asset_df_key]
                idx = df[df["ASSET TAG"] == tag].index
                if len(idx):
                    st.session_state[asset_df_key].loc[idx[0], "IS_MISSING"] = True
                st.rerun()

    with col_c:
        edit_key = f"edit_toggle_{tag}"
        if st.button("Edit asset", key=f"edit_btn_{tag}"):
            st.session_state[edit_key] = not st.session_state.get(edit_key, False)

    if st.session_state.get(f"edit_toggle_{tag}", False):
        _inline_edit_form(row, tag, asset_df_key)


def _inline_edit_form(row, tag: str, asset_df_key: str):
    from data_loader import load_sidecar, save_sidecar
    import numpy as np

    ASSET_TYPES = [
        "FURNITURE AND FITTINGS", "COMPUTER AND ICT EQUIPMENT",
        "LABORATORY EQUIPMENT", "OFFICE EQUIPMENT", "PLANT AND MACHINERY",
        "CONSTRUCTION EQUIPMENTS", "KITCHEN AND CATERING EQUIPMENT",
        "FIRE SAFETY EQUIPMENT",
    ]
    CONDITIONS = ["GOOD", "NEW", "SERVICEABLE", "FAIR", "POOR", "FAULTY", "BROKEN", "OBSOLETE", "OLD"]

    st.markdown('<div class="edit-form">', unsafe_allow_html=True)
    st.markdown("**Edit asset details**")

    c1, c2 = st.columns(2)
    with c1:
        new_desc = st.text_input("Description", value=str(row.get("ASSET DESCRIPTION", "") or ""), key=f"ed_desc_{tag}")
        new_type = st.selectbox("Asset Type", ASSET_TYPES,
            index=ASSET_TYPES.index(row.get("ASSET TYPE")) if row.get("ASSET TYPE") in ASSET_TYPES else 0,
            key=f"ed_type_{tag}")
        new_dept = st.text_input("Department", value=str(row.get("DEPARTMENT", "") or ""), key=f"ed_dept_{tag}")
        new_floor = st.text_input("Floor", value=str(row.get("FLOOR", "") or ""), key=f"ed_floor_{tag}")
        new_room = st.text_input("Room", value=str(row.get("ROOM", "") or ""), key=f"ed_room_{tag}")
    with c2:
        new_cond = st.selectbox("Condition", CONDITIONS,
            index=CONDITIONS.index(row.get("CONDITION")) if row.get("CONDITION") in CONDITIONS else 0,
            key=f"ed_cond_{tag}")
        fmv_val = float(row.get("FAIR MARKET VALUE", 0) or 0)
        res_val = float(row.get("RESERVE PRICE", 0) or 0)
        new_fmv = st.number_input("Fair Market Value (KES)", value=fmv_val, min_value=0.0, step=100.0, key=f"ed_fmv_{tag}")
        new_res = st.number_input("Reserve Price (KES)", value=res_val, min_value=0.0, step=100.0, key=f"ed_res_{tag}")
        new_serial = st.text_input("Serial Number", value=str(row.get("SERIAL NUMBER", "") or ""), key=f"ed_serial_{tag}")

    if st.button("Save changes", key=f"ed_save_{tag}"):
        sidecar = load_sidecar()
        edits = {
            "ASSET DESCRIPTION": new_desc,
            "ASSET TYPE": new_type,
            "DEPARTMENT": new_dept,
            "FLOOR": new_floor,
            "ROOM": new_room,
            "CONDITION": new_cond,
            "FAIR MARKET VALUE": new_fmv,
            "RESERVE PRICE": new_res,
            "SERIAL NUMBER": new_serial,
        }
        sidecar.setdefault("row_edits", {})[tag] = edits
        save_sidecar(sidecar)

        df = st.session_state[asset_df_key]
        idx = df[df["ASSET TAG"] == tag].index
        if len(idx):
            for field, val in edits.items():
                st.session_state[asset_df_key].loc[idx[0], field] = val
            if new_res > 0:
                ratio = round(new_fmv / new_res, 2)
                st.session_state[asset_df_key].loc[idx[0], "FMV_RESERVE_RATIO"] = ratio

        st.session_state[f"edit_toggle_{tag}"] = False
        st.success("Changes saved.")
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
