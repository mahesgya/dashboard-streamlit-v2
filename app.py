import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))

from components.style import load_css
from components.sidebar import render_sidebar, get_metric_mode
from utils.data_loader import load_data

from pages_content.overview import render_overview
from pages_content.respondent_profile import render_respondent_profile
from pages_content.usage_competitor import render_usage_competitor
from pages_content.branch import render_branch
from pages_content.touchpoint import render_touchpoint


st.set_page_config(
    page_title="Bank XYZ CX Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_css()

df, labels = load_data()

page, filtered_df = render_sidebar(df)
mode = get_metric_mode()

if page == "Overview":
    render_overview(filtered_df, labels, mode)
elif page == "Respondent Profile":
    render_respondent_profile(filtered_df, labels, mode)
elif page == "Usage & Competitor":
    render_usage_competitor(filtered_df, labels, mode)
elif page == "Branch":
    render_branch(filtered_df, labels, mode)
elif page == "Touchpoint":
    render_touchpoint(filtered_df, labels, mode)
