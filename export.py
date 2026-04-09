import io
import pandas as pd
from datetime import date
from openpyxl import Workbook
from openpyxl.styles import (
    Font, PatternFill, Alignment, Border, Side, numbers
)
from openpyxl.utils import get_column_letter


GOLD = "C9A84C"
NAVY = "0D1B2A"
DARK_BLUE = "1B2E45"
WHITE = "F0F4F8"
MUTED = "8899AA"
SUCCESS = "2ECC71"
DANGER = "E74C3C"


def _thin_border():
    s = Side(style="thin", color="243550")
    return Border(left=s, right=s, top=s, bottom=s)


def _header_cell(ws, row, col, value, bold=True, bg=DARK_BLUE, fg=GOLD, size=11):
    cell = ws.cell(row=row, column=col, value=value)
    cell.font = Font(name="Calibri", bold=bold, color=fg, size=size)
    cell.fill = PatternFill("solid", fgColor=bg)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = _thin_border()
    return cell


def _data_cell(ws, row, col, value, bold=False, number_format=None):
    cell = ws.cell(row=row, column=col, value=value)
    cell.font = Font(name="Calibri", bold=bold, color="D0D8E4", size=10)
    cell.fill = PatternFill("solid", fgColor="0D1B2A")
    cell.alignment = Alignment(horizontal="left", vertical="center")
    cell.border = _thin_border()
    if number_format:
        cell.number_format = number_format
    return cell


