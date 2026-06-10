import streamlit as st
import plotly.express as px

# =====================================================
# COLOR PALETTE (blue) — used across every chart
# order: dark -> light
# =====================================================
PALETTE = [
    "#001D39",
    "#0A4174",
    "#49769F",
    "#4E8EA2",
    "#6EA2B3",
    "#7BBDE8",
    "#BDD8E9",
]

# Continuous scale for value-based bars (light = small, dark = large)
PALETTE_CONTINUOUS = list(reversed(PALETTE))

# Bank XYZ vs Competitor comparison colors (used everywhere comparative)
XYZ_COLOR = "#0A4174"        # Bank XYZ — strong brand blue
COMP_COLOR = "#9CB7CC"       # Competitor — muted grey-blue
POSITIVE_COLOR = "#0A4174"   # XYZ ahead (diverging bars)
NEGATIVE_COLOR = "#dc2626"   # XYZ behind (diverging bars)

# Icon colors (taken from the darker end of the palette so they read on white)
ICON = {
    "darkest": "#001D39",
    "dark": "#0A4174",
    "mid": "#49769F",
    "teal": "#4E8EA2",
    "soft": "#6EA2B3",
}


def mi(name, color=ICON["dark"], size=20):
    """Render a Material Symbols (line) icon as inline HTML."""
    return (
        f"<span style=\"font-family:'Material Symbols Rounded';"
        f"font-size:{size}px;line-height:1;vertical-align:-4px;margin-right:8px;"
        f"color:{color};font-variation-settings:'FILL' 0,'wght' 500,'GRAD' 0,'opsz' 24;\">"
        f"{name}</span>"
    )


def load_icon_font():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200');
        </style>
        """,
        unsafe_allow_html=True,
    )


def _contrast_text(rgb_str):
    """Pick black or white text depending on the luminance of an 'rgb(...)' color."""
    try:
        nums = rgb_str[rgb_str.find("(") + 1: rgb_str.find(")")].split(",")
        r, g, b = (float(x) for x in nums[:3])
    except Exception:
        return "#ffffff"
    luminance = 0.299 * r + 0.587 * g + 0.114 * b
    return "#0f172a" if luminance > 150 else "#ffffff"


def base_layout(fig, height=330, margin=None, showlegend=False):
    """Apply the consistent white-card Plotly layout used across the dashboard."""
    fig.update_layout(
        height=height,
        margin=margin or dict(l=10, r=20, t=40, b=45),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(color="#0f172a", size=12),
        showlegend=showlegend,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
    )
    fig.update_xaxes(showgrid=False, zeroline=False, tickfont=dict(color="#0f172a"))
    fig.update_yaxes(showgrid=False, zeroline=False, tickfont=dict(color="#0f172a"))
    return fig


def style_treemap(fig, value_by_label, root_color="rgb(73, 118, 159)"):
    """Style a px.treemap consistently across pages."""
    labels = list(fig.data[0].labels)
    values = list(value_by_label.values())
    vmax = max(values) if values else 1
    vmin = min(values) if values else 0

    marker_colors = []
    text_colors = []
    for lab in labels:
        if lab in value_by_label:
            v = value_by_label[lab]
            norm = (v - vmin) / (vmax - vmin) if vmax > vmin else 0.5
            color = px.colors.sample_colorscale(PALETTE_CONTINUOUS, [norm])[0]
        else:
            color = root_color
        marker_colors.append(color)
        text_colors.append(_contrast_text(color))

    fig.update_traces(
        marker=dict(colors=marker_colors, line=dict(color="white", width=2)),
        insidetextfont=dict(color=text_colors, size=13),
        textinfo="label+percent root",
        textposition="middle center",
        tiling=dict(pad=3),
        hovertemplate="<b>%{label}</b><br>Respondents: %{value} (%{percentRoot:.1%})<extra></extra>",
    )
    return fig
