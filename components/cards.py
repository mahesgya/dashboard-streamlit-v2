import streamlit as st


def metric_card(title, value, sub_text="vs previous period", delta_text=None, delta_type="up", accent=None):
    """A KPI metric card. `delta_text` renders a coloured up/down indicator."""
    delta_class = "metric-up" if delta_type == "up" else "metric-down"
    delta_html = f"<span class='{delta_class}'>{delta_text}</span>" if delta_text else ""

    accent_style = f"border-top:4px solid {accent};" if accent else ""

    # Hide the sub row when there is neither sub text nor a delta.
    # Without a sub row: centre the card content and enlarge the value.
    if (sub_text and sub_text.strip()) or delta_html:
        sub_html = f'<div class="metric-sub">{sub_text} &nbsp; {delta_html}</div>'
        card_class = "metric-card"
    else:
        sub_html = ""
        card_class = "metric-card no-sub"

    st.markdown(f"""
    <div class="{card_class}" style="{accent_style}">
        <div class="metric-title">{title}</div>
        <div class="metric-value">{value}</div>
        {sub_html}
    </div>
    """, unsafe_allow_html=True)


def comparison_card(title, xyz_value, comp_value, unit="", higher_is_better=True, accent=None):
    """KPI card that shows Bank XYZ value with a delta vs the competitor."""
    try:
        gap = float(xyz_value) - float(comp_value)
    except (TypeError, ValueError):
        gap = None

    if gap is None:
        delta_text = None
        delta_type = "up"
    else:
        ahead = (gap >= 0) if higher_is_better else (gap <= 0)
        arrow = "▲" if gap >= 0 else "▼"
        delta_text = f"{arrow} {abs(gap):.2f} vs competitor"
        delta_type = "up" if ahead else "down"

    value_text = f"{xyz_value}{unit}" if xyz_value is not None else "-"
    metric_card(
        title,
        value_text,
        sub_text=f"competitor: {comp_value}{unit}" if comp_value is not None else "",
        delta_text=delta_text,
        delta_type=delta_type,
        accent=accent,
    )


def chart_card_header(title, subtitle=None, icon_html=""):
    """Render the title/subtitle header used inside chart containers."""
    st.markdown(
        f'<div class="chart-title">{icon_html}{title}</div>',
        unsafe_allow_html=True,
    )
    if subtitle:
        st.markdown(
            f'<div class="chart-subtitle">{subtitle}</div>',
            unsafe_allow_html=True,
        )
