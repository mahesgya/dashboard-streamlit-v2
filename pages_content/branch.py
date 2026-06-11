"""Page 3 — Branch.

Physical environment & facility quality across branches vs the competitor, plus a
per-branch outcome scorecard (NPS & CSI) — which branch is in trouble, and where.
"""

import pandas as pd
import streamlit as st

from components.cards import comparison_card, kpi_card
from components.theme import ICON, mi, load_icon_font
from utils import transforms as T
from utils import charts
from utils.data_loader import clean_label
from utils.transforms import group_columns
from utils.labels import translate, translate_df
from pages_content._common import page_header, spacer, chart_card, plot, caption, empty_state

BRANCH_PREFIX = "T_KC2"
DIGITAL_PREFIX = "T_J1"
ELECTRONIC_PREFIX = "T_SL1"


def render_kpis(df, labels, mode):
    paired = T.get_paired_scores(df, BRANCH_PREFIX, labels, mode)
    fac_xyz = round(paired["xyz"].mean(), 2) if not paired.empty else None
    fac_comp = round(paired["competitor"].mean(), 2) if not paired.empty else None
    n_branches = df["CABANG"].dropna().nunique() if "CABANG" in df.columns else 0
    nps_val = T.nps(df["G1A_num"]) if "G1A_num" in df.columns else None
    csi_xyz = T.csat(df, "E1A_num", mode)
    csi_comp = T.csat(df, "E1B_num", mode)
    unit = T.metric_suffix(mode)

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        comparison_card("apartment", "Branch Facility (XYZ)", fac_xyz, fac_comp, unit=unit, accent=ICON["dark"])
    with k2:
        kpi_card("store", "Branches Covered", f"{n_branches}", sub_text="distinct branches", accent=ICON["mid"])
    with k3:
        kpi_card("thumb_up", "Avg. NPS", f"{nps_val}" if nps_val is not None else "-",
                 sub_text="across selected branches", accent=ICON["darkest"])
    with k4:
        comparison_card("sentiment_satisfied", "CSI (Bank XYZ)", csi_xyz, csi_comp, unit=unit, accent=ICON["teal"])


def render_scorecard(df, labels, mode):
    box = chart_card("Branch Scorecard — NPS, CSI & Facility",
                     "Outcome scores per branch (darker = stronger within each column)",
                     icon=("table_rows", "darkest", 18))
    table = T.branch_metric_table(df, labels, mode, min_n=8, top_branches=20)
    if table.empty:
        empty_state(box, "Not enough per-branch responses for a scorecard."); return

    table = table.sort_values("NPS", ascending=False)
    disp = table.set_index("branch")[["NPS", "CSI", "Facility", "n"]]
    metric_fmt = "{:.1f}%" if mode == "Top-2-Box" else "{:.2f}"
    fmts = {"NPS": "{:.0f}", "CSI": metric_fmt, "Facility": metric_fmt, "n": "{:.0f}"}
    styler = charts.scorecard_styler(disp, fmts=fmts)
    with box:
        st.dataframe(styler, use_container_width=True, height=min(560, 42 * len(disp) + 48))
    caption(box, "Branches with at least 8 responses; top 20 by NPS shown. Click column headers to sort.")


def render_heatmap(df, labels, mode):
    box = chart_card("Branch × Facility Heatmap", "Bank XYZ facility score per branch (dark = stronger)",
                     icon=("grid_view", "mid", 18))
    cols = [
        c for c in group_columns(df, BRANCH_PREFIX)
        if T._benchmark_side(labels.get(c, "")) == "XYZ"
        and not T._is_overall(clean_label(labels.get(c, "")))
    ]
    matrix = T.branch_attribute_matrix(df, cols, labels, mode=mode)
    if matrix.empty:
        empty_state(box, "Not enough per-branch responses for a heatmap."); return
    matrix.index = [translate(i) for i in matrix.index]
    plot(box, charts.heatmap(matrix, mode=mode))
    caption(box, "Rows = facility attributes, columns = branches (≥ 5 responses, 15 largest).")


