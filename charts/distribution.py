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


def fmv_boxplot(df: pd.DataFrame) -> go.Figure:
    fig = px.box(
        df, x="ASSET TYPE", y="FAIR MARKET VALUE",
        title="FMV distribution by asset type",
        labels={"FAIR MARKET VALUE": "Fair Market Value (KES)", "ASSET TYPE": ""},
        color="ASSET TYPE",
        color_discrete_sequence=CHART_COLORS,
    )
    fig.update_xaxes(tickangle=-35)
    fig.update_traces(hovertemplate="<b>%{x}</b><br>KES %{y:,.0f}<extra></extra>")
    return _theme(fig)


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
        title=dict(text="Data completeness per column",
                   font=dict(color=PALETTE["accent"], family="Playfair Display")),
        yaxis=dict(range=[0, 105], title="Completeness (%)"),
        xaxis=dict(title=""),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans", color=PALETTE["text_primary"]),
        showlegend=False,
        margin=dict(l=10, r=10, t=50, b=80),
    )
    fig.update_xaxes(tickangle=-35, tickfont=dict(color=PALETTE["text_muted"]))
    fig.update_yaxes(tickfont=dict(color=PALETTE["text_muted"]))
    return fig


def condition_distribution(df: pd.DataFrame) -> go.Figure:
    grp = df.groupby("CONDITION").size().reset_index(name="COUNT").sort_values("COUNT", ascending=False)
    fig = px.bar(
        grp, x="CONDITION", y="COUNT",
        title="Asset count by condition",
        labels={"COUNT": "Number of assets", "CONDITION": ""},
        color="COUNT",
        color_continuous_scale=[[0, "#243550"], [1, "#C9A84C"]],
    )
    fig.update_xaxes(tickangle=-35)
    fig.update_traces(hovertemplate="<b>%{x}</b><br>Count: %{y}<extra></extra>")
    fig.update_layout(coloraxis_showscale=False)
    return _theme(fig)
