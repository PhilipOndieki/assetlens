import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from styles import PALETTE, CHART_COLORS


def _theme(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=PALETTE["text_primary"], family="DM Sans"),
        hoverlabel=dict(bgcolor=PALETTE["bg_card"], bordercolor=PALETTE["accent"],
                        font=dict(color=PALETTE["text_primary"])),
        margin=dict(l=10, r=10, t=50, b=10),
        title_font=dict(color=PALETTE["accent"], size=15, family="Playfair Display"),
    )
    fig.update_xaxes(gridcolor="rgba(201,168,76,0.15)", linecolor=PALETTE["border"],
                     tickfont=dict(color=PALETTE["text_muted"]))
    fig.update_yaxes(gridcolor="rgba(201,168,76,0.15)", linecolor=PALETTE["border"],
                     tickfont=dict(color=PALETTE["text_muted"]))
    return fig


def building_asset_count(df: pd.DataFrame, campus: str) -> go.Figure:
    sub = df[df["LOCATION"] == campus]
    grp = sub.groupby("BUILDING").size().reset_index(name="COUNT").sort_values("COUNT", ascending=False)
    fig = px.bar(
        grp, x="BUILDING", y="COUNT",
        title="Asset count per building",
        labels={"COUNT": "Assets", "BUILDING": ""},
        color="COUNT",
        color_continuous_scale=[[0, "#243550"], [1, "#C9A84C"]],
    )
    fig.update_xaxes(tickangle=-35)
    fig.update_traces(hovertemplate="<b>%{x}</b><br>Assets: %{y}<extra></extra>")
    fig.update_layout(coloraxis_showscale=False)
    return _theme(fig)


def building_fmv(df: pd.DataFrame, campus: str) -> go.Figure:
    sub = df[df["LOCATION"] == campus]
    grp = sub.groupby(["BUILDING", "ASSET TYPE"])["FAIR MARKET VALUE"].sum().reset_index()
    fig = px.bar(
        grp, x="BUILDING", y="FAIR MARKET VALUE", color="ASSET TYPE",
        title="Total FMV by building",
        labels={"FAIR MARKET VALUE": "Total FMV (KES)", "BUILDING": ""},
        color_discrete_sequence=CHART_COLORS,
    )
    fig.update_xaxes(tickangle=-35)
    fig.update_traces(hovertemplate="<b>%{x}</b><br>%{fullData.name}<br>KES %{y:,.0f}<extra></extra>")
    return _theme(fig)


def condition_heatmap(df: pd.DataFrame, campus: str) -> go.Figure:
    sub = df[df["LOCATION"] == campus]
    conditions = sorted(sub["CONDITION"].dropna().unique().tolist())
    pivot = sub.groupby(["BUILDING", "CONDITION"]).size().unstack(fill_value=0)
    for c in conditions:
        if c not in pivot.columns:
            pivot[c] = 0
    pivot = pivot[conditions]

    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns.tolist(),
        y=pivot.index.tolist(),
        colorscale=[[0.0, "#162236"], [0.5, "#9E7B30"], [1.0, "#C9A84C"]],
        hovertemplate="Building: %{y}<br>Condition: %{x}<br>Count: %{z}<extra></extra>",
        colorbar=dict(tickfont=dict(color=PALETTE["text_muted"]),
                      title=dict(text="Count", font=dict(color=PALETTE["text_muted"]))),
    ))
    fig.update_layout(
        title=dict(text="Condition heatmap — buildings × condition",
                   font=dict(color=PALETTE["accent"], family="Playfair Display")),
        xaxis=dict(tickangle=-35, tickfont=dict(color=PALETTE["text_muted"])),
        yaxis=dict(tickfont=dict(color=PALETTE["text_muted"]), autorange="reversed"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans", color=PALETTE["text_primary"]),
        margin=dict(l=10, r=10, t=50, b=10),
    )
    return fig
