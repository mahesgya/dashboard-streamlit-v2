"""Thin Plotly chart factory — every chart shares the white-card XYZ theme.

Factories: grouped_bar, diverging_bar, radar, gauge, dumbbell, stacked_likert,
heatmap, single_bar. They accept tidy DataFrames produced by utils.transforms.
"""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from components.theme import (
    PALETTE,
    PALETTE_CONTINUOUS,
    XYZ_COLOR,
    COMP_COLOR,
    NEGATIVE_COLOR,
    base_layout,
)


def _val_fmt(mode):
    return "%{x:.1f}%" if mode == "Top-2-Box" else "%{x:.2f}"


# ---------------------------------------------------------------------------
# Grouped bar — Bank XYZ vs Competitor per attribute (horizontal)
# ---------------------------------------------------------------------------
def grouped_bar(scores_df, mode="Mean", height=None, sort_by="xyz", top_n=None):
    """scores_df: [attribute, xyz, competitor(, gap)] -> grouped horizontal bars."""
    df = scores_df.copy()
    if df.empty:
        return _empty_fig()

    if sort_by in df.columns:
        df = df.sort_values(sort_by, ascending=True)
    if top_n:
        df = df.tail(top_n)

    height = height or max(280, 26 * len(df) + 90)
    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            y=df["attribute"],
            x=df["competitor"],
            name="Competitor",
            orientation="h",
            marker_color=COMP_COLOR,
            hovertemplate="<b>%{y}</b><br>Competitor: " + _val_fmt(mode) + "<extra></extra>",
        )
    )
    fig.add_trace(
        go.Bar(
            y=df["attribute"],
            x=df["xyz"],
            name="Bank XYZ",
            orientation="h",
            marker_color=XYZ_COLOR,
            hovertemplate="<b>%{y}</b><br>Bank XYZ: " + _val_fmt(mode) + "<extra></extra>",
        )
    )

    fig = base_layout(fig, height=height, showlegend=True,
                      margin=dict(l=10, r=20, t=40, b=30))
    fig.update_layout(barmode="group", bargap=0.25, bargroupgap=0.05)
    fig.update_xaxes(title=None)
    return fig


# ---------------------------------------------------------------------------
# Single-series horizontal bar (no competitor)
# ---------------------------------------------------------------------------
def single_bar(scores_df, mode="Mean", height=None, top_n=None):
    df = scores_df.copy()
    if df.empty:
        return _empty_fig()
    df = df.sort_values("score", ascending=True)
    if top_n:
        df = df.tail(top_n)
    height = height or max(260, 24 * len(df) + 80)

    fig = px.bar(
        df,
        x="score",
        y="attribute",
        orientation="h",
        color="score",
        color_continuous_scale=PALETTE_CONTINUOUS,
    )
    fig.update_traces(
        hovertemplate="<b>%{y}</b><br>Bank XYZ: " + _val_fmt(mode) + "<extra></extra>",
    )
    fig = base_layout(fig, height=height, margin=dict(l=10, r=30, t=30, b=30))
    fig.update_layout(coloraxis_showscale=False)
    fig.update_xaxes(title=None)
    fig.update_yaxes(title=None)
    return fig


# ---------------------------------------------------------------------------
# Diverging / tornado bar — gap (XYZ - competitor)
# ---------------------------------------------------------------------------
def diverging_bar(scores_df, mode="Mean", height=None, top_n=None):
    """scores_df needs [attribute, gap]. Positive = XYZ ahead (blue),
    negative = XYZ behind (red)."""
    df = scores_df.copy()
    if df.empty or "gap" not in df.columns:
        return _empty_fig()

    df = df.dropna(subset=["gap"]).sort_values("gap")
    if top_n:
        # keep the most extreme gaps on both ends
        df = pd.concat([df.head(top_n), df.tail(top_n)]).drop_duplicates("attribute")
        df = df.sort_values("gap")

    height = height or max(280, 26 * len(df) + 90)
    colors = [XYZ_COLOR if g >= 0 else NEGATIVE_COLOR for g in df["gap"]]
    unit = "pp" if mode == "Top-2-Box" else ""

    fmt_gaps = [f"{g:+.2f}{unit}" for g in df["gap"]]
    fig = go.Figure(
        go.Bar(
            y=df["attribute"],
            x=df["gap"],
            orientation="h",
            marker_color=colors,
            text=fmt_gaps,
            textposition="outside",
            cliponaxis=False,
            customdata=fmt_gaps,
            hovertemplate="<b>%{y}</b><br>Gap (XYZ vs competitor): %{customdata}<extra></extra>",
        )
    )
    fig = base_layout(fig, height=height, margin=dict(l=10, r=50, t=30, b=30))
    fig.add_vline(x=0, line_width=1.5, line_color="#94a3b8")
    fig.update_xaxes(title=None)
    fig.update_yaxes(title=None)
    return fig


