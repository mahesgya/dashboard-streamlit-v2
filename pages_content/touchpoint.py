"""Page 4 — Touchpoint.

Dissects service quality per touchpoint (Security, Teller, CS, Customer Advisor,
ATM, Electronic Facilities) to find the touchpoints that lift or sink satisfaction.
The most drill-down page: selector + detail, tornado gap, IPA quadrant, waiting
time and emotional response.
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from components.cards import comparison_card, metric_card
from components.theme import XYZ_COLOR, NEGATIVE_COLOR, ICON, mi, load_icon_font, base_layout
from utils import transforms as T
from utils import charts
from utils import labels as L
from utils.transforms import group_columns
from utils.labels import translate, translate_df, TOUCHPOINTS, POSITIVE_EMOTIONS, NEGATIVE_EMOTIONS
from pages_content._common import page_header, spacer, chart_card, plot, caption, empty_state


def _selected_scores(df, labels, mode, cfg):
    """Return (scores_df, paired_bool) for the selected touchpoint."""
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
            comparison_card(mi("touch_app", ICON["dark"], 16) + f"{name} (XYZ)",
                            xyz, comp, unit=unit, accent=ICON["dark"])
        with k2:
            metric_card(mi("emoji_events", ICON["mid"], 16) + "Attributes Won", f"{wins} / {len(scores)}",
                        sub_text="ahead of competitor", accent=ICON["mid"])
    else:
        xyz = round(scores["score"].mean(), 2) if not scores.empty else None
        with k1:
            metric_card(mi("touch_app", ICON["dark"], 16) + f"{name} (XYZ)",
                        f"{xyz}{unit}" if xyz is not None else "-",
                        sub_text="mean across attributes", accent=ICON["dark"])
        with k2:
            metric_card(mi("list", ICON["mid"], 16) + "Attributes", f"{len(scores)}",
                        sub_text="measured items", accent=ICON["mid"])

    nps_xyz = T.nps(df["G1A_num"]) if "G1A_num" in df.columns else None
    nps_comp = T.nps(df["G1C_num"]) if "G1C_num" in df.columns else None
    with k3:
        comparison_card(mi("thumb_up", ICON["darkest"], 16) + "Overall NPS", nps_xyz, nps_comp,
                        unit="", accent=ICON["darkest"])
    with k4:
        csat_xyz = T.csat(df, "E1A_num", mode)
        csat_comp = T.csat(df, "E1B_num", mode)
        comparison_card(mi("sentiment_satisfied", ICON["soft"], 16) + "Overall CSAT", csat_xyz, csat_comp,
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
        empty_state(box, "Gap tornado requires a competitor benchmark (not available here).")
        return
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
    caption(box, "Bottom-right of the 'Concentrate here' quadrant = high importance, low performance → fix first.")


def render_waiting(df):
    box = chart_card("Waiting Time vs Tolerance", "Actual vs tolerated queue time (minutes)",
                     icon=("schedule", "dark", 18))
    rows = []
    pairs = [("Teller", "TL5_num", "TL6_num"), ("Customer Service", "CS5_num", "CS6_num")]
    for label, actual_col, tol_col in pairs:
        if actual_col in df.columns and tol_col in df.columns:
            actual = pd.to_numeric(df[actual_col], errors="coerce").mean()
            tol = pd.to_numeric(df[tol_col], errors="coerce").mean()
            if pd.notna(actual) and pd.notna(tol):
                rows.append({"label": label, "actual": round(actual, 1), "tolerance": round(tol, 1)})
    data = pd.DataFrame(rows)
    if data.empty:
        empty_state(box); return
    plot(box, charts.dumbbell(data, height=260))
    breaches = data[data["actual"] > data["tolerance"]]["label"].tolist()
    if breaches:
        caption(box, f"Threshold breached at: {', '.join(breaches)} (actual exceeds tolerance).")
    else:
        caption(box, "Actual waiting time stays within the tolerated threshold at every point.")


def render_emotion(df, labels):
    box = chart_card("Emotional Response", "Mean score per emotion — positive (blue) vs negative (red)",
                     icon=("mood", "teal", 18))
    cols = group_columns(df, "T_I1A")
    xyz_cols = [c for c in cols if T._benchmark_side(labels.get(c, "")) == "XYZ"]
    rows = []
    for c in xyz_cols:
        name = translate(labels.get(c, c).rsplit(" - ", 1)[0])
        score = T.aggregate_series(df[c], "Mean")
        if pd.notna(score):
            valence = "Positive" if name in POSITIVE_EMOTIONS else "Negative"
            rows.append({"emotion": name, "score": score, "valence": valence})
    data = pd.DataFrame(rows)
    if data.empty:
        empty_state(box); return
    data = data.sort_values("score")
    colors = [XYZ_COLOR if v == "Positive" else NEGATIVE_COLOR for v in data["valence"]]
    fig = go.Figure(go.Bar(
        y=data["emotion"], x=data["score"], orientation="h", marker_color=colors,
        text=[f"{s:.2f}" for s in data["score"]], textposition="outside", cliponaxis=False,
        hovertemplate="<b>%{y}</b><br>Mean: %{x:.2f}<extra></extra>",
    ))
    fig = base_layout(fig, height=max(320, 22 * len(data) + 80), margin=dict(l=10, r=40, t=30, b=30))
    fig.update_xaxes(title="Mean score (1–6)", range=[0, 6.4])
    fig.update_yaxes(title=None)
    plot(box, fig)
    caption(box, "Positive emotions should run high; negative emotions should run low.")


def render_touchpoint(df, labels, mode):
    load_icon_font()
    page_header("Touchpoint", "Service-quality deep dive per touchpoint — XYZ vs competitor, IPA and emotion")

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
    c3, c4 = st.columns([1, 1.2])
    with c3:
        render_waiting(df)
    with c4:
        render_emotion(df, labels)
