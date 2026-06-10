"""Shared page helpers: header, chart-card wrapper, empty-state guard."""

import streamlit as st

from components.theme import mi, ICON


def page_header(title, subtitle):
    st.markdown(f'<div class="page-title">{title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-subtitle">{subtitle}</div>', unsafe_allow_html=True)


def spacer(px=18):
    st.markdown(f"<div style='height:{px}px'></div>", unsafe_allow_html=True)


def chart_card(title, subtitle=None, icon=("insights", "dark", 18)):
    """Context manager returning a bordered white card with a styled header."""
    box = st.container(border=True)
    name, key, size = icon
    box.markdown(
        f'<div class="chart-title">{mi(name, ICON[key], size)}{title}</div>',
        unsafe_allow_html=True,
    )
    if subtitle:
        box.markdown(f'<div class="chart-subtitle">{subtitle}</div>', unsafe_allow_html=True)
    return box


def caption(box, text):
    box.markdown(f'<div class="chart-caption">{text}</div>', unsafe_allow_html=True)


def plot(box, fig):
    box.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def empty_state(box, message="No data available for the current filters."):
    box.info(message)
