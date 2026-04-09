import pandas as pd
import numpy as np
import streamlit as st
from valuation_engine import estimate_values, apply_condition_multiplier

CAMPUSES = [
    "JKUAT MAIN CAMPUS",
    "JKUAT KAREN",
    "JKUAT MOMBASA",
    "JKUAT KITALE",
]

CAMPUS_BUILDINGS = {
    "JKUAT MAIN CAMPUS": [
        "COLLEGE OF HUMAN RESOURCES AND ENTREPRENUERSHIP DEVELOPMENT(COHRED) BUILDING",
        "MAIN ADMINISTRATION BLOCK",
        "COLLEGE OF ENGINEERING AND TECHNOLOGY (COETEC)",
        "LIBRARY BLOCK",
        "SCIENCE COMPLEX",
        "STUDENT CENTRE",
    ],
    "JKUAT KAREN": [
        "KAREN ADMINISTRATION BLOCK",
        "KAREN LECTURE BLOCK A",
        "KAREN COMPUTER LAB",
        "KAREN LIBRARY",
    ],
    "JKUAT MOMBASA": [
        "MOMBASA ADMINISTRATION BLOCK",
        "MOMBASA LECTURE BLOCK",
        "MOMBASA ICT CENTRE",
        "MOMBASA LIBRARY",
    ],
    "JKUAT KITALE": [
        "KITALE ADMINISTRATION BLOCK",
        "KITALE LECTURE HALL",
        "KITALE ICT LAB",
        "KITALE LIBRARY",
    ],
}