def export_to_excel(df: pd.DataFrame, valuer_name: str = "Philip Barongo Ondieki") -> bytes:
    wb = Workbook()

    # ── Sheet 1: Full Asset Register ──
    ws1 = wb.active
    ws1.title = "Asset Register"
    ws1.sheet_view.showGridLines = False

    # Title block
    ws1.merge_cells("A1:N2")
    title_cell = ws1.cell(row=1, column=1,
                          value="JKUAT ASSET VALUATION REGISTER — 2025")
    title_cell.font = Font(name="Calibri", bold=True, color=GOLD, size=16)
    title_cell.fill = PatternFill("solid", fgColor=NAVY)
    title_cell.alignment = Alignment(horizontal="center", vertical="center")

    ws1.merge_cells("A3:N3")
    sub_cell = ws1.cell(row=3, column=1,
                        value=f"Prepared by: {valuer_name}  |  Date: {date.today().strftime('%d %B %Y')}  |  Ref: JKUAT/VAL/2025/001")
    sub_cell.font = Font(name="Calibri", color=MUTED, size=10, italic=True)
    sub_cell.fill = PatternFill("solid", fgColor=NAVY)
    sub_cell.alignment = Alignment(horizontal="center", vertical="center")
    ws1.row_dimensions[3].height = 18

    headers = [
        "ASSET TAG", "ASSET DESCRIPTION", "SERIAL NUMBER", "MODEL NUMBER",
        "ASSET TYPE", "LOCATION", "BUILDING", "DEPARTMENT", "FLOOR", "ROOM",
        "USER", "CONDITION", "RESERVE PRICE (KES)", "FAIR MARKET VALUE (KES)",
        "VALUATION SOURCE", "FMV/RESERVE RATIO"
    ]
    for col_idx, h in enumerate(headers, 1):
        _header_cell(ws1, 5, col_idx, h)

    col_map = {
        "ASSET TAG": 1, "ASSET DESCRIPTION": 2, "SERIAL NUMBER": 3,
        "MODEL NUMBER": 4, "ASSET TYPE": 5, "LOCATION": 6, "BUILDING": 7,
        "DEPARTMENT": 8, "FLOOR": 9, "ROOM": 10, "USER": 11,
        "CONDITION": 12, "RESERVE PRICE": 13, "FAIR MARKET VALUE": 14,
        "VALUATION_SOURCE": 15, "FMV_RESERVE_RATIO": 16
    }

    for row_idx, (_, row) in enumerate(df.iterrows(), 6):
        row_fill_color = "111F30" if row_idx % 2 == 0 else "0D1B2A"
        for col_name, col_idx in col_map.items():
            val = row.get(col_name, "")
            c = ws1.cell(row=row_idx, column=col_idx, value=val if val != "" else None)
            c.font = Font(name="Calibri", color="D0D8E4", size=10)
            c.fill = PatternFill("solid", fgColor=row_fill_color)
            c.alignment = Alignment(horizontal="left", vertical="center")
            c.border = _thin_border()
            if col_idx in (13, 14):
                c.number_format = '#,##0.00'
                c.alignment = Alignment(horizontal="right", vertical="center")
            if col_idx == 16:
                c.number_format = '0.00'
                c.alignment = Alignment(horizontal="center", vertical="center")
            if col_name == "CONDITION":
                color_map = {"Good": "1A4731", "Fair": "4A3C00", "Poor": "4A1500", "Condemned": "3D0000"}
                bg = color_map.get(str(val), "0D1B2A")
                c.fill = PatternFill("solid", fgColor=bg)

    col_widths = [14, 38, 18, 14, 28, 22, 42, 20, 8, 18, 16, 12, 20, 22, 16, 14]
    for i, w in enumerate(col_widths, 1):
        ws1.column_dimensions[get_column_letter(i)].width = w
    ws1.row_dimensions[1].height = 36
    ws1.row_dimensions[5].height = 32

    # ── Sheet 2: Summary Pivot ──
    ws2 = wb.create_sheet("Summary by Campus & Building")
    ws2.sheet_view.showGridLines = False

    ws2.merge_cells("A1:G2")
    t = ws2.cell(row=1, column=1, value="VALUATION SUMMARY — BY CAMPUS, BUILDING & ASSET TYPE")
    t.font = Font(name="Calibri", bold=True, color=GOLD, size=14)
    t.fill = PatternFill("solid", fgColor=NAVY)
    t.alignment = Alignment(horizontal="center", vertical="center")

    pivot_headers = ["CAMPUS", "BUILDING", "ASSET TYPE", "COUNT", "TOTAL FMV (KES)", "AVG FMV (KES)", "TOTAL RESERVE (KES)", "FMV/RESERVE"]
    for ci, h in enumerate(pivot_headers, 1):
        _header_cell(ws2, 4, ci, h)

    summary = (
        df.groupby(["LOCATION", "BUILDING", "ASSET TYPE"])
        .agg(
            COUNT=("ASSET TAG", "count"),
            TOTAL_FMV=("FAIR MARKET VALUE", "sum"),
            AVG_FMV=("FAIR MARKET VALUE", "mean"),
            TOTAL_RESERVE=("RESERVE PRICE", "sum"),
        )
        .reset_index()
    )
    summary["FMV_RESERVE"] = (summary["TOTAL_FMV"] / summary["TOTAL_RESERVE"]).round(2)

    for ri, (_, row) in enumerate(summary.iterrows(), 5):
        for ci, val in enumerate([
            row["LOCATION"], row["BUILDING"], row["ASSET TYPE"],
            row["COUNT"], row["TOTAL_FMV"], row["AVG_FMV"], row["TOTAL_RESERVE"], row["FMV_RESERVE"]
        ], 1):
            c = ws2.cell(row=ri, column=ci, value=val)
            c.font = Font(name="Calibri", color="D0D8E4", size=10)
            fill_c = "111F30" if ri % 2 == 0 else "0D1B2A"
            c.fill = PatternFill("solid", fgColor=fill_c)
            c.alignment = Alignment(horizontal="left", vertical="center")
            c.border = _thin_border()
            if ci in (5, 6, 7):
                c.number_format = '#,##0.00'
                c.alignment = Alignment(horizontal="right", vertical="center")

    for i, w in enumerate([22, 42, 28, 8, 20, 20, 20, 12], 1):
        ws2.column_dimensions[get_column_letter(i)].width = w

    # ── Sheet 3: Valuation Basis ──
    ws3 = wb.create_sheet("Valuation Basis")
    ws3.sheet_view.showGridLines = False

    ws3.merge_cells("A1:D2")
    tb = ws3.cell(row=1, column=1, value="VALUATION BASIS & METHODOLOGY NOTES")
    tb.font = Font(name="Calibri", bold=True, color=GOLD, size=14)
    tb.fill = PatternFill("solid", fgColor=NAVY)
    tb.alignment = Alignment(horizontal="center", vertical="center")

    notes = [
        ("Method:", "Assets with blank Reserve Price or Fair Market Value were valued using a Schedule of Rates based on current Kenyan market conditions (Q1 2025)."),
        ("Condition Adjustment:", "Good = 100% | Fair = 70% | Poor = 40% | Condemned = 10% of base rate."),
        ("Basis of Value:", "Fair Market Value — the estimated amount for which an asset should exchange on the date of valuation between a willing buyer and a willing seller."),
        ("Standards:", "Valuation conducted in accordance with the Kenya Valuers Act Cap 532 and the International Valuation Standards (IVS)."),
        ("Disclaimer:", "Values assigned to estimated assets are indicative and subject to revision upon physical inspection."),
    ]

    for ri, (label, note) in enumerate(notes, 5):
        lc = ws3.cell(row=ri, column=1, value=label)
        lc.font = Font(name="Calibri", bold=True, color=GOLD, size=10)
        lc.fill = PatternFill("solid", fgColor=DARK_BLUE)
        lc.alignment = Alignment(horizontal="left", vertical="top")
        lc.border = _thin_border()

        ws3.merge_cells(f"B{ri}:D{ri}")
        nc = ws3.cell(row=ri, column=2, value=note)
        nc.font = Font(name="Calibri", color="D0D8E4", size=10)
        nc.fill = PatternFill("solid", fgColor="0D1B2A")
        nc.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
        nc.border = _thin_border()
        ws3.row_dimensions[ri].height = 40

    # Source breakdown
    ws3.cell(row=11, column=1, value="Valuation Source Breakdown").font = Font(name="Calibri", bold=True, color=GOLD, size=11)
    for ci, h in enumerate(["Source", "Count", "% of Total"], 1):
        _header_cell(ws3, 12, ci, h)

    src = df.groupby("VALUATION_SOURCE").size().reset_index(name="COUNT")
    total = src["COUNT"].sum()
    for ri, (_, row) in enumerate(src.iterrows(), 13):
        ws3.cell(row=ri, column=1, value=row["VALUATION_SOURCE"]).font = Font(name="Calibri", color="D0D8E4", size=10)
        ws3.cell(row=ri, column=2, value=row["COUNT"]).font = Font(name="Calibri", color="D0D8E4", size=10)
        pct = ws3.cell(row=ri, column=3, value=round(row["COUNT"] / total * 100, 1))
        pct.font = Font(name="Calibri", color="D0D8E4", size=10)
        pct.number_format = "0.0%"
        for ci in (1, 2, 3):
            ws3.cell(row=ri, column=ci).fill = PatternFill("solid", fgColor="0D1B2A")
            ws3.cell(row=ri, column=ci).border = _thin_border()

    for i, w in enumerate([22, 60, 12], 1):
        ws3.column_dimensions[get_column_letter(i)].width = w

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf.getvalue()


def export_to_csv(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")
