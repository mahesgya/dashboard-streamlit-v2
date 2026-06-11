"""Pill-style banded heatmap tables (rounded colour cells + legend).

Design only — the data fed in is unchanged. Colours use discrete bands
(green → red) as a fraction of the scale max, matching the reference legend:
≥90% dark green, ≥75% light green, ≥60% yellow, ≥45% orange, else red.
"""

import pandas as pd

DARK_GREEN = "#1a7d3f"
LIGHT_GREEN = "#6cbf86"
YELLOW = "#f0cf64"
ORANGE = "#e89a52"
RED = "#d65f5f"

# (min fraction of max, background, foreground)
_SCORE_BANDS = [
    (0.90, DARK_GREEN, "#ffffff"),
    (0.75, LIGHT_GREEN, "#ffffff"),
    (0.60, YELLOW, "#0f172a"),
    (0.45, ORANGE, "#ffffff"),
    (0.00, RED, "#ffffff"),
]

# NPS thresholds (-100..100 range, data here sits high)
_NPS_BANDS = [
    (60, DARK_GREEN, "#ffffff"),
    (40, LIGHT_GREEN, "#ffffff"),
    (20, YELLOW, "#0f172a"),
    (0, ORANGE, "#ffffff"),
    (-1e9, RED, "#ffffff"),
]

NEUTRAL_BG = "#eef2f7"
NEUTRAL_FG = "#64748b"


def score_band(value, vmax):
    r = value / vmax if vmax else 0
    for thr, bg, fg in _SCORE_BANDS:
        if r >= thr:
            return bg, fg
    return RED, "#ffffff"


def nps_band(value):
    for thr, bg, fg in _NPS_BANDS:
        if value >= thr:
            return bg, fg
    return RED, "#ffffff"


def _vmax(mode):
    return 100 if mode == "Top-2-Box" else 6


def _score_fmt(value, mode):
    return f"{value:.0f}%" if mode == "Top-2-Box" else f"{value:.2f}"


def _legend_items(mode):
    if mode == "Top-2-Box":
        labels = ["90–100%", "75–89%", "60–74%", "45–59%", "<45%"]
    else:
        labels = ["5.40–6.00", "4.50–5.39", "3.60–4.49", "2.70–3.59", "<2.70"]
    colors = [(DARK_GREEN, "#fff"), (LIGHT_GREEN, "#fff"), (YELLOW, "#0f172a"),
              (ORANGE, "#fff"), (RED, "#fff")]
    return [(lab, bg, fg) for lab, (bg, fg) in zip(labels, colors)]


def _legend_html(items):
    spans = "".join(
        f"<span class='ph-legend-item' style='background:{bg};color:{fg};'>{lab}</span>"
        for lab, bg, fg in items
    )
    return f"<div class='ph-legend'>{spans}</div>"


def _is_na(v):
    return v is None or (isinstance(v, float) and pd.isna(v))


def _table_html(matrix, color_fn, fmt_fn, row_header, na="–"):
    cols = list(matrix.columns)
    head = "".join(f"<th>{c}</th>" for c in cols)
    body = ""
    for idx, row in matrix.iterrows():
        cells = ""
        for c in cols:
            v = row[c]
            if _is_na(v):
                cells += f"<td><div class='ph-pill ph-na'>{na}</div></td>"
            else:
                bg, fg = color_fn(v, c)
                cells += (f"<td><div class='ph-pill' style='background:{bg};color:{fg};'>"
                          f"{fmt_fn(v, c)}</div></td>")
        body += f"<tr><td class='ph-rowlabel'>{idx}</td>{cells}</tr>"
    return (
        f"<div class='ph-wrap'><table class='pill-heatmap'>"
        f"<thead><tr><th class='ph-rowhead'>{row_header}</th>{head}</tr></thead>"
        f"<tbody>{body}</tbody></table></div>"
    )


def render_score_heatmap(box, matrix, mode="Mean", row_header="", na="–"):
    """Uniform-scale matrix (1–6 Mean or 0–100 Top-2-Box) → banded pill table."""
    if matrix is None or matrix.empty:
        box.info("No data available for the current filters.")
        return
    vmax = _vmax(mode)
    html = _table_html(
        matrix,
        color_fn=lambda v, c: score_band(v, vmax),
        fmt_fn=lambda v, c: _score_fmt(v, mode),
        row_header=row_header, na=na,
    )
    box.markdown(html + _legend_html(_legend_items(mode)), unsafe_allow_html=True)


def render_scorecard_heatmap(box, table, mode="Mean", row_header="Branch"):
    """Branch scorecard with per-column scales: NPS, CSI, Facility, n."""
    if table is None or table.empty:
        box.info("No data available for the current filters.")
        return
    vmax = _vmax(mode)

    def color_fn(v, c):
        if c == "NPS":
            return nps_band(v)
        if c == "n":
            return NEUTRAL_BG, NEUTRAL_FG
        return score_band(v, vmax)  # CSI, Facility

    def fmt_fn(v, c):
        if c == "NPS" or c == "n":
            return f"{v:.0f}"
        return _score_fmt(v, mode)

    html = _table_html(table, color_fn=color_fn, fmt_fn=fmt_fn, row_header=row_header)
    # No legend here: the scorecard mixes scales (NPS vs CSI/Facility), so a single
    # score-band legend would be misleading.
    box.markdown(html, unsafe_allow_html=True)
