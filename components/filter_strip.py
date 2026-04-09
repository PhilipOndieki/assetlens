import streamlit as st
import pandas as pd


def filter_strip(df: pd.DataFrame, key_prefix: str = "fs") -> pd.DataFrame:
    campuses = sorted(df["LOCATION"].dropna().unique().tolist())
    conditions = sorted(df["CONDITION"].dropna().unique().tolist())
    asset_types = sorted(df["ASSET TYPE"].dropna().unique().tolist())

    st.markdown('<div class="filter-strip">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)

    with c1:
        sel_campus = st.multiselect(
            "Campus", campuses, default=campuses,
            key=f"{key_prefix}_campus"
        )
    with c2:
        sel_cond = st.multiselect(
            "Condition", conditions, default=conditions,
            key=f"{key_prefix}_cond"
        )
    with c3:
        sel_type = st.multiselect(
            "Asset Type", asset_types, default=asset_types,
            key=f"{key_prefix}_type"
        )

    st.markdown('</div>', unsafe_allow_html=True)

    fdf = df[
        df["LOCATION"].isin(sel_campus) &
        df["CONDITION"].isin(sel_cond) &
        df["ASSET TYPE"].isin(sel_type)
    ]
    return fdf