def render_digitalization(df, labels):
    box = chart_card("Branch Digitalization Perception", "Likert composition (Top-2 / Middle / Bottom-2 box)",
                     icon=("devices", "dark", 18))
    comp = translate_df(T.likert_composition(df, group_columns(df, DIGITAL_PREFIX), labels))
    if comp.empty:
        empty_state(box); return
    plot(box, charts.stacked_likert(comp))


def render_electronic(df, labels, mode):
    box = chart_card("Electronic Facilities", "Availability & function of in-branch devices (Bank XYZ, % Top-2-Box)" if mode == "Top-2-Box" else "Availability & function of in-branch devices (Bank XYZ)",
                     icon=("smart_display", "soft", 18))
    scores = translate_df(T.get_single_scores(df, ELECTRONIC_PREFIX, labels, mode, drop_overall=True))
    if scores.empty:
        empty_state(box); return
    plot(box, charts.single_bar(scores, mode=mode, top_n=12))


def render_ranking(df, labels, mode):
    box = chart_card("Facility Attribute Ranking", "Bank XYZ vs competitor — sorted by Bank XYZ score",
                     icon=("bar_chart", "dark", 18))
    paired = translate_df(T.get_paired_scores(df, BRANCH_PREFIX, labels, mode))
    if paired.empty:
        empty_state(box); return
    plot(box, charts.grouped_bar(paired, mode=mode))


def render_gap(df, labels, mode):
    box = chart_card("Physical Aspect Gap", "Where Bank XYZ branches trail the competitor (red)",
                     icon=("compare_arrows", "teal", 18))
    paired = translate_df(T.get_paired_scores(df, BRANCH_PREFIX, labels, mode))
    if paired.empty:
        empty_state(box); return
    plot(box, charts.diverging_bar(paired, mode=mode, top_n=8))
    caption(box, "The 8 largest advantages and 8 largest shortfalls.")


def render_insights(df, labels, mode):
    table = T.branch_metric_table(df, labels, mode, min_n=8)
    paired = T.get_paired_scores(df, BRANCH_PREFIX, labels)
    if not table.empty and table["NPS"].notna().any():
        best = table.loc[table["NPS"].idxmax()]
        worst = table.loc[table["NPS"].idxmin()]
        best_txt = f"<b>{best['branch']}</b> (NPS {best['NPS']:.0f})"
        worst_txt = f"<b>{worst['branch']}</b> (NPS {worst['NPS']:.0f})"
    else:
        best_txt = worst_txt = "<b>-</b>"
    if not paired.empty:
        weak = translate(paired.loc[paired["gap"].idxmin(), "attribute"])
        strong = translate(paired.loc[paired["gap"].idxmax(), "attribute"])
    else:
        weak = strong = "-"

    st.markdown(
        f"""
    <div class="insight-box" style="min-height:auto;">
        <div class="insight-title">{mi("lightbulb", ICON["darkest"], 22)}Key Insights</div>
        <ul style="list-style:none; padding-left:0; margin:0;
                   display:grid; grid-template-columns:repeat(2, 1fr); gap:10px 36px;">
            <li>{mi("emoji_events", ICON["dark"])}Top branch by NPS: {best_txt}.</li>
            <li>{mi("warning", ICON["mid"])}Lowest branch by NPS: {worst_txt} — prioritise for review.</li>
            <li>{mi("thumb_up", ICON["teal"])}Strongest facility vs competitor: <b>{strong}</b>.</li>
            <li>{mi("trending_down", ICON["darkest"])}Weakest facility vs competitor: <b>{weak}</b>.</li>
        </ul>
    </div>
    """,
        unsafe_allow_html=True,
    )


def render_branch(df, labels, mode):
    load_icon_font()
    page_header("Branch", "Physical environment and facility quality across Bank XYZ branches vs the competitor")
    render_kpis(df, labels, mode)

    spacer(28)
    render_scorecard(df, labels, mode)

    spacer()
    render_heatmap(df, labels, mode)

    spacer()
    c1, c2 = st.columns([1, 1])
    with c1:
        render_digitalization(df, labels)
    with c2:
        render_electronic(df, labels, mode)

    # Facility attribute detail moved to the bottom (revision request).
    spacer()
    render_ranking(df, labels, mode)

    spacer()
    render_gap(df, labels, mode)

    spacer()
    render_insights(df, labels, mode)
