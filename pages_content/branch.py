"""Page 3 — Branch.

Physical environment & facility quality of the branches and how they compare with
the competitor — which branch is in trouble, and on which physical aspect.
"""

import streamlit as st

from components.cards import comparison_card, metric_card
from components.theme import ICON, mi, load_icon_font
from utils import transforms as T
from utils import charts
from utils import labels as L
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

    dig_cols = group_columns(df, DIGITAL_PREFIX)
    dig = T.aggregate_series(df[dig_cols].stack(), mode) if dig_cols else None

    wins = int((paired["gap"] > 0).sum()) if not paired.empty else 0
    total = len(paired)
    unit = T.metric_suffix(mode)

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        comparison_card(mi("apartment", ICON["dark"], 16) + "Branch Facility (XYZ)",
                        fac_xyz, fac_comp, unit=unit, accent=ICON["dark"])
    with k2:
        metric_card(mi("store", ICON["mid"], 16) + "Branches Covered", f"{n_branches}",
                    sub_text="distinct branches", accent=ICON["mid"])
    with k3:
        val = f"{dig}{unit}" if dig is not None else "-"
        metric_card(mi("devices", ICON["teal"], 16) + "Digitalization", val,
                    sub_text="avg. perception score", accent=ICON["teal"])
    with k4:
        metric_card(mi("emoji_events", ICON["soft"], 16) + "Facility Wins", f"{wins} / {total}",
                    sub_text="attributes ahead of competitor", accent=ICON["soft"])


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
    caption(box, "Showing the 8 largest advantages and 8 largest shortfalls.")


def render_heatmap(df, labels, mode):
    box = chart_card("Branch × Facility Heatmap", "Bank XYZ score per branch (dark = stronger)",
                     icon=("grid_view", "mid", 18))
    from utils.data_loader import clean_label
    cols = group_columns(df, BRANCH_PREFIX)
    xyz_cols = [
        c for c in cols
        if T._benchmark_side(labels.get(c, "")) == "XYZ"
        and not T._is_overall(clean_label(labels.get(c, "")))
    ]
    matrix = T.branch_attribute_matrix(df, xyz_cols, labels, mode=mode)
    if matrix.empty:
        empty_state(box, "Not enough per-branch responses for a heatmap."); return
    matrix.index = [translate(i) for i in matrix.index]
    plot(box, charts.heatmap(matrix, mode=mode))
    caption(box, "Branches with at least 5 responses; the 15 largest branches are shown.")


def render_digitalization(df, labels):
    box = chart_card("Branch Digitalization Perception", "Likert composition (Top-2 / Middle / Bottom-2 box)",
                     icon=("devices", "dark", 18))
    cols = group_columns(df, DIGITAL_PREFIX)
    comp = translate_df(T.likert_composition(df, cols, labels))
    if comp.empty:
        empty_state(box); return
    plot(box, charts.stacked_likert(comp))


def render_electronic(df, labels, mode):
    box = chart_card("Electronic Facilities", "Availability & function of in-branch devices (Bank XYZ)",
                     icon=("smart_display", "soft", 18))
    scores = translate_df(T.get_single_scores(df, ELECTRONIC_PREFIX, labels, mode, drop_overall=True))
    if scores.empty:
        empty_state(box); return
    plot(box, charts.single_bar(scores, mode=mode, top_n=12))


def render_branch(df, labels, mode):
    load_icon_font()
    page_header("Branch", "Physical environment and facility quality across Bank XYZ branches vs the competitor")
    render_kpis(df, labels, mode)

    spacer(28)
    render_ranking(df, labels, mode)

    spacer()
    c1, c2 = st.columns([1.1, 1])
    with c1:
        render_heatmap(df, labels, mode)
    with c2:
        render_gap(df, labels, mode)

    spacer()
    c3, c4 = st.columns([1, 1])
    with c3:
        render_digitalization(df, labels)
    with c4:
        render_electronic(df, labels, mode)