# ---------------------------------------------------------------------------
# Radar — overall touchpoint comparison (2 layers)
# ---------------------------------------------------------------------------
def _closed(seq):
    """Close a polar ring, converting NaN to None so gaps render cleanly."""
    out = [None if pd.isna(v) else v for v in seq]
    return out + [out[0]]


def radar(df, mode="Mean", height=430):
    """df: [attribute, xyz, competitor]. Competitor may contain NaN (no benchmark)."""
    if df.empty:
        return _empty_fig()
    cats = df["attribute"].tolist()
    cats_closed = cats + [cats[0]]

    fig = go.Figure()
    if "competitor" in df.columns and df["competitor"].notna().any():
        fig.add_trace(
            go.Scatterpolar(
                r=_closed(df["competitor"].tolist()),
                theta=cats_closed,
                name="Competitor",
                connectgaps=False,
                fill="toself",
                fillcolor="rgba(156,183,204,0.25)",
                line=dict(color=COMP_COLOR, width=2),
            )
        )
    fig.add_trace(
        go.Scatterpolar(
            r=_closed(df["xyz"].tolist()),
            theta=cats_closed,
            name="Bank XYZ",
            fill="toself",
            fillcolor="rgba(10,65,116,0.20)",
            line=dict(color=XYZ_COLOR, width=2.5),
        )
    )

    lo = float(np.nanmin([np.nanmin(df["xyz"].values), np.nanmin(df["competitor"].values)]))
    rng = [0, 100] if mode == "Top-2-Box" else [max(0, lo - 0.4), 6]
    fig.update_layout(
        height=height,
        margin=dict(l=70, r=70, t=40, b=40),
        paper_bgcolor="white",
        font=dict(color="#0f172a", size=12),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.04, xanchor="center", x=0.5),
        polar=dict(
            bgcolor="white",
            radialaxis=dict(visible=True, range=rng, gridcolor="#E2E8F0",
                            tickfont=dict(size=10, color="#64748b")),
            angularaxis=dict(gridcolor="#E2E8F0", tickfont=dict(size=11, color="#0f172a")),
        ),
    )
    return fig


# ---------------------------------------------------------------------------
# Gauge — NPS indicator
# ---------------------------------------------------------------------------
def gauge(value, reference=None, title="NPS", height=300, vrange=(-100, 100)):
    if value is None:
        return _empty_fig()
    delta = dict(reference=reference, increasing=dict(color="#16a34a"),
                 decreasing=dict(color="#dc2626")) if reference is not None else None

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number+delta" if delta else "gauge+number",
            value=value,
            delta=delta,
            number=dict(font=dict(size=40, color="#0f172a")),
            gauge=dict(
                axis=dict(range=list(vrange), tickfont=dict(size=10, color="#64748b")),
                bar=dict(color=XYZ_COLOR, thickness=0.7),
                bgcolor="white",
                borderwidth=0,
                steps=[
                    dict(range=[vrange[0], 0], color="#fde8e8"),
                    dict(range=[0, 30], color="#fef9c3"),
                    dict(range=[30, vrange[1]], color="#dcfce7"),
                ],
                threshold=dict(line=dict(color="#0f172a", width=3), thickness=0.75,
                               value=reference) if reference is not None else None,
            ),
        )
    )
    fig.update_layout(
        height=height,
        margin=dict(l=20, r=20, t=20, b=10),
        paper_bgcolor="white",
        font=dict(color="#0f172a"),
    )
    return fig


