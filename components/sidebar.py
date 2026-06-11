import streamlit as st

from utils.labels import (
    GENDER_MAP, TENURE_MAP, TENURE_ORDER_RAW, FREQUENCY_MAP, FREQUENCY_ORDER_RAW, clean_age,
)


# dataframe column -> session_state key holding the current selection
FILTER_KEYS = {
    "PROV": "f_prov",
    "KABKOTA": "f_city",
    "CABANG": "f_branch",
    "S1": "f_gender",
    "S2_2": "f_age",
    "S4": "f_tenure",
    "S7": "f_freq",
}

GEO_LEVELS = ["PROV", "KABKOTA", "CABANG"]

# Per-page filter context (general revision: filters tailored per page).
PAGE_FILTERS = {
    "Overview": ["PROV", "KABKOTA", "CABANG"],
    "Respondent Profile": ["PROV", "S1", "S2_2", "S4", "S7"],
    "Usage & Competitor": ["PROV", "KABKOTA", "S1", "S2_2"],
    "Branch": ["PROV", "KABKOTA", "CABANG"],
    "Touchpoint": ["PROV", "CABANG", "S1", "S2_2"],
}

FILTER_META = {
    "PROV": dict(label="Province"),
    "KABKOTA": dict(label="City / Regency"),
    "CABANG": dict(label="Branch"),
    "S1": dict(label="Gender", label_map=GENDER_MAP),
    "S2_2": dict(label="Age Group", transform=clean_age),
    "S4": dict(label="Length of Relationship", label_map=TENURE_MAP, order=TENURE_ORDER_RAW),
    "S7": dict(label="Transaction Frequency", label_map=FREQUENCY_MAP, order=FREQUENCY_ORDER_RAW),
}

METRIC_MODE_KEY = "metric_mode"


def get_metric_mode():
    return st.session_state.get(METRIC_MODE_KEY, "Mean")


def _geo_scope_df(df, target_col):
    """Apply the geo selections of levels ABOVE `target_col` (cascade)."""
    out = df
    for col in GEO_LEVELS:
        if col == target_col:
            break
        sel = st.session_state.get(FILTER_KEYS[col], [])
        if sel and col in out.columns:
            out = out[out[col].astype(str).isin(sel)]
    return out


def _options_for(df, col):
    meta = FILTER_META[col]
    scope = _geo_scope_df(df, col) if col in GEO_LEVELS else df
    if col not in scope.columns:
        return []
    options = scope[col].dropna().astype(str)
    options = options[options.str.strip() != ""].unique().tolist()
    order = meta.get("order")
    if order:
        rank = {v: i for i, v in enumerate(order)}
        options = sorted(options, key=lambda x: rank.get(x, 999))
    else:
        options = sorted(options)
    return options


def _render_filter(df, col):
    meta = FILTER_META[col]
    key = FILTER_KEYS[col]
    options = _options_for(df, col)

    # Prune any stored selection that is no longer valid after a cascade change.
    current = [v for v in st.session_state.get(key, []) if v in options]
    st.session_state[key] = current

    def fmt(value):
        if meta.get("label_map") and value in meta["label_map"]:
            return meta["label_map"][value]
        if meta.get("transform"):
            return meta["transform"](value)
        return value

    st.multiselect(meta["label"], options=options, key=key, placeholder="All", format_func=fmt)


def _reset_filters(page):
    for col in PAGE_FILTERS.get(page, []):
        st.session_state[FILTER_KEYS[col]] = []


@st.dialog("Filters")
def filter_dialog(df, page):
    st.markdown("**Aggregate metric**")
    st.segmented_control(
        "Aggregate metric",
        options=["Mean", "Top-2-Box"],
        default="Mean",
        key=METRIC_MODE_KEY,
        label_visibility="collapsed",
    )
    st.markdown("<hr style='margin:14px 0;border-top:1px solid #e5e7eb;'>", unsafe_allow_html=True)

    for col in PAGE_FILTERS.get(page, []):
        _render_filter(df, col)

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.button("Reset", use_container_width=True, on_click=_reset_filters, args=(page,))
    with c2:
        if st.button("Apply", use_container_width=True, type="primary"):
            st.rerun()


def apply_filters(df, page):
    """Apply only the filters relevant to the current page."""
    out = df.copy()
    for col in PAGE_FILTERS.get(page, []):
        sel = st.session_state.get(FILTER_KEYS[col], [])
        if sel and col in out.columns:
            out = out[out[col].astype(str).isin(sel)]
    return out


NAV_ITEMS = {
    "▦  Overview": "Overview",
    "♙  Customer Respondent": "Respondent Profile",
    "▮  Usage & Competitor": "Usage & Competitor",
    "▥  Branch Experience": "Branch",
    "☆  Touchpoint Experience": "Touchpoint",
}


def render_sidebar(df):
    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-title">Bank XYZ<br>CX360</div>
            <div class="sidebar-caption">XYZ vs Competitor</div>
            """,
            unsafe_allow_html=True,
        )

        page_label = st.radio("Navigation", list(NAV_ITEMS.keys()), label_visibility="collapsed")
        page = NAV_ITEMS[page_label]

        st.markdown("<hr>", unsafe_allow_html=True)

        page_filter_cols = PAGE_FILTERS.get(page, [])
        active = sum(1 for c in page_filter_cols if st.session_state.get(FILTER_KEYS[c]))
        mode = get_metric_mode()
        btn_label = f"▤  Filters ({active})" if active else "▤  Filters"
        if st.button(btn_label, use_container_width=True):
            filter_dialog(df, page)

        st.caption(f"Aggregate metric: **{mode}**")

        st.markdown(
            """
            <div class="sidebar-info">
                <hr>
                <b>Aggregate default:</b> Mean (1–6)<br>
                <b>Benchmark:</b> Bank XYZ vs Competitor
            </div>
            """,
            unsafe_allow_html=True,
        )

    filtered_df = apply_filters(df, page)
    return page, filtered_df


def render_inline_filter_chips(page):
    """Optional: show active filters as a caption under the page header."""
    chips = []
    for col in PAGE_FILTERS.get(page, []):
        sel = st.session_state.get(FILTER_KEYS[col], [])
        if sel:
            chips.append(f"{FILTER_META[col]['label']}: {', '.join(map(str, sel[:3]))}"
                         + ("…" if len(sel) > 3 else ""))
    return chips
