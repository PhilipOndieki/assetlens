import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from styles import PALETTE, CHART_COLORS


def _theme(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=PALETTE["text_primary"], family="DM Sans"),
        legend=dict(
            bgcolor="rgba(22,34,54,0.85)",
            bordercolor=PALETTE["border"],
            borderwidth=1,
            font=dict(color=PALETTE["text_primary"], size=11),
        ),
        hoverlabel=dict(
            bgcolor=PALETTE["bg_card"],
            bordercolor=PALETTE["accent"],
            font=dict(color=PALETTE["text_primary"], family="DM Sans"),
        ),
        margin=dict(l=10, r=10, t=50, b=10),
        title_font=dict(color=PALETTE["accent"], size=15, family="Playfair Display"),
    )
    fig.update_xaxes(
        gridcolor="rgba(201,168,76,0.15)",
        linecolor=PALETTE["border"],
        tickfont=dict(color=PALETTE["text_muted"]),
        title_font=dict(color=PALETTE["text_muted"]),
    )
    fig.update_yaxes(
        gridcolor="rgba(201,168,76,0.15)",
        linecolor=PALETTE["border"],
        tickfont=dict(color=PALETTE["text_muted"]),
        title_font=dict(color=PALETTE["text_muted"]),
    )
    return fig


def asset_count_by_campus(df: pd.DataFrame) -> go.Figure:
    grp = df.groupby(["LOCATION", "ASSET TYPE"]).size().reset_index(name="COUNT")
    fig = px.bar(
        grp, x="LOCATION", y="COUNT", color="ASSET TYPE",
        title="Asset count by campus",
        labels={"COUNT": "Number of assets", "LOCATION": ""},
        color_discrete_sequence=CHART_COLORS,
    )
    fig.update_xaxes(tickangle=-35)
    fig.update_traces(hovertemplate="<b>%{x}</b><br>%{fullData.name}<br>Count: %{y}<extra></extra>")
    return _theme(fig)


def asset_type_donut(df: pd.DataFrame) -> go.Figure:
    grp = df.groupby("ASSET TYPE").size().reset_index(name="COUNT")
    fig = px.pie(
        grp, values="COUNT", names="ASSET TYPE",
        title="Asset type distribution",
        hole=0.52,
        color_discrete_sequence=CHART_COLORS,
    )
    fig.update_traces(
        textfont_size=11,
        hovertemplate="<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>",
    )
    return _theme(fig)


def top_buildings_by_fmv(df: pd.DataFrame, n: int = 10) -> go.Figure:
    grp = df.groupby("BUILDING")["FAIR MARKET VALUE"].sum().reset_index()
    grp = grp.nlargest(n, "FAIR MARKET VALUE")
    fig = px.bar(
        grp, x="BUILDING", y="FAIR MARKET VALUE",
        title=f"Top {n} buildings by fair market value (KES)",
        labels={"FAIR MARKET VALUE": "Total FMV (KES)", "BUILDING": ""},
        color="FAIR MARKET VALUE",
        color_continuous_scale=[[0, "#243550"], [0.5, "#9E7B30"], [1.0, "#C9A84C"]],
    )
    fig.update_xaxes(tickangle=-35)
    fig.update_traces(hovertemplate="<b>%{x}</b><br>KES %{y:,.0f}<extra></extra>")
    fig.update_layout(coloraxis_showscale=False)
    return _theme(fig)


def fmv_treemap(df: pd.DataFrame) -> go.Figure:
    grp = df.groupby(["LOCATION", "BUILDING", "ASSET TYPE"])["FAIR MARKET VALUE"].sum().reset_index()
    grp = grp[grp["FAIR MARKET VALUE"] > 0]
    fig = px.treemap(
        grp,
        path=[px.Constant("JKUAT"), "LOCATION", "BUILDING", "ASSET TYPE"],
        values="FAIR MARKET VALUE",
        title="FMV concentration — campus › building › asset type",
        color="FAIR MARKET VALUE",
        color_continuous_scale=[[0, "#162236"], [0.5, "#9E7B30"], [1.0, "#C9A84C"]],
    )
    fig.update_traces(
        hovertemplate="<b>%{label}</b><br>FMV: KES %{value:,.0f}<extra></extra>",
        textfont=dict(family="DM Sans", size=12),
    )
    fig.update_layout(coloraxis_showscale=False, margin=dict(l=10, r=10, t=50, b=10))
    return _theme(fig)