# ---------------------------------------------------------------------------
# Dumbbell — actual vs tolerance (waiting times)
# ---------------------------------------------------------------------------
def dumbbell(df, height=300):
    """df: [label, actual, tolerance] in minutes."""
    if df.empty:
        return _empty_fig()

    fig = go.Figure()
    for _, row in df.iterrows():
        breach = row["actual"] > row["tolerance"]
        fig.add_shape(
            type="line",
            x0=row["tolerance"], x1=row["actual"],
            y0=row["label"], y1=row["label"],
            line=dict(color=NEGATIVE_COLOR if breach else "#cbd5e1", width=3),
        )

    fig.add_trace(
        go.Scatter(
            x=df["tolerance"], y=df["label"], mode="markers+text",
            name="Tolerance", marker=dict(size=15, color=COMP_COLOR, line=dict(color="white", width=1.5)),
            text=[f"{v:.0f}" for v in df["tolerance"]], textposition="bottom center",
            textfont=dict(size=10, color="#64748b"),
            hovertemplate="<b>%{y}</b><br>Tolerated: %{x:.1f} min<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["actual"], y=df["label"], mode="markers+text",
            name="Actual", marker=dict(size=15, color=XYZ_COLOR, line=dict(color="white", width=1.5)),
            text=[f"{v:.0f}" for v in df["actual"]], textposition="top center",
            textfont=dict(size=10, color="#0f172a"),
            hovertemplate="<b>%{y}</b><br>Actual: %{x:.1f} min<extra></extra>",
        )
    )

    max_x = float(pd.concat([df["actual"], df["tolerance"]]).max())
    fig = base_layout(fig, height=height, showlegend=True,
                      margin=dict(l=10, r=45, t=50, b=40))
    fig.update_xaxes(title="Minutes", range=[0, max_x * 1.18] if max_x else [0, 1])
    fig.update_yaxes(title=None, automargin=True)
    fig.update_layout(yaxis=dict(range=[-0.6, len(df) - 0.4]))
    return fig


# ---------------------------------------------------------------------------
# Stacked Likert — Top/Mid/Bottom box composition
# ---------------------------------------------------------------------------
def stacked_likert(df, height=None):
    """df: [attribute, top, mid, bottom] as percentages (sum ~100)."""
    if df.empty:
        return _empty_fig()
    height = height or max(260, 40 * len(df) + 80)

    fig = go.Figure()
    fig.add_trace(go.Bar(y=df["attribute"], x=df["bottom"], name="Bottom-2 (1–2)",
                         orientation="h", marker_color="#dc6868",
                         hovertemplate="%{x:.0f}%<extra>Bottom</extra>"))
    fig.add_trace(go.Bar(y=df["attribute"], x=df["mid"], name="Middle (3–4)",
                         orientation="h", marker_color="#e2c97a",
                         hovertemplate="%{x:.0f}%<extra>Middle</extra>"))
    fig.add_trace(go.Bar(y=df["attribute"], x=df["top"], name="Top-2 (5–6)",
                         orientation="h", marker_color=XYZ_COLOR,
                         hovertemplate="%{x:.0f}%<extra>Top</extra>"))

    fig = base_layout(fig, height=height, showlegend=True,
                      margin=dict(l=10, r=20, t=40, b=30))
    fig.update_layout(barmode="stack")
    fig.update_xaxes(title=None, range=[0, 100], ticksuffix="%")
    fig.update_yaxes(title=None)
    return fig


