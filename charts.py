import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from styles import PALETTE, CHART_COLORS, PLOTLY_TEMPLATE


def _apply_theme(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=PALETTE["text_primary"], family="DM Sans"),
        legend=dict(
            bgcolor="rgba(22,34,54,0.85)",
            bordercolor=PALETTE["border"],
            borderwidth=1,
            font=dict(color=PALETTE["text_primary"], size=11),
            orientation="v",
            xanchor="right",
            x=1,
            yanchor="top",
            y=1,
        ),
        hoverlabel=dict(
            bgcolor=PALETTE["bg_card"],
            bordercolor=PALETTE["accent"],
            font=dict(color=PALETTE["text_primary"], family="DM Sans"),
        ),
        margin=dict(l=10, r=10, t=50, b=10),
    )
    fig.update_xaxes(
        gridcolor="rgba(201,168,76,0.15)",
        linecolor=PALETTE["border"],
        tickfont=dict(color=PALETTE["text_muted"]),
        title_font=dict(color=PALETTE["text_muted"]),
        zerolinecolor=PALETTE["border"],
    )
    fig.update_yaxes(
        gridcolor="rgba(201,168,76,0.15)",
        linecolor=PALETTE["border"],
        tickfont=dict(color=PALETTE["text_muted"]),
        title_font=dict(color=PALETTE["text_muted"]),
        zerolinecolor=PALETTE["border"],
    )
    return fig


def fmt_kes(val):
    try:
        return f"KES {val:,.0f}"
    except Exception:
        return str(val)


def asset_count_by_campus_stacked(df: pd.DataFrame) -> go.Figure:
    grp = df.groupby(["LOCATION", "ASSET TYPE"]).size().reset_index(name="COUNT")
    fig = px.bar(
        grp, x="COUNT", y="LOCATION", color="ASSET TYPE",
        orientation="h",
        title="Asset Count by Campus — Stacked by Asset Type",
        labels={"COUNT": "Number of Assets", "LOCATION": "Campus"},
        color_discrete_sequence=CHART_COLORS,
    )
    fig.update_traces(hovertemplate="<b>%{y}</b><br>%{fullData.name}<br>Count: %{x}<extra></extra>")
    return _apply_theme(fig)


def asset_type_donut(df: pd.DataFrame) -> go.Figure:
    grp = df.groupby("ASSET TYPE").size().reset_index(name="COUNT")
    fig = px.pie(
        grp, values="COUNT", names="ASSET TYPE",
        title="Asset Type Distribution — All Campuses",
        hole=0.52,
        color_discrete_sequence=CHART_COLORS,
    )
    fig.update_traces(
        textfont_size=12,
        hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Share: %{percent}<extra></extra>",
    )
    fig.update_layout(showlegend=True)
    return _apply_theme(fig)


def top_buildings_by_fmv(df: pd.DataFrame, n: int = 10) -> go.Figure:
    grp = df.groupby("BUILDING")["FAIR MARKET VALUE"].sum().reset_index()
    grp = grp.nlargest(n, "FAIR MARKET VALUE")
    grp["FMV_FMT"] = grp["FAIR MARKET VALUE"].apply(fmt_kes)
    fig = px.bar(
        grp, x="FAIR MARKET VALUE", y="BUILDING",
        orientation="h",
        title=f"Top {n} Buildings by Total Fair Market Value (KES)",
        labels={"FAIR MARKET VALUE": "Total FMV (KES)", "BUILDING": ""},
        color="FAIR MARKET VALUE",
        color_continuous_scale=[[0, "#243550"], [0.5, "#9E7B30"], [1.0, "#C9A84C"]],
    )
    fig.update_traces(
        hovertemplate="<b>%{y}</b><br>Total FMV: KES %{x:,.0f}<extra></extra>",
    )
    fig.update_layout(coloraxis_showscale=False, yaxis=dict(autorange="reversed"))
    return _apply_theme(fig)


def fmv_treemap(df: pd.DataFrame) -> go.Figure:
    grp = df.groupby(["LOCATION", "BUILDING", "ASSET TYPE"])["FAIR MARKET VALUE"].sum().reset_index()
    grp = grp[grp["FAIR MARKET VALUE"] > 0]
    fig = px.treemap(
        grp,
        path=[px.Constant("JKUAT"), "LOCATION", "BUILDING", "ASSET TYPE"],
        values="FAIR MARKET VALUE",
        title="FMV Concentration — Campus › Building › Asset Type",
        color="FAIR MARKET VALUE",
        color_continuous_scale=[[0, "#162236"], [0.5, "#9E7B30"], [1.0, "#C9A84C"]],
    )
    fig.update_traces(
        hovertemplate="<b>%{label}</b><br>FMV: KES %{value:,.0f}<extra></extra>",
        textfont=dict(family="DM Sans", size=12),
    )
    fig.update_layout(margin=dict(l=10, r=10, t=50, b=10), coloraxis_showscale=False)
    return _apply_theme(fig)


