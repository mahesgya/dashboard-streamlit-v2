"""Page 1 — Overview.

Executive summary of Bank XYZ vs Competitor on outcome KPIs in one screen, plus a
branch-level map (click a branch to see its NPS and CSI).
"""

import pandas as pd
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


def _branch_popup_html(city, province, metric, sub):
    """HTML popup: city header + a list of every branch with its NPS and CSI."""
    rows = ""
    for _, b in sub.iterrows():
        csi = "–" if b["CSI"] is None or pd.isna(b["CSI"]) else f"{b['CSI']:g}"
        nps_v = "–" if b["NPS"] is None or pd.isna(b["NPS"]) else f"{b['NPS']:g}"
        rows += (
            f"<tr><td style='padding:2px 8px 2px 0;'>{b['branch']}</td>"
            f"<td style='padding:2px 8px;text-align:right;color:#0A4174;font-weight:700;'>{nps_v}</td>"
            f"<td style='padding:2px 0;text-align:right;color:#0f766e;font-weight:700;'>{csi}</td></tr>"
        )
    return (
        f"<div style='font-family:inherit;font-size:12px;max-height:240px;overflow:auto;'>"
        f"<div style='font-weight:800;font-size:13px;margin-bottom:2px;'>{city}</div>"
        f"<div style='color:#64748b;margin-bottom:6px;'>{province} · avg {metric}</div>"
        f"<table style='border-collapse:collapse;'>"
        f"<tr style='border-bottom:1px solid #e5e7eb;color:#64748b;'>"
        f"<th style='text-align:left;padding-right:8px;'>Branch</th>"
        f"<th style='text-align:right;padding:0 8px;'>NPS</th>"
        f"<th style='text-align:right;'>CSI</th></tr>{rows}</table></div>"
    )


def render_map(df, labels, mode):
    box = st.container(border=True)
    box.markdown(
        '<div class="chart-title">' + mi("map", ICON["dark"], 18) +
        "Regional Map — NPS &amp; CSI by City/Regency</div>", unsafe_allow_html=True)

    # Choose which metric colours the regions.
    color_by = box.radio("Colour regions by", ["NPS", "CSI"], horizontal=True,
                         key="map_color_by", label_visibility="collapsed")
    box.markdown(
        f'<div class="chart-subtitle">Each region (kabupaten/kota) is shaded by its average '
        f'<b>{color_by}</b>. Click a region to list all its branches with NPS &amp; CSI.</div>',
        unsafe_allow_html=True)

    try:
        import folium
        import branca.colormap as cm
        from streamlit_folium import st_folium
    except Exception:
        box.info("Install `folium` and `streamlit-folium` to view the interactive map.")
        return

    city_tbl = T.city_metric_table(df, labels, mode)
    branch_tbl = T.branch_metric_table(df, labels, mode, min_n=1)
    if city_tbl.empty:
        empty_state(box); return

    unit = T.metric_suffix(mode) if color_by == "CSI" else ""
    values = {r["city"]: r[color_by] for _, r in city_tbl.iterrows() if r[color_by] is not None and pd.notna(r[color_by])}
    if not values:
        empty_state(box, "No regional data for the current filters."); return

    cmap = cm.LinearColormap(
        colors=["#BDD8E9", "#7BBDE8", "#49769F", "#0A4174", "#001D39"],
        vmin=min(values.values()), vmax=max(values.values()),
        caption=f"Average {color_by}{(' ' + unit) if unit else ''}",
    )

    geojson = geo.load_kabkota_geojson()
    present = set(df["KABKOTA"].dropna().astype(str).unique()) if "KABKOTA" in df.columns else set()
    feats = [f for f in geojson["features"] if f["properties"]["KABKOTA"] in present] or geojson["features"]

    m = folium.Map(location=list(geo.MAP_CENTER), zoom_start=geo.MAP_ZOOM,
                   tiles="cartodbpositron", control_scale=False)

    info = {r["city"]: r for _, r in city_tbl.iterrows()}
    for feat in feats:
        city = feat["properties"]["KABKOTA"]
        val = values.get(city)
        meta = info.get(city)
        if meta is not None:
            metric_txt = (f"NPS {meta['NPS']:g}" if color_by == "NPS"
                          else f"CSI {meta['CSI']:g}{unit}") if val is not None else "no data"
            sub = branch_tbl[branch_tbl["city"] == city] if not branch_tbl.empty else branch_tbl
            popup = folium.Popup(_branch_popup_html(city, meta["province"], metric_txt, sub), max_width=320)
            tip = f"{city}: {metric_txt} ({meta['n']} resp.)"
        else:
            popup, tip = None, city

        def style(_feature, v=val):
            return {
                "fillColor": cmap(v) if v is not None else "#eef2f7",
                "color": "white", "weight": 1,
                "fillOpacity": 0.85 if v is not None else 0.4,
            }

        folium.GeoJson(
            feat,
            style_function=style,
            highlight_function=lambda x: {"weight": 2.5, "color": "#0A4174", "fillOpacity": 0.95},
            tooltip=tip, popup=popup,
        ).add_to(m)

    cmap.add_to(m)
    with box:
        st_folium(m, height=480, use_container_width=True, returned_objects=[])
    caption(box, f"{len(values)} regions shaded by average {color_by}. Grey = no data after filters.")


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
