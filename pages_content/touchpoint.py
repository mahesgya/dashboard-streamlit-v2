"""Page 4 — Touchpoint.

Service-quality deep dive across the six touchpoints (Security, Teller, CS,
Customer Advisor, ATM, Electronic Facilities): selector + detail, tornado gap,
IPA quadrant, branch × touchpoint heatmap, waiting time and emotion.
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from components.cards import comparison_card, kpi_card
from components.theme import XYZ_COLOR, NEGATIVE_COLOR, ICON, mi, load_icon_font, base_layout
from utils import transforms as T
from utils import charts
from utils.transforms import group_columns
from utils.labels import translate, translate_df, TOUCHPOINTS, POSITIVE_EMOTIONS
from components.heatmap import render_score_heatmap
from pages_content._common import page_header, spacer, chart_card, plot, caption, empty_state


def _selected_scores(df, labels, mode, cfg):
    if cfg["paired"]:
        return T.get_paired_scores(df, cfg["prefix"], labels, mode), True
    return T.get_single_scores(df, cfg["prefix"], labels, mode, drop_overall=True), False


def render_kpis(df, labels, mode, cfg, name):
    scores, paired = _selected_scores(df, labels, mode, cfg)
    unit = T.metric_suffix(mode)
    k1, k2, k3, k4 = st.columns(4)

    if paired and not scores.empty:
        xyz = round(scores["xyz"].mean(), 2)
        comp = round(scores["competitor"].mean(), 2)
        wins = int((scores["gap"] > 0).sum())
        with k1:
            comparison_card("touch_app", f"{name} (XYZ)", xyz, comp, unit=unit, accent=ICON["dark"])
        with k2:
            kpi_card("emoji_events", "Attributes Won", f"{wins} / {len(scores)}",
                     sub_text="ahead of competitor", accent=ICON["mid"])
    else:
        xyz = round(scores["score"].mean(), 2) if not scores.empty else None
        with k1:
            kpi_card("touch_app", f"{name} (XYZ)", f"{xyz}{unit}" if xyz is not None else "-",
                     sub_text="mean across attributes", accent=ICON["dark"])
        with k2:
            kpi_card("list", "Attributes", f"{len(scores)}", sub_text="measured items", accent=ICON["mid"])

    nps_xyz = T.nps(df["G1A_num"]) if "G1A_num" in df.columns else None
    nps_comp = T.nps(df["G1C_num"]) if "G1C_num" in df.columns else None
    with k3:
        comparison_card("thumb_up", "Overall NPS", nps_xyz, nps_comp, unit="", accent=ICON["darkest"])
    with k4:
        comparison_card("sentiment_satisfied", "Overall CSI",
                        T.csat(df, "E1A_num", mode), T.csat(df, "E1B_num", mode),
                        unit=unit, accent=ICON["soft"])


def render_detail(df, labels, mode, cfg, name):
    box = chart_card(f"{name} — Attribute Detail", "Score per attribute", icon=("insights", "dark", 18))
    scores, paired = _selected_scores(df, labels, mode, cfg)
    scores = translate_df(scores)
    if scores.empty:
        empty_state(box); return
    if paired:
        plot(box, charts.grouped_bar(scores, mode=mode))
    else:
        plot(box, charts.single_bar(scores, mode=mode))
        caption(box, "No competitor benchmark exists for this touchpoint — Bank XYZ only.")


def render_tornado(df, labels, mode, cfg, name):
    box = chart_card(f"{name} — Gap Tornado", "Bank XYZ minus competitor per attribute",
                     icon=("swap_vert", "teal", 18))
    if not cfg["paired"]:
        empty_state(box, "Gap tornado requires a competitor benchmark (not available here)."); return
    scores = translate_df(T.get_paired_scores(df, cfg["prefix"], labels, mode))
    if scores.empty:
        empty_state(box); return
    plot(box, charts.diverging_bar(scores, mode=mode))


def render_ipa(df, labels):
    box = chart_card("Importance–Performance Analysis (Brand Image)",
                     "Importance (T_C1A) vs Bank XYZ performance (T_C1B). Dashed lines = means.",
                     icon=("scatter_plot", "darkest", 18))
    ipa = translate_df(T.ipa(df, labels))
    if ipa.empty:
        empty_state(box); return
    plot(box, charts.ipa_scatter(ipa))
    caption(box, "'Concentrate here' (high importance, low performance) = fix first.")


def render_branch_heatmap(df, labels, mode):
    box = chart_card("Branch × Touchpoint Heatmap", "Average Bank XYZ score per touchpoint, per branch",
                     icon=("grid_view", "mid", 18))
    matrix = T.branch_touchpoint_matrix(df, labels, TOUCHPOINTS, mode=mode, min_n=8, top_branches=20)
    if matrix.empty:
        empty_state(box, "Not enough per-branch responses for a heatmap."); return
    render_score_heatmap(box, matrix, mode=mode, row_header="Branch")
    caption(box, "Rows = branches (≥ 8 responses, top 20), columns = the 6 touchpoints.")


def render_waiting(df):
    box = chart_card("Waiting Time vs Tolerance", "Actual vs tolerated queue time (minutes)",
                     icon=("schedule", "dark", 18))
    rows = []
    for label, ac, tc in [("Teller", "TL5_num", "TL6_num"), ("Customer Service", "CS5_num", "CS6_num")]:
        if ac in df.columns and tc in df.columns:
            a = pd.to_numeric(df[ac], errors="coerce").mean()
            t = pd.to_numeric(df[tc], errors="coerce").mean()
            if pd.notna(a) and pd.notna(t):
                rows.append({"label": label, "actual": round(a, 1), "tolerance": round(t, 1)})
    data = pd.DataFrame(rows)
    if data.empty:
        empty_state(box); return
    plot(box, charts.dumbbell(data, height=260))
    breaches = data[data["actual"] > data["tolerance"]]["label"].tolist()
    caption(box, (f"Threshold breached at: {', '.join(breaches)}." if breaches
                  else "Actual waiting time stays within the tolerated threshold."))


def render_emotion(df, labels):
    box = chart_card("Emotional Response", "Mean score per emotion — positive (blue) vs negative (red)",
                     icon=("mood", "teal", 18))
    cols = group_columns(df, "T_I1A")
    xyz_cols = [c for c in cols if T._benchmark_side(labels.get(c, "")) == "XYZ"]
    rows = []
    for c in xyz_cols:
        emo = translate(labels.get(c, c).rsplit(" - ", 1)[0])
        score = T.aggregate_series(df[c], "Mean")
        if pd.notna(score):
            rows.append({"emotion": emo, "score": score,
                         "valence": "Positive" if emo in POSITIVE_EMOTIONS else "Negative"})
    data = pd.DataFrame(rows)
    if data.empty:
        empty_state(box); return
    data = data.sort_values("score")
    colors = [XYZ_COLOR if v == "Positive" else NEGATIVE_COLOR for v in data["valence"]]
    fig = go.Figure(go.Bar(
        y=data["emotion"], x=data["score"], orientation="h", marker_color=colors,
        text=[f"{s:.2f}" for s in data["score"]], textposition="outside", cliponaxis=False,
        hovertemplate="<b>%{y}</b><br>Mean: %{x:.2f}<extra></extra>"))
    fig = base_layout(fig, height=max(320, 22 * len(data) + 80), margin=dict(l=10, r=40, t=30, b=30))
    fig.update_xaxes(title="Mean score (1–6)", range=[0, 6.4])
    fig.update_yaxes(title=None)
    plot(box, fig)
    caption(box, "Positive emotions should run high; negative emotions should run low.")


def render_insights(df, labels, mode):
    overall = T.touchpoint_overall(df, labels, TOUCHPOINTS, mode).dropna(subset=["xyz"])
    if not overall.empty:
        best = overall.loc[overall["xyz"].idxmax()]
        worst = overall.loc[overall["xyz"].idxmin()]
        best_txt = f"<b>{best['attribute']}</b>"
        worst_txt = f"<b>{worst['attribute']}</b>"
    else:
        best_txt = worst_txt = "<b>-</b>"
    paired = overall.dropna(subset=["gap"])
    if not paired.empty:
        wgap = paired.loc[paired["gap"].idxmin()]
        gap_txt = f"<b>{wgap['attribute']}</b> ({wgap['gap']:+.2f} vs competitor)"
    else:
        gap_txt = "<b>-</b>"

    st.markdown(
        f"""
    <div class="insight-box" style="min-height:auto;">
        <div class="insight-title">{mi("lightbulb", ICON["darkest"], 22)}Key Insights</div>
        <ul style="list-style:none; padding-left:0; margin:0;
                   display:grid; grid-template-columns:repeat(2, 1fr); gap:10px 36px;">
            <li>{mi("thumb_up", ICON["dark"])}Highest-scoring touchpoint for Bank XYZ: {best_txt}.</li>
            <li>{mi("trending_down", ICON["mid"])}Lowest-scoring touchpoint: {worst_txt}.</li>
            <li>{mi("compare_arrows", ICON["teal"])}Largest competitive gap to close: {gap_txt}.</li>
            <li>{mi("scatter_plot", ICON["darkest"])}Use the IPA quadrant to prioritise high-importance, low-performance attributes.</li>
        </ul>
    </div>
    """,
        unsafe_allow_html=True,
    )


def render_touchpoint(df, labels, mode):
    load_icon_font()
    page_header("Touchpoint", "Service-quality deep dive across the six touchpoints — XYZ vs competitor")

    name = st.selectbox("Select a touchpoint", list(TOUCHPOINTS.keys()), index=0)
    cfg = TOUCHPOINTS[name]

    render_kpis(df, labels, mode, cfg, name)

    spacer(28)
    c1, c2 = st.columns([1, 1])
    with c1:
        render_detail(df, labels, mode, cfg, name)
    with c2:
        render_tornado(df, labels, mode, cfg, name)

    spacer()
    render_ipa(df, labels)

    spacer()
    render_branch_heatmap(df, labels, mode)

    spacer()
    c3, c4 = st.columns([1, 1.2])
    with c3:
        render_waiting(df)
    with c4:
        render_emotion(df, labels)

    spacer()
    render_insights(df, labels, mode)
