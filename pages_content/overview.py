"""Page 1 — Overview.

Executive summary of Bank XYZ vs Competitor on outcome KPIs in one screen:
who wins/loses, and on which touchpoint.
"""

import pandas as pd
import streamlit as st

from components.cards import metric_card, comparison_card
from components.theme import ICON, mi, load_icon_font
from utils import transforms as T
from utils.labels import DOMAINS_PAIRED
from utils import charts
from pages_content._common import page_header, spacer, chart_card, plot, caption, empty_state


def domain_overall(df, labels, mode):
    """Mean XYZ vs competitor per touchpoint domain (overall benchmark)."""
    rows = []
    for domain, prefix in DOMAINS_PAIRED.items():
        paired = T.get_paired_scores(df, prefix, labels, mode)
        if paired.empty:
            continue
        rows.append(
            {
                "attribute": domain,
                "xyz": round(paired["xyz"].mean(), 2),
                "competitor": round(paired["competitor"].mean(), 2),
                "gap": round(paired["xyz"].mean() - paired["competitor"].mean(), 2),
            }
        )
    return pd.DataFrame(rows)


def render_kpis(df, mode, overall):
    csat_xyz = T.csat(df, "E1A_num", mode)
    csat_comp = T.csat(df, "E1B_num", mode)
    nps_xyz = T.nps(df["G1A_num"]) if "G1A_num" in df.columns else None
    nps_comp = T.nps(df["G1C_num"]) if "G1C_num" in df.columns else None
    ret_xyz = T.aggregate_series(df["F1A_num"], mode) if "F1A_num" in df.columns else None
    ret_comp = T.aggregate_series(df["F1B_num"], mode) if "F1B_num" in df.columns else None

    unit = T.metric_suffix(mode)

    k1, k2, k3, k4, k5 = st.columns(5)

    with k1:
        metric_card(
            mi("groups", ICON["dark"], 16) + "Total Respondents",
            f"{len(df):,}",
            sub_text="survey participants",
            accent=ICON["dark"],
        )
    with k2:
        comparison_card(
            mi("sentiment_satisfied", ICON["mid"], 16) + "CSAT (Bank XYZ)",
            csat_xyz, csat_comp, unit=unit, accent=ICON["mid"],
        )
    with k3:
        # NPS is always the standard 0–10 score regardless of the Mean/T2B toggle.
        comparison_card(
            mi("thumb_up", ICON["darkest"], 16) + "NPS (Bank XYZ)",
            nps_xyz, nps_comp, unit="", accent=ICON["darkest"],
        )
    with k4:
        comparison_card(
            mi("loyalty", ICON["teal"], 16) + "Retention (Bank XYZ)",
            ret_xyz, ret_comp, unit=unit, accent=ICON["teal"],
        )
    with k5:
        wins = int((overall["gap"] > 0).sum()) if not overall.empty else 0
        total = len(overall)
        metric_card(
            mi("emoji_events", ICON["soft"], 16) + "Touchpoints Won",
            f"{wins} / {total}",
            sub_text="domains ahead of competitor",
            accent=ICON["soft"],
        )


def render_nps_gauge(df):
    box = chart_card(
        "Net Promoter Score",
        "Bank XYZ vs competitor benchmark (threshold marker)",
        icon=("speed", "darkest", 18),
    )
    nps_xyz = T.nps(df["G1A_num"]) if "G1A_num" in df.columns else None
    nps_comp = T.nps(df["G1C_num"]) if "G1C_num" in df.columns else None
    if nps_xyz is None:
        empty_state(box)
        return
    fig = charts.gauge(nps_xyz, reference=nps_comp, title="NPS", height=300)
    plot(box, fig)
    promoters, passives, detractors = T.nps_breakdown(df["G1A_num"])
    caption(
        box,
        f"Promoters {promoters}% · Passives {passives}% · Detractors {detractors}%. "
        f"Threshold marker = competitor NPS ({nps_comp}).",
    )


def render_radar(overall, mode):
    box = chart_card(
        "Touchpoint Overview",
        f"Overall {T.metric_axis_title(mode).lower()} — Bank XYZ vs competitor",
        icon=("radar", "dark", 18),
    )
    if overall.empty:
        empty_state(box)
        return
    plot(box, charts.radar(overall, mode=mode, height=360))


def render_gap(overall, mode):
    box = chart_card(
        "Competitive Gap by Touchpoint",
        "Bank XYZ minus competitor — blue = ahead, red = behind",
        icon=("compare_arrows", "teal", 18),
    )
    if overall.empty:
        empty_state(box)
        return
    plot(box, charts.diverging_bar(overall, mode=mode, height=340))


def render_insights(df, overall):
    nps_xyz = T.nps(df["G1A_num"]) if "G1A_num" in df.columns else None
    nps_comp = T.nps(df["G1C_num"]) if "G1C_num" in df.columns else None

    if not overall.empty:
        best = overall.loc[overall["gap"].idxmax()]
        worst = overall.loc[overall["gap"].idxmin()]
        best_txt = f"<b>{best['attribute']}</b> (+{best['gap']:.2f})"
        worst_txt = f"<b>{worst['attribute']}</b> ({worst['gap']:+.2f})"
    else:
        best_txt = worst_txt = "<b>-</b>"

    nps_txt = (
        f"Bank XYZ NPS is <b>{nps_xyz}</b> vs competitor <b>{nps_comp}</b>."
        if nps_xyz is not None else "NPS data is unavailable."
    )

    st.markdown(
        f"""
    <div class="insight-box" style="min-height:auto;">
        <div class="insight-title">{mi("lightbulb", ICON["darkest"], 22)}Executive Summary</div>
        <ul style="list-style:none; padding-left:0; margin:0;
                   display:grid; grid-template-columns:repeat(2, 1fr); gap:10px 36px;">
            <li>{mi("emoji_events", ICON["dark"])}Strongest advantage: {best_txt} versus the competitor.</li>
            <li>{mi("warning", ICON["mid"])}Largest gap to close: {worst_txt}.</li>
            <li>{mi("thumb_up", ICON["darkest"])}{nps_txt}</li>
            <li>{mi("insights", ICON["soft"])}Use the touchpoint radar to spot dimensions where Bank XYZ falls behind peers.</li>
        </ul>
    </div>
    """,
        unsafe_allow_html=True,
    )


def render_overview(df, labels, mode):
    load_icon_font()
    page_header("Overview", "Executive snapshot of Bank XYZ customer experience versus the competitor")

    overall = domain_overall(df, labels, mode)
    render_kpis(df, mode, overall)

    spacer(28)
    c1, c2 = st.columns([1, 1.25])
    with c1:
        render_nps_gauge(df)
    with c2:
        render_radar(overall, mode)

    spacer()
    render_gap(overall, mode)

    spacer()
    render_insights(df, overall)