SYNTHETIC_ASSETS = {
    "JKUAT KAREN": [
        ("JKUAT K-001", "CHAIR MIDBACK LEATHER METALLIC FRAME", "FURNITURE AND FITTINGS", "KAREN ADMINISTRATION BLOCK", "Good"),
        ("JKUAT K-002", "MONITOR HP", "COMPUTER AND ICT EQUIPMENT", "KAREN COMPUTER LAB", "Good"),
        ("JKUAT K-003", "TABLE WOODEN 3 DRAWERS", "FURNITURE AND FITTINGS", "KAREN ADMINISTRATION BLOCK", "Fair"),
        ("JKUAT K-004", "DESKTOP PC LENOVO", "COMPUTER AND ICT EQUIPMENT", "KAREN COMPUTER LAB", "Good"),
        ("JKUAT K-005", "PROJECTOR EPSON", "COMPUTER AND ICT EQUIPMENT", "KAREN LECTURE BLOCK A", "Good"),
        ("JKUAT K-006", "CHAIR CONFERENCE ORANGE METALLIC FRAME", "FURNITURE AND FITTINGS", "KAREN LECTURE BLOCK A", "Good"),
        ("JKUAT K-007", "CABINET WOODEN UPPER AND LOWER PARTITION", "FURNITURE AND FITTINGS", "KAREN LIBRARY", "Fair"),
        ("JKUAT K-008", "LAPTOP DELL LATITUDE", "COMPUTER AND ICT EQUIPMENT", "KAREN ADMINISTRATION BLOCK", "Good"),
        ("JKUAT K-009", "SOFASET WOODEN 3 SEATER", "FURNITURE AND FITTINGS", "KAREN ADMINISTRATION BLOCK", "Good"),
        ("JKUAT K-010", "PRINTER BROTHER LASER", "COMPUTER AND ICT EQUIPMENT", "KAREN ADMINISTRATION BLOCK", "Fair"),
        ("JKUAT K-011", "TABLE WOODEN", "FURNITURE AND FITTINGS", "KAREN LIBRARY", "Good"),
        ("JKUAT K-012", "TELEPHONE HANDSET AVAYA", "COMPUTER AND ICT EQUIPMENT", "KAREN ADMINISTRATION BLOCK", "Good"),
    ],
    "JKUAT MOMBASA": [
        ("JKUAT M-001", "CHAIR MIDBACK LEATHER METALLIC FRAME", "FURNITURE AND FITTINGS", "MOMBASA ADMINISTRATION BLOCK", "Good"),
        ("JKUAT M-002", "TABLE WOODEN 3 DRAWERS", "FURNITURE AND FITTINGS", "MOMBASA ADMINISTRATION BLOCK", "Good"),
        ("JKUAT M-003", "DESKTOP PC HP", "COMPUTER AND ICT EQUIPMENT", "MOMBASA ICT CENTRE", "Good"),
        ("JKUAT M-004", "MONITOR SAMSUNG", "COMPUTER AND ICT EQUIPMENT", "MOMBASA ICT CENTRE", "Fair"),
        ("JKUAT M-005", "PROJECTOR BENQ", "COMPUTER AND ICT EQUIPMENT", "MOMBASA LECTURE BLOCK", "Good"),
        ("JKUAT M-006", "CHAIR CONFERENCE ORANGE METALLIC FRAME", "FURNITURE AND FITTINGS", "MOMBASA LECTURE BLOCK", "Good"),
        ("JKUAT M-007", "CABINET WOODEN", "FURNITURE AND FITTINGS", "MOMBASA LIBRARY", "Fair"),
        ("JKUAT M-008", "LAPTOP HP ELITEBOOK", "COMPUTER AND ICT EQUIPMENT", "MOMBASA ADMINISTRATION BLOCK", "Good"),
        ("JKUAT M-009", "TABLE WOODEN", "FURNITURE AND FITTINGS", "MOMBASA LIBRARY", "Poor"),
        ("JKUAT M-010", "PRINTER CANON", "COMPUTER AND ICT EQUIPMENT", "MOMBASA ADMINISTRATION BLOCK", "Good"),
        ("JKUAT M-011", "SOFASET WOODEN 3 SEATER", "FURNITURE AND FITTINGS", "MOMBASA ADMINISTRATION BLOCK", "Good"),
        ("JKUAT M-012", "TELEPHONE HANDSET PANASONIC", "COMPUTER AND ICT EQUIPMENT", "MOMBASA ADMINISTRATION BLOCK", "Good"),
        ("JKUAT M-013", "CHAIR MIDBACK LEATHER METALLIC FRAME", "FURNITURE AND FITTINGS", "MOMBASA ICT CENTRE", "Good"),
        ("JKUAT M-014", "TABLE WOODEN 3 DRAWERS", "FURNITURE AND FITTINGS", "MOMBASA ICT CENTRE", "Fair"),
    ],
    "JKUAT KITALE": [
        ("JKUAT KT-001", "CHAIR MIDBACK LEATHER METALLIC FRAME", "FURNITURE AND FITTINGS", "KITALE ADMINISTRATION BLOCK", "Good"),
        ("JKUAT KT-002", "CHAIR CONFERENCE METALLIC FRAME", "FURNITURE AND FITTINGS", "KITALE LECTURE HALL", "Good"),
        ("JKUAT KT-003", "TABLE WOODEN 3 DRAWERS", "FURNITURE AND FITTINGS", "KITALE ADMINISTRATION BLOCK", "Good"),
        ("JKUAT KT-004", "DESKTOP PC LENOVO", "COMPUTER AND ICT EQUIPMENT", "KITALE ICT LAB", "Good"),
        ("JKUAT KT-005", "MONITOR LG", "COMPUTER AND ICT EQUIPMENT", "KITALE ICT LAB", "Good"),
        ("JKUAT KT-006", "PROJECTOR OPTOMA", "COMPUTER AND ICT EQUIPMENT", "KITALE LECTURE HALL", "Fair"),
        ("JKUAT KT-007", "CABINET WOODEN", "FURNITURE AND FITTINGS", "KITALE LIBRARY", "Good"),
        ("JKUAT KT-008", "LAPTOP LENOVO THINKPAD", "COMPUTER AND ICT EQUIPMENT", "KITALE ADMINISTRATION BLOCK", "Good"),
        ("JKUAT KT-009", "TABLE WOODEN", "FURNITURE AND FITTINGS", "KITALE LIBRARY", "Fair"),
        ("JKUAT KT-010", "TELEPHONE HANDSET CISCO", "COMPUTER AND ICT EQUIPMENT", "KITALE ADMINISTRATION BLOCK", "Good"),
    ],
}


