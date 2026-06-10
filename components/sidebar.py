import streamlit as st


# =========================
# Filter label maps & ordering (raw survey value -> English label)
# =========================
TENURE_LABEL_MAP = {
    "1 bulan s/d 3 bulan": "1–3 months",
    "3 bulan s/d 11 bulan": "3–11 months",
    "1 tahun s/d 2 tahun 11 bulan": "1–2 years",
    "3 tahun s/d 4 tahun 11 bulan": "3–4 years",
    "5 tahun atau lebih": "≥ 5 years",
}

TENURE_ORDER = [
    "1 bulan s/d 3 bulan",
    "3 bulan s/d 11 bulan",
    "1 tahun s/d 2 tahun 11 bulan",
    "3 tahun s/d 4 tahun 11 bulan",
    "5 tahun atau lebih",
]

FREQUENCY_LABEL_MAP = {
    "1 minggu 2 kali atau lebih": "≥ 2× a week",
    "1 minggu sekali": "Once a week",
    "2 minggu sekali": "Once every 2 weeks",
    "1 bulan sekali": "Once a month",
}

FREQUENCY_ORDER = [
    "1 minggu 2 kali atau lebih",
    "1 minggu sekali",
    "2 minggu sekali",
    "1 bulan sekali",
]

GENDER_LABEL_MAP = {
    "Pria": "Male",
    "Laki-laki": "Male",
    "Wanita": "Female",
    "Perempuan": "Female",
}


def clean_age_label(value):
    """Translate the Indonesian age-group labels (only the word 'tahun')."""
    value = str(value)
    value = value.replace(" tahun ke atas", "+ years")
    value = value.replace(" tahun dan ke atas", "+ years")
    value = value.replace(" tahun", " years")
    return value


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

# How the aggregate metric is computed across the whole app
METRIC_MODE_KEY = "metric_mode"


def get_metric_mode():
    """Return the active aggregate mode: 'Mean' (default) or 'Top-2-Box'."""
    return st.session_state.get(METRIC_MODE_KEY, "Mean")


def sidebar_multiselect(label, col, df, key, label_map=None, custom_order=None, transform=None):
    if col not in df.columns:
        return

    options = df[col].dropna().astype(str).unique().tolist()

    if custom_order:
        order_dict = {value: i for i, value in enumerate(custom_order)}
        options = sorted(options, key=lambda x: order_dict.get(x, 999))
    else:
        options = sorted(options)

    def format_label(value):
        if label_map and value in label_map:
            return label_map[value]
        if transform:
            return transform(value)
        return value

    st.multiselect(
        label,
        options=options,
        key=key,
        placeholder="All",
        format_func=format_label,
    )


def apply_filters(df, filters):
    filtered_df = df.copy()
    for col, selected_values in filters.items():
        if col in filtered_df.columns and selected_values:
            filtered_df = filtered_df[filtered_df[col].astype(str).isin(selected_values)]
    return filtered_df


def _reset_filters():
    for k in FILTER_KEYS.values():
        st.session_state[k] = []


@st.dialog("Filters")
def filter_dialog(df):
    sidebar_multiselect("Province", "PROV", df, FILTER_KEYS["PROV"])
    sidebar_multiselect("City / Regency", "KABKOTA", df, FILTER_KEYS["KABKOTA"])
    sidebar_multiselect("Branch", "CABANG", df, FILTER_KEYS["CABANG"])
    sidebar_multiselect("Gender", "S1", df, FILTER_KEYS["S1"], label_map=GENDER_LABEL_MAP)
    sidebar_multiselect("Age Group", "S2_2", df, FILTER_KEYS["S2_2"], transform=clean_age_label)
    sidebar_multiselect(
        "Length of Relationship",
        "S4",
        df,
        FILTER_KEYS["S4"],
        label_map=TENURE_LABEL_MAP,
        custom_order=TENURE_ORDER,
    )
    sidebar_multiselect(
        "Transaction Frequency",
        "S7",
        df,
        FILTER_KEYS["S7"],
        label_map=FREQUENCY_LABEL_MAP,
        custom_order=FREQUENCY_ORDER,
    )

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.button("Reset", use_container_width=True, on_click=_reset_filters)
    with c2:
        if st.button("Apply", use_container_width=True, type="primary"):
            st.rerun()


NAV_ITEMS = {
    "▦  Overview": "Overview",
    "♙  Respondent Profile": "Respondent Profile",
    "▥  Branch": "Branch",
    "☆  Touchpoint": "Touchpoint",
}


def render_sidebar(df):
    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-title">Bank XYZ<br>CX Dashboard</div>
            <div class="sidebar-caption">XYZ vs Competitor</div>
            """,
            unsafe_allow_html=True,
        )

        page_label = st.radio(
            "Navigation",
            list(NAV_ITEMS.keys()),
            label_visibility="collapsed",
        )
        page = NAV_ITEMS[page_label]

        st.markdown("<hr>", unsafe_allow_html=True)

        # Aggregate metric toggle — applies to every comparison chart.
        st.markdown("**Aggregate metric**")
        st.segmented_control(
            "Aggregate metric",
            options=["Mean", "Top-2-Box"],
            default="Mean",
            key=METRIC_MODE_KEY,
            label_visibility="collapsed",
        )

        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

        # Filters open in a centered modal (keeps the sidebar compact).
        active = sum(1 for k in FILTER_KEYS.values() if st.session_state.get(k))
        btn_label = f"▤  Filters ({active})" if active else "▤  Filters"

        if st.button(btn_label, use_container_width=True):
            filter_dialog(df)

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

    filters = {col: st.session_state.get(key, []) for col, key in FILTER_KEYS.items()}
    filtered_df = apply_filters(df, filters)

    return page, filtered_df, filters
