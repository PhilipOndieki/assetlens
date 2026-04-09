import os
import json
import pandas as pd
import numpy as np
import streamlit as st

SIDECAR_PATH = "session_data.json"

LAB_VARIANTS = ["LABAROTY", "LABOROTARY", "LABRATORY", "LABORTORY", "LABARATORY"]
LAB_PATTERN = "|".join(LAB_VARIANTS)

EMPTY_SIDECAR = {
    "tag_updates": {},
    "missing_flags": [],
    "new_assets": [],
    "pending_values": {},
    "condition_edits": {},
    "row_edits": {},
}


def load_sidecar() -> dict:
    if os.path.exists(SIDECAR_PATH):
        try:
            with open(SIDECAR_PATH, "r") as f:
                data = json.load(f)
            for key in EMPTY_SIDECAR:
                data.setdefault(key, EMPTY_SIDECAR[key])
            return data
        except (json.JSONDecodeError, IOError):
            return EMPTY_SIDECAR.copy()
    return EMPTY_SIDECAR.copy()


def save_sidecar(data: dict):
    tmp = SIDECAR_PATH + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, SIDECAR_PATH)


def _normalise_lab_col(series: pd.Series) -> pd.Series:
    mask = series.str.upper().str.contains(LAB_PATTERN, na=False, regex=True)
    series = series.copy()
    series.loc[mask] = series.loc[mask].str.upper().str.replace(
        LAB_PATTERN, "LABORATORY", regex=True
    )
    return series


def _clean(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [c.strip() for c in df.columns]

    for alias in [c for c in df.columns if c.upper().startswith("LOCATION") and c != "LOCATION"]:
        df.rename(columns={alias: "LOCATION"}, inplace=True)

    str_cols = df.select_dtypes(include="object").columns.tolist()
    df[str_cols] = df[str_cols].apply(lambda c: c.str.strip())
    df[str_cols] = df[str_cols].replace({"": pd.NA, "nan": pd.NA, "NaN": pd.NA, "None": pd.NA})

    if "LOCATION" in df.columns:
        df["LOCATION"] = df["LOCATION"].str.upper().str.strip()

    if "ASSET TYPE" in df.columns:
        df["ASSET TYPE"] = df["ASSET TYPE"].replace(
            {"FURNITURE AND FITTING": "FURNITURE AND FITTINGS"}
        )

    for col in ["ROOM", "DEPARTMENT", "BUILDING"]:
        if col in df.columns:
            df[col] = _normalise_lab_col(df[col].fillna(""))
            df[col] = df[col].replace({"": pd.NA})

    required = [
        "ASSET TAG", "ASSET DESCRIPTION", "SERIAL NUMBER", "MODEL NUMBER",
        "ASSET TYPE", "LOCATION", "BUILDING", "DEPARTMENT", "FLOOR", "ROOM",
        "USER", "CONDITION", "RESERVE PRICE", "FAIR MARKET VALUE",
    ]
    for col in required:
        if col not in df.columns:
            df[col] = pd.NA

    for col in ["RESERVE PRICE", "FAIR MARKET VALUE"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def _apply_sidecar(asset_df: pd.DataFrame, pending_df: pd.DataFrame, sidecar: dict):
    tag_updates = sidecar.get("tag_updates", {})
    if tag_updates:
        asset_df["ASSET TAG"] = asset_df["ASSET TAG"].replace(tag_updates)
        pending_df["ASSET TAG"] = pending_df["ASSET TAG"].replace(tag_updates)

    missing_flags = set(sidecar.get("missing_flags", []))
    asset_df["IS_MISSING"] = asset_df["ASSET TAG"].isin(missing_flags)

    new_assets = sidecar.get("new_assets", [])
    if new_assets:
        new_df = pd.DataFrame(new_assets)
        asset_df = pd.concat([asset_df, new_df], ignore_index=True)

    pending_values = sidecar.get("pending_values", {})
    if pending_values and not pending_df.empty:
        for tag, vals in pending_values.items():
            mask = pending_df["ASSET TAG"] == tag
            if mask.any():
                pending_df.loc[mask, "FAIR MARKET VALUE"] = vals.get("fmv", pd.NA)
                pending_df.loc[mask, "RESERVE PRICE"] = vals.get("reserve", pd.NA)

    condition_edits = sidecar.get("condition_edits", {})
    if condition_edits:
        for tag, cond in condition_edits.items():
            mask = asset_df["ASSET TAG"] == tag
            asset_df.loc[mask, "CONDITION"] = cond

    row_edits = sidecar.get("row_edits", {})
    if row_edits:
        for tag, edits in row_edits.items():
            mask = asset_df["ASSET TAG"] == tag
            if mask.any():
                for field, value in edits.items():
                    asset_df.loc[mask, field] = value

    return asset_df, pending_df


def _derive_columns(df: pd.DataFrame) -> pd.DataFrame:
    df["FMV_RESERVE_RATIO"] = (
        df["FAIR MARKET VALUE"] / df["RESERVE PRICE"]
    ).replace([np.inf, -np.inf], 0).round(2)

    df["IS_UNTAGGED"] = (
        df["ASSET TAG"].fillna("UNTAGGED").str.upper().str.strip() == "UNTAGGED"
    )
    if "IS_MISSING" not in df.columns:
        df["IS_MISSING"] = False

    return df


@st.cache_data(show_spinner=False, hash_funcs={pd.DataFrame: lambda x: x.shape})
def _load_excel(filepath: str):
    return pd.read_excel(filepath)


def load_data(filepath: str):
    raw = _load_excel(filepath)
    df = _clean(raw.copy())

    mask_pending = df["FAIR MARKET VALUE"].isna() | df["RESERVE PRICE"].isna()
    pending_df = df[mask_pending].copy().reset_index(drop=True)
    asset_df = df[~mask_pending].copy().reset_index(drop=True)

    sidecar = load_sidecar()
    asset_df, pending_df = _apply_sidecar(asset_df, pending_df, sidecar)

    asset_df = _derive_columns(asset_df)

    asset_df["BUILDING"] = asset_df["BUILDING"].fillna("UNASSIGNED")
    asset_df["ASSET TYPE"] = asset_df["ASSET TYPE"].fillna("OTHER")
    asset_df["CONDITION"] = asset_df["CONDITION"].fillna("UNKNOWN")

    return asset_df, pending_df


def get_completeness(df: pd.DataFrame) -> pd.DataFrame:
    total = len(df)
    skip = {"VALUATION_SOURCE", "FMV_RESERVE_RATIO", "IS_UNTAGGED", "IS_MISSING"}
    rows = []
    for col in df.columns:
        if col in skip:
            continue
        filled = df[col].replace({pd.NA: np.nan}).notna().sum()
        pct = round((filled / total) * 100, 1) if total > 0 else 0
        rows.append({"Column": col, "Filled": int(filled), "Total": total, "Completeness (%)": pct})
    return pd.DataFrame(rows)
