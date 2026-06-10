import streamlit as st


def load_css():
    st.markdown(
        """
    <style>
    /* =====================================================
       GLOBAL APP STYLE
    ===================================================== */
    .stApp {
        background-color: #f8fafc;
    }

    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }

    /* Keep the header transparent (do not hide it entirely so the
       sidebar open/close control is not removed). */
    header[data-testid="stHeader"] {
        background: transparent !important;
    }

    /* Hide the top-right toolbar (Deploy / menu), not the whole header. */
    [data-testid="stToolbar"],
    [data-testid="stDecoration"] {
        display: none !important;
    }

    /* Lock the sidebar open: hide the collapse toggle. */
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapseButton"],
    [data-testid="stExpandSidebarButton"] {
        display: none !important;
    }

    /* Force the sidebar to stay open at full width. */
    section[data-testid="stSidebar"] {
        transform: none !important;
        visibility: visible !important;
        margin-left: 0 !important;
    }

    section[data-testid="stSidebar"][aria-expanded="false"] {
        transform: none !important;
        margin-left: 0 !important;
    }

    .block-container {
        padding-top: 1.2rem;
        padding-left: 1.4rem;
        padding-right: 1.4rem;
        padding-bottom: 2rem;
        max-width: 100%;
    }

    div[data-testid="stVerticalBlock"] {
        gap: 0.8rem;
    }

    hr {
        border: none;
        border-top: 1px solid #1e3a5f;
        margin: 22px 0;
    }


    /* =====================================================
       SIDEBAR BACKGROUND
    ===================================================== */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #061b3a 0%, #08244d 100%);
        width: 285px !important;
        min-width: 285px !important;
    }

    section[data-testid="stSidebar"] > div {
        padding-top: 1.4rem;
        padding-left: 1.1rem;
        padding-right: 1.1rem;
    }

    section[data-testid="stSidebar"] * {
        color: white;
    }

    .sidebar-title {
        font-size: 25px;
        font-weight: 900;
        line-height: 1.22;
        margin-bottom: 6px;
        color: #ffffff;
        letter-spacing: 0.2px;
    }

    .sidebar-caption {
        font-size: 12.5px;
        color: #9fb6d4;
        font-weight: 600;
        margin-bottom: 26px;
    }

    .sidebar-info {
        font-size: 13px;
        color: #cbd5e1;
        margin-top: 32px;
        line-height: 1.7;
    }


    /* =====================================================
       SIDEBAR RADIO NAVIGATION — LOOK LIKE A CUSTOM MENU
    ===================================================== */
    section[data-testid="stSidebar"] div[role="radiogroup"] {
        display: flex;
        flex-direction: column;
        gap: 8px;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label {
        background-color: transparent !important;
        border-radius: 12px !important;
        padding: 0px !important;
        margin: 0px 0px 4px 0px !important;
        min-height: 44px !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
        display: flex !important;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label > div {
        padding: 12px 14px !important;
        border-radius: 12px !important;
        width: 100% !important;
        flex: 1 1 100% !important;
        box-sizing: border-box !important;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label:hover > div {
        background-color: rgba(255, 255, 255, 0.08) !important;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) > div {
        background-color: #0b5ba7 !important;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] p {
        color: #ffffff !important;
        font-weight: 800 !important;
        font-size: 15px !important;
        line-height: 1.2 !important;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] input {
        display: none !important;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] svg {
        display: none !important;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child {
        display: none !important;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label > div:last-child {
        margin-left: 0px !important;
    }


    /* =====================================================
       SIDEBAR FILTER LABELS
    ===================================================== */
    section[data-testid="stSidebar"] h3 {
        color: #ffffff !important;
        font-size: 18px;
        font-weight: 800;
        margin-bottom: 12px;
    }

    section[data-testid="stSidebar"] label {
        color: #ffffff !important;
        font-weight: 700;
        font-size: 13px;
        margin-bottom: 4px;
    }


    /* =====================================================
       SIDEBAR MULTISELECT / SELECTBOX
    ===================================================== */
    section[data-testid="stSidebar"] div[data-baseweb="select"] {
        background-color: #ffffff !important;
        border-radius: 10px !important;
        border: none !important;
    }

    section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        border-radius: 10px !important;
        border: 1px solid #e5e7eb !important;
        min-height: 40px !important;
    }

    section[data-testid="stSidebar"] div[data-baseweb="select"] * {
        color: #0f172a !important;
    }

    section[data-testid="stSidebar"] div[data-baseweb="select"] input { color: #0f172a !important; }
    section[data-testid="stSidebar"] div[data-baseweb="select"] span { color: #0f172a !important; }

    section[data-testid="stSidebar"] span[data-baseweb="tag"] {
        background-color: #e0f2fe !important;
        color: #0f172a !important;
        border-radius: 8px !important;
        padding: 3px 6px !important;
        margin: 2px !important;
    }

    section[data-testid="stSidebar"] span[data-baseweb="tag"] span {
        color: #0f172a !important;
        font-size: 12px !important;
    }

    section[data-testid="stSidebar"] span[data-baseweb="tag"] svg {
        color: #0f172a !important;
        fill: #0f172a !important;
    }


    /* =====================================================
       DROPDOWN MENU LIST
    ===================================================== */
    div[data-baseweb="popover"] { z-index: 999999 !important; }

    div[data-baseweb="popover"] ul {
        background-color: #ffffff !important;
        border-radius: 10px !important;
        border: 1px solid #e5e7eb !important;
        box-shadow: 0px 8px 24px rgba(15, 23, 42, 0.16) !important;
        padding-top: 6px !important;
        padding-bottom: 6px !important;
    }

    div[data-baseweb="popover"] li {
        color: #334155 !important;
        font-size: 14px !important;
        padding-top: 9px !important;
        padding-bottom: 9px !important;
    }

    div[data-baseweb="popover"] li:hover { background-color: #f1f5f9 !important; }


    /* =====================================================
       PAGE TITLE
    ===================================================== */
    .page-title {
        font-size: 30px;
        font-weight: 900;
        color: #0f172a;
        margin-bottom: 2px;
        letter-spacing: -0.4px;
    }

    .page-subtitle {
        font-size: 15px;
        color: #475569;
        margin-bottom: 22px;
    }


    /* =====================================================
       KPI METRIC CARDS
    ===================================================== */
    .metric-card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 14px 14px;
        min-height: 132px;
        height: 100%;
        box-shadow: 0px 2px 8px rgba(15, 23, 42, 0.04);
        display: flex;
        flex-direction: column;
    }

    .metric-card.no-sub {
        align-items: center;
        justify-content: center;
        text-align: center;
    }

    .metric-card.no-sub .metric-value {
        font-size: 34px;
        margin-top: 4px;
    }

    .metric-title {
        font-size: 12.5px;
        color: #334155;
        font-weight: 800;
        margin-bottom: 6px;
        line-height: 1.25;
    }

    .metric-value {
        font-size: 22px;
        font-weight: 900;
        color: #0f172a;
        line-height: 1.15;
        letter-spacing: 0.2px;
        white-space: nowrap;
    }

    .metric-sub {
        font-size: 11px;
        color: #64748b;
        margin-top: auto;
        padding-top: 8px;
    }

    .metric-up { color: #16a34a; font-weight: 800; }
    .metric-down { color: #dc2626; font-weight: 800; }


    /* =====================================================
       CHART CARDS / CONTAINER
    ===================================================== */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        box-shadow: 0px 2px 8px rgba(15, 23, 42, 0.04);
    }

    div[data-testid="stVerticalBlockBorderWrapper"] > div {
        padding: 16px 16px 10px 16px;
    }

    .chart-title {
        font-size: 15px;
        font-weight: 900;
        color: #0f172a;
        margin-bottom: 4px;
        line-height: 1.3;
    }

    .chart-subtitle {
        font-size: 12px;
        color: #64748b;
        margin-bottom: 8px;
    }

    .chart-caption {
        font-size: 12px;
        color: #64748b;
        margin-top: 6px;
        line-height: 1.5;
        font-style: italic;
    }


    /* =====================================================
       INSIGHT BOX
    ===================================================== */
    .insight-box {
        background: #ecfeff;
        border: 1px solid #cffafe;
        border-radius: 16px;
        padding: 22px 24px;
        height: 100%;
        min-height: 310px;
        box-shadow: 0px 2px 8px rgba(15, 23, 42, 0.04);
    }

    .insight-title {
        color: #0f766e;
        font-size: 20px;
        font-weight: 900;
        margin-bottom: 14px;
    }

    .insight-box ul { padding-left: 18px; margin-top: 0; margin-bottom: 0; }

    .insight-box li {
        margin-bottom: 12px;
        color: #0f172a;
        font-size: 14px;
        line-height: 1.55;
    }


    /* =====================================================
       STREAMLIT BUTTONS
    ===================================================== */
    .stButton > button {
        background-color: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        color: #0f172a;
        font-weight: 700;
        padding: 0.55rem 1rem;
    }

    .stButton > button:hover {
        border-color: #0b5ba7;
        color: #0b5ba7;
    }


    /* =====================================================
       MEAN / TOP-2-BOX TOGGLE (segmented control & radio)
    ===================================================== */
    div[data-testid="stSegmentedControl"] button {
        border-radius: 10px !important;
        font-weight: 700 !important;
    }


    /* =====================================================
       SIDEBAR FILTER BUTTON
    ===================================================== */
    section[data-testid="stSidebar"] .stButton > button {
        background: rgba(255, 255, 255, 0.08) !important;
        border: 1px solid rgba(255, 255, 255, 0.18) !important;
        border-radius: 12px !important;
        color: #ffffff !important;
        font-weight: 800 !important;
        font-size: 15px !important;
        padding: 12px 14px !important;
        width: 100% !important;
        justify-content: flex-start !important;
    }

    section[data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(255, 255, 255, 0.16) !important;
        border-color: rgba(255, 255, 255, 0.30) !important;
        color: #ffffff !important;
    }

    section[data-testid="stSidebar"] .stButton > button p {
        color: #ffffff !important;
        font-weight: 800 !important;
        font-size: 15px !important;
    }

    /* Mean / Top-2-Box toggle living in the sidebar */
    section[data-testid="stSidebar"] div[data-testid="stSegmentedControl"] button {
        color: #0f172a !important;
    }


    /* =====================================================
       FILTER DIALOG (centered modal)
    ===================================================== */
    div[data-testid="stDialog"] div[role="dialog"] { border-radius: 16px !important; }

    div[data-testid="stDialog"] label {
        color: #0f172a !important;
        font-weight: 700 !important;
        font-size: 13px !important;
    }


    /* =====================================================
       DATAFRAME / TABLE
    ===================================================== */
    div[data-testid="stDataFrame"] {
        border-radius: 14px;
        overflow: hidden;
        border: 1px solid #e5e7eb;
    }


    /* =====================================================
       PLOTLY CHART SPACING
    ===================================================== */
    div[data-testid="stPlotlyChart"] { margin-top: -4px; }


    /* =====================================================
       SMALL RESPONSIVE ADJUSTMENT
    ===================================================== */
    @media (max-width: 1500px) {
        .metric-card { padding: 12px 12px; min-height: 128px; }
        .metric-value { font-size: 19px; }
        .metric-title { font-size: 11.5px; margin-bottom: 5px; }
        .metric-sub { font-size: 10px; }
        .page-title { font-size: 27px; }
        .chart-title { font-size: 14px; }
    }

    @media (max-width: 1280px) {
        .metric-value { font-size: 17px; }
        .metric-title { font-size: 11px; }
    }

    </style>
    """,
        unsafe_allow_html=True,
    )