def _build_synthetic_df() -> pd.DataFrame:
    rows = []
    for campus, assets in SYNTHETIC_ASSETS.items():
        for tag, desc, atype, building, cond in assets:
            rows.append({
                "ASSET TAG": tag,
                "ASSET DESCRIPTION": desc,
                "SERIAL NUMBER": "",
                "MODEL NUMBER": "",
                "ASSET TYPE": atype,
                "LOCATION": campus,
                "BUILDING": building,
                "DEPARTMENT": "",
                "FLOOR": "",
                "ROOM": "",
                "USER": "",
                "CONDITION": cond,
                "RESERVE PRICE": np.nan,
                "FAIR MARKET VALUE": np.nan,
            })
    return pd.DataFrame(rows)


@st.cache_data(show_spinner=False)
def load_data(filepath: str) -> pd.DataFrame:
    try:
        df = pd.read_excel(filepath)
    except FileNotFoundError:
        return pd.DataFrame()

    # Normalise column names — strip whitespace
    df.columns = [c.strip() for c in df.columns]
    # Rename LOCATION to normalised form
    if "LOCATION" not in df.columns:
        for c in df.columns:
            if c.upper().startswith("LOCATION"):
                df.rename(columns={c: "LOCATION"}, inplace=True)
                break

    # Strip string columns
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.strip()
        df[col] = df[col].replace({"nan": "", "NaN": "", "None": ""})

    # Normalise location to uppercase
    if "LOCATION" in df.columns:
        df["LOCATION"] = df["LOCATION"].str.upper().str.strip()

    # Merge synthetic campus data
    synthetic = _build_synthetic_df()
    df = pd.concat([df, synthetic], ignore_index=True)

    # Ensure required columns exist with defaults
    required = ["ASSET TAG", "ASSET DESCRIPTION", "ASSET TYPE", "LOCATION",
                "BUILDING", "CONDITION", "RESERVE PRICE", "FAIR MARKET VALUE"]
    for col in required:
        if col not in df.columns:
            df[col] = ""

    # Default condition
    df["CONDITION"] = df["CONDITION"].replace({"": "Good", "nan": "Good"}).fillna("Good")
    df.loc[~df["CONDITION"].isin(["Good", "Fair", "Poor", "Condemned"]), "CONDITION"] = "Good"

    # Convert numeric columns
    for col in ["RESERVE PRICE", "FAIR MARKET VALUE"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Valuation source flag
    df["VALUATION_SOURCE"] = "Original"
    mask = df["FAIR MARKET VALUE"].isna() | df["RESERVE PRICE"].isna()
    df.loc[mask, "VALUATION_SOURCE"] = "Estimated"

    # Apply valuation fill
    for idx, row in df[mask].iterrows():
        fmv, reserve = estimate_values(
            str(row.get("ASSET DESCRIPTION", "")),
            str(row.get("ASSET TYPE", ""))
        )
        fmv, reserve = apply_condition_multiplier(fmv, reserve, str(row.get("CONDITION", "Good")))
        if pd.isna(row["FAIR MARKET VALUE"]):
            df.at[idx, "FAIR MARKET VALUE"] = fmv
        if pd.isna(row["RESERVE PRICE"]):
            df.at[idx, "RESERVE PRICE"] = reserve

    # Derived columns
    df["FMV_RESERVE_RATIO"] = df.apply(
        lambda r: round(r["FAIR MARKET VALUE"] / r["RESERVE PRICE"], 2)
        if r["RESERVE PRICE"] and r["RESERVE PRICE"] > 0 else 0.0,
        axis=1
    )

    # Ensure BUILDING not empty
    df["BUILDING"] = df["BUILDING"].replace({"": "UNASSIGNED", "nan": "UNASSIGNED"}).fillna("UNASSIGNED")
    df["ASSET TYPE"] = df["ASSET TYPE"].replace({"": "OTHER", "nan": "OTHER"}).fillna("OTHER")

    return df


def get_completeness(df: pd.DataFrame) -> pd.DataFrame:
    total = len(df)
    rows = []
    for col in df.columns:
        if col in ["VALUATION_SOURCE", "FMV_RESERVE_RATIO"]:
            continue
        filled = df[col].replace({"": np.nan, "nan": np.nan}).notna().sum()
        pct = round((filled / total) * 100, 1) if total > 0 else 0
        rows.append({"Column": col, "Filled": int(filled), "Total": total, "Completeness (%)": pct})
    return pd.DataFrame(rows)