# ---------------------------------------------------------------------------
# Heatmap — branch x attribute
# ---------------------------------------------------------------------------
def heatmap(matrix, mode="Mean", height=None):
    """matrix: DataFrame index=branch, columns=attribute, values=score."""
    if matrix.empty:
        return _empty_fig()
    height = height or max(320, 26 * len(matrix.index) + 120)

    fig = px.imshow(
        matrix,
        color_continuous_scale=PALETTE_CONTINUOUS,
        aspect="auto",
        labels=dict(color=("Top-2-Box %" if mode == "Top-2-Box" else "Mean")),
    )
    fig.update_traces(
        hovertemplate="<b>%{y}</b><br>%{x}<br>Score: %{z:.2f}<extra></extra>",
    )
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=30, b=120),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(color="#0f172a", size=11),
    )
    fig.update_xaxes(tickangle=-40, tickfont=dict(size=10))
    return fig


# ---------------------------------------------------------------------------
# IPA quadrant scatter
# ---------------------------------------------------------------------------
def ipa_scatter(df, height=460):
    """df: [attribute, importance, performance]."""
    if df.empty:
        return _empty_fig()

    imp_mean = df["importance"].mean()
    perf_mean = df["performance"].mean()

    def quadrant(r):
        if r["importance"] >= imp_mean and r["performance"] < perf_mean:
            return "Concentrate here"          # high importance, low performance
        if r["importance"] >= imp_mean and r["performance"] >= perf_mean:
            return "Keep up the good work"
        if r["importance"] < imp_mean and r["performance"] >= perf_mean:
            return "Possible overkill"
        return "Low priority"

    df = df.copy()
    df["Quadrant"] = df.apply(quadrant, axis=1)
    color_map = {
        "Concentrate here": "#dc2626",
        "Keep up the good work": "#0A4174",
        "Possible overkill": "#6EA2B3",
        "Low priority": "#94a3b8",
    }

    fig = px.scatter(
        df, x="performance", y="importance", color="Quadrant",
        color_discrete_map=color_map, hover_name="attribute",
        custom_data=["attribute"],
    )
    fig.update_traces(
        marker=dict(size=12, line=dict(color="white", width=1)),
        hovertemplate="<b>%{customdata[0]}</b><br>Performance: %{x:.2f}<br>Importance: %{y:.2f}<extra></extra>",
    )
    fig.add_vline(x=perf_mean, line_width=1, line_dash="dash", line_color="#94a3b8")
    fig.add_hline(y=imp_mean, line_width=1, line_dash="dash", line_color="#94a3b8")
    fig = base_layout(fig, height=height, showlegend=True,
                      margin=dict(l=10, r=20, t=50, b=40))
    fig.update_xaxes(title="Performance (mean)")
    fig.update_yaxes(title="Importance (mean)")
    return fig


def scorecard_styler(values, fmts=None):
    """Return a pandas Styler colouring each column as a heatmap gradient.

    `values`: DataFrame (index = row label, columns = metrics, mixed scales OK).
    `fmts`: optional {column: python-format-string}. No matplotlib dependency —
    colours come from the plotly palette.
    """
    fmts = fmts or {}

    def _col_styles(s):
        nums = pd.to_numeric(s, errors="coerce")
        mn, mx = nums.min(), nums.max()
        styles = []
        for v in nums:
            if pd.isna(v):
                styles.append("")
                continue
            norm = (v - mn) / (mx - mn) if mx > mn else 0.5
            color = px.colors.sample_colorscale(PALETTE_CONTINUOUS, [norm])[0]
            txt = "#ffffff" if norm > 0.55 else "#0f172a"
            styles.append(f"background-color:{color}; color:{txt}; font-weight:700;")
        return styles

    styler = values.style.apply(_col_styles, axis=0)
    fmt_map = {c: fmts.get(c, "{:.2f}") for c in values.columns}
    styler = styler.format({c: (lambda v, f=f: f.format(v) if pd.notna(v) else "–")
                            for c, f in fmt_map.items()})
    return styler


def _empty_fig():
    fig = go.Figure()
    fig.add_annotation(text="No data available", showarrow=False,
                       font=dict(color="#94a3b8", size=14))
    fig.update_layout(height=200, paper_bgcolor="white", plot_bgcolor="white",
                      xaxis=dict(visible=False), yaxis=dict(visible=False))
    return fig
