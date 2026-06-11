"""Page 1 — Overview.

Executive summary of Bank XYZ vs Competitor on outcome KPIs in one screen, plus a
branch-level map (click a branch to see its NPS and CSI).
"""

import streamlit as st

from components.cards import kpi_card, comparison_card
from components.theme import ICON, mi, load_icon_font
from utils import transforms as T
from utils.labels import TOUCHPOINTS
from utils import geo
from pages_content._common import page_header, spacer, caption, empty_state


def render_kpis(df, mode, overall):
    csi_xyz = T.csat(df, "E1A_num", mode)
    csi_comp = T.csat(df, "E1B_num", mode)
    nps_xyz = T.nps(df["G1A_num"]) if "G1A_num" in df.columns else None
    nps_comp = T.nps(df["G1C_num"]) if "G1C_num" in df.columns else None
    ret_xyz = T.aggregate_series(df["F1A_num"], mode) if "F1A_num" in df.columns else None
    ret_comp = T.aggregate_series(df["F1B_num"], mode) if "F1B_num" in df.columns else None
    unit = T.metric_suffix(mode)

    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        kpi_card("groups", "Total Respondents", f"{len(df):,}",
                 sub_text="survey participants", accent=ICON["dark"])
    with k2:
        comparison_card("sentiment_satisfied", "CSI (Bank XYZ)", csi_xyz, csi_comp,
                        unit=unit, accent=ICON["mid"])
    with k3:
        comparison_card("thumb_up", "NPS (Bank XYZ)", nps_xyz, nps_comp, unit="", accent=ICON["darkest"])
    with k4:
        comparison_card("loyalty", "Retention (Bank XYZ)", ret_xyz, ret_comp, unit=unit, accent=ICON["teal"])
    with k5:
        paired = overall.dropna(subset=["gap"])
        wins = int((paired["gap"] > 0).sum()) if not paired.empty else 0
        kpi_card("emoji_events", "Touchpoints Won", f"{wins} / {len(paired)}",
                 sub_text="ahead of competitor", accent=ICON["soft"])


def render_map(df, labels, mode):
    box = st.container(border=True)
    box.markdown(
        '<div class="chart-title">' + mi("map", ICON["dark"], 18) +
        "Branch Map — NPS &amp; CSI</div>", unsafe_allow_html=True)
    box.markdown(
        '<div class="chart-subtitle">Each marker is a branch (colour = NPS). Click a marker for its scores.</div>',
        unsafe_allow_html=True)

    try:
        import folium
        import branca.colormap as cm
        from streamlit_folium import st_folium
    except Exception:
        box.info("Install `folium` and `streamlit-folium` to view the interactive branch map.")
        return

    table = T.branch_metric_table(df, labels, mode, min_n=1)
    if table.empty:
        empty_state(box); return

    unit = T.metric_suffix(mode)
    points = []
    for _, r in table.iterrows():
        coord = geo.branch_coord(r["branch"], r["city"])
        if coord is None or r["NPS"] is None:
            continue
        points.append((coord, r))

    if not points:
        empty_state(box, "No mappable branches for the current filters."); return

    nps_vals = [r["NPS"] for _, r in points]
    cmap = cm.LinearColormap(
        colors=["#BDD8E9", "#7BBDE8", "#49769F", "#0A4174", "#001D39"],
        vmin=min(nps_vals), vmax=max(nps_vals), caption="NPS",
    )

    m = folium.Map(location=list(geo.MAP_CENTER), zoom_start=geo.MAP_ZOOM,
                   tiles="cartodbpositron", control_scale=False)

    for (lat, lon), r in points:
        csi = f"{r['CSI']}{unit}" if r["CSI"] is not None else "–"
        html = (
            f"<div style='font-family:inherit;font-size:12px;'>"
            f"<b>{r['branch']}</b><br>{r['city']}, {r['province']}<br>"
            f"<span style='color:#0A4174;font-weight:700;'>NPS: {r['NPS']}</span><br>"
            f"<span style='color:#0f766e;font-weight:700;'>CSI: {csi}</span><br>"
            f"<span style='color:#64748b;'>n = {r['n']}</span></div>"
        )
        folium.CircleMarker(
            location=[lat, lon], radius=6, color="white", weight=1,
            fill=True, fill_color=cmap(r["NPS"]), fill_opacity=0.92,
            tooltip=r["branch"], popup=folium.Popup(html, max_width=240),
        ).add_to(m)

    cmap.add_to(m)
    with box:
        st_folium(m, height=470, use_container_width=True, returned_objects=[])
    caption(box, f"{len(points)} branches mapped at city level. Marker colour scales with branch NPS.")


def render_insights(df, overall):
    nps_xyz = T.nps(df["G1A_num"]) if "G1A_num" in df.columns else None
    nps_comp = T.nps(df["G1C_num"]) if "G1C_num" in df.columns else None
    paired = overall.dropna(subset=["gap"])
    if not paired.empty:
        best = paired.loc[paired["gap"].idxmax()]
        worst = paired.loc[paired["gap"].idxmin()]
        best_txt = f"<b>{best['attribute']}</b> (+{best['gap']:.2f})"
        worst_txt = f"<b>{worst['attribute']}</b> ({worst['gap']:+.2f})"
    else:
        best_txt = worst_txt = "<b>-</b>"
    nps_txt = (f"Bank XYZ NPS is <b>{nps_xyz}</b> vs competitor <b>{nps_comp}</b>."
               if nps_xyz is not None else "NPS data is unavailable.")

    st.markdown(
        f"""
    <div class="insight-box" style="min-height:auto;">
        <div class="insight-title">{mi("lightbulb", ICON["darkest"], 22)}Executive Summary</div>
        <ul style="list-style:none; padding-left:0; margin:0;
                   display:grid; grid-template-columns:repeat(2, 1fr); gap:10px 36px;">
            <li>{mi("emoji_events", ICON["dark"])}Strongest advantage: {best_txt} versus the competitor.</li>
            <li>{mi("warning", ICON["mid"])}Largest gap to close: {worst_txt}.</li>
            <li>{mi("thumb_up", ICON["darkest"])}{nps_txt}</li>
            <li>{mi("map", ICON["soft"])}Use the branch map to spot regional NPS/CSI hotspots and laggards.</li>
        </ul>
    </div>
    """,
        unsafe_allow_html=True,
    )


def render_overview(df, labels, mode):
    load_icon_font()
    page_header("Overview", "Executive snapshot of Bank XYZ customer experience versus the competitor")

    overall = T.touchpoint_overall(df, labels, TOUCHPOINTS, mode)
    render_kpis(df, mode, overall)

    # Full-width branch map across the row.
    spacer(28)
    render_map(df, labels, mode)

    # NOTE: the replacement chart requested ("ganti sama chart ini") goes here,
    # directly below the full-width map. Awaiting the chart spec/attachment.

    spacer()
    render_insights(df, overall)