def campus_building_count_bar(df: pd.DataFrame, campus: str) -> go.Figure:
    sub = df[df["LOCATION"] == campus]
    grp = sub.groupby("BUILDING").size().reset_index(name="COUNT").sort_values("COUNT", ascending=True)
    fig = px.bar(
        grp, x="COUNT", y="BUILDING", orientation="h",
        title=f"Asset Count per Building",
        labels={"COUNT": "Assets", "BUILDING": ""},
        color="COUNT",
        color_continuous_scale=[[0, "#243550"], [1, "#C9A84C"]],
    )
    fig.update_traces(hovertemplate="<b>%{y}</b><br>Assets: %{x}<extra></extra>")
    fig.update_layout(coloraxis_showscale=False, yaxis=dict(autorange="reversed"))
    return _apply_theme(fig)


def campus_fmv_stacked_bar(df: pd.DataFrame, campus: str) -> go.Figure:
    sub = df[df["LOCATION"] == campus]
    grp = sub.groupby(["BUILDING", "ASSET TYPE"])["FAIR MARKET VALUE"].sum().reset_index()
    fig = px.bar(
        grp, x="FAIR MARKET VALUE", y="BUILDING", color="ASSET TYPE",
        orientation="h",
        title=f"Total FMV by Building — Stacked by Asset Type",
        labels={"FAIR MARKET VALUE": "Total FMV (KES)", "BUILDING": ""},
        color_discrete_sequence=CHART_COLORS,
    )
    fig.update_traces(hovertemplate="<b>%{y}</b><br>%{fullData.name}<br>KES %{x:,.0f}<extra></extra>")
    fig.update_layout(yaxis=dict(autorange="reversed"))
    return _apply_theme(fig)


def condition_heatmap(df: pd.DataFrame, campus: str) -> go.Figure:
    sub = df[df["LOCATION"] == campus]
    pivot = sub.groupby(["BUILDING", "CONDITION"]).size().unstack(fill_value=0)
    conditions = ["Good", "Fair", "Poor", "Condemned"]
    for c in conditions:
        if c not in pivot.columns:
            pivot[c] = 0
    pivot = pivot[conditions]

    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns.tolist(),
        y=pivot.index.tolist(),
        colorscale=[
            [0.0, "#162236"],
            [0.25, "#243550"],
            [0.5, "#9E7B30"],
            [1.0, "#C9A84C"],
        ],
        hoverongaps=False,
        hovertemplate="Building: %{y}<br>Condition: %{x}<br>Count: %{z}<extra></extra>",
        showscale=True,
        colorbar=dict(
            tickfont=dict(color=PALETTE["text_muted"]),
            title=dict(text="Count", font=dict(color=PALETTE["text_muted"])),
            bgcolor="rgba(0,0,0,0)",
        ),
    ))
    fig.update_layout(
        title=dict(text="Condition Heatmap — Buildings × Condition", font=dict(color=PALETTE["accent"])),
        xaxis=dict(title="Condition", tickfont=dict(color=PALETTE["text_muted"])),
        yaxis=dict(title="", tickfont=dict(color=PALETTE["text_muted"]), autorange="reversed"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans", color=PALETTE["text_primary"]),
        margin=dict(l=10, r=10, t=50, b=10),
    )
    return fig


def fmv_boxplot(df: pd.DataFrame) -> go.Figure:
    fig = px.box(
        df, x="ASSET TYPE", y="FAIR MARKET VALUE",
        title="FMV Distribution by Asset Type",
        labels={"FAIR MARKET VALUE": "Fair Market Value (KES)", "ASSET TYPE": ""},
        color="ASSET TYPE",
        color_discrete_sequence=CHART_COLORS,
    )
    fig.update_traces(hovertemplate="<b>%{x}</b><br>KES %{y:,.0f}<extra></extra>")
    return _apply_theme(fig)


def completeness_bar(completeness_df: pd.DataFrame) -> go.Figure:
    colors = [
        PALETTE["danger"] if p < 80 else PALETTE["accent"]
        for p in completeness_df["Completeness (%)"]
    ]
    fig = go.Figure(go.Bar(
        x=completeness_df["Column"],
        y=completeness_df["Completeness (%)"],
        marker_color=colors,
        hovertemplate="<b>%{x}</b><br>Completeness: %{y:.1f}%<extra></extra>",
    ))
    fig.add_hline(
        y=80, line_dash="dot", line_color=PALETTE["warning"],
        annotation_text="80% threshold",
        annotation_font_color=PALETTE["warning"],
    )
    fig.update_layout(
        title=dict(text="Data Completeness per Column", font=dict(color=PALETTE["accent"])),
        yaxis=dict(range=[0, 105], title="Completeness (%)"),
        xaxis=dict(title=""),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans", color=PALETTE["text_primary"]),
        showlegend=False,
        margin=dict(l=10, r=10, t=50, b=80),
    )
    fig.update_xaxes(tickangle=-35, gridcolor="rgba(201,168,76,0.15)", tickfont=dict(color=PALETTE["text_muted"]))
    fig.update_yaxes(gridcolor="rgba(201,168,76,0.15)", tickfont=dict(color=PALETTE["text_muted"]))
    return fig
