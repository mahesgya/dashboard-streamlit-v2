"""Page 2 — Respondent Profile.

Who the respondents are (demographics & banking behaviour) and a sanity check on
sample representativeness. All distribution bars are shown as share of respondents.
"""

import pandas as pd
import plotly.express as px
import streamlit as st

from components.cards import kpi_card
from components.theme import PALETTE, PALETTE_CONTINUOUS, ICON, mi, load_icon_font, style_treemap, base_layout
from utils import labels as L
from pages_content._common import page_header, spacer, chart_card, plot, empty_state


def _counts(df, col):
    if col not in df.columns:
        return pd.Series(dtype=int)
    return df[col].dropna().astype(str).replace("", pd.NA).dropna().value_counts()


def _multi_counts(df, col, sep=";"):
    if col not in df.columns:
        return pd.Series(dtype=int)
    s = df[col].dropna().astype(str)
    s = s[s.str.strip() != ""]
    exploded = s.str.split(sep).explode().str.strip()
    exploded = exploded[exploded != ""]
    return exploded.value_counts()


def render_kpis(df):
    total = len(df)
    avg_age = pd.to_numeric(df.get("S2_1_num"), errors="coerce").mean() if "S2_1_num" in df.columns else None
    avg_age_txt = f"{avg_age:.1f}" if pd.notna(avg_age) else "-"

    existing_txt = (f"{df['S3'].astype(str).str.lower().str.startswith('ya').mean()*100:.1f}%"
                    if "S3" in df.columns and total else "-")
    married_txt = (f"{(df['P1'].astype(str)=='Menikah').mean()*100:.1f}%"
                   if "P1" in df.columns and total else "-")

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        kpi_card("groups", "Total Respondents", f"{total:,}", sub_text="survey participants", accent=ICON["dark"])
    with k2:
        kpi_card("cake", "Avg. Age", avg_age_txt, sub_text="mean age (years)", accent=ICON["mid"])
    with k3:
        kpi_card("verified_user", "Existing Customers", existing_txt, sub_text="share of respondents", accent=ICON["darkest"])
    with k4:
        kpi_card("favorite", "Married", married_txt, sub_text="share of respondents", accent=ICON["soft"])


def _donut(box, counts, total, center_label="Total"):
    data = counts.reset_index()
    data.columns = ["Category", "Count"]
    fig = px.pie(data, names="Category", values="Count", hole=0.58,
                 color_discrete_sequence=["#0A4174", "#7BBDE8", "#49769F", "#BDD8E9", "#6EA2B3"])
    fig.update_traces(textposition="inside", textinfo="percent",
                      insidetextorientation="horizontal", textfont_size=13,
                      marker=dict(line=dict(color="#ffffff", width=2)))
    fig.update_layout(height=330, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor="white",
                      showlegend=True, font=dict(color="#0f172a", size=12),
                      legend=dict(orientation="h", yanchor="bottom", y=-0.08, xanchor="center", x=0.5),
                      annotations=[dict(text=f"<b>{total:,}</b><br>{center_label}", x=0.5, y=0.5,
                                        font_size=15, showarrow=False)])
    plot(box, fig)


def render_age(df):
    box = chart_card("Age Distribution", "Share of respondents by age group", icon=("cake", "dark", 18))
    counts = _counts(df, "S2_2")
    if counts.empty:
        empty_state(box); return
    total = len(df)
    data = counts.reset_index()
    data.columns = ["Age Group", "Count"]
    data["Age Group"] = data["Age Group"].map(L.clean_age)
    data["pct"] = (data["Count"] / total * 100).round(1)
    data["_sort"] = data["Age Group"].str.extract(r"(\d+)").astype(float)
    data = data.sort_values("_sort")
    fig = px.bar(data, x="Age Group", y="pct", text="pct", color="Age Group",
                 color_discrete_sequence=PALETTE, custom_data=["Count"])
    fig.update_traces(textposition="outside", cliponaxis=False, texttemplate="%{text}%",
                      hovertemplate="<b>%{x}</b><br>%{y}% (%{customdata[0]} resp.)<extra></extra>")
    fig = base_layout(fig, height=330, margin=dict(l=10, r=10, t=40, b=50))
    fig.update_yaxes(title="% of respondents", range=[0, data["pct"].max() * 1.25], ticksuffix="%")
    fig.update_xaxes(title="Age group (years)")
    plot(box, fig)


def render_gender(df):
    box = chart_card("Gender", "Share of respondents", icon=("wc", "mid", 18))
    counts = _counts(df, "S1")
    if counts.empty:
        empty_state(box); return
    counts.index = counts.index.map(lambda x: L.GENDER_MAP.get(x, x))
    _donut(box, counts.groupby(level=0).sum(), len(df))


def render_marital(df):
    box = chart_card("Marital Status", "Share of respondents", icon=("favorite", "teal", 18))
    counts = _counts(df, "P1")
    if counts.empty:
        empty_state(box); return
    counts.index = counts.index.map(lambda x: L.MARITAL_MAP.get(x, x))
    _donut(box, counts.groupby(level=0).sum(), len(df))


def _hbar(box, counts, total, label_map=None, top_n=10):
    if counts.empty:
        empty_state(box); return
    if label_map:
        counts.index = counts.index.map(lambda x: label_map.get(x, x))
        counts = counts.groupby(level=0).sum().sort_values(ascending=False)
    counts = counts.head(top_n).sort_values(ascending=True)
    data = counts.reset_index()
    data.columns = ["Category", "Count"]
    data["pct"] = (data["Count"] / total * 100).round(1)
    fig = px.bar(data, x="pct", y="Category", orientation="h", text="pct",
                 color="pct", color_continuous_scale=PALETTE_CONTINUOUS, custom_data=["Count"])
    fig.update_traces(textposition="outside", cliponaxis=False, texttemplate="%{text}%",
                      hovertemplate="<b>%{y}</b><br>%{x}% (%{customdata[0]} resp.)<extra></extra>")
    fig = base_layout(fig, height=max(300, 30 * len(data) + 60), margin=dict(l=10, r=45, t=30, b=30))
    fig.update_layout(coloraxis_showscale=False)
    fig.update_xaxes(title="% of respondents", range=[0, data["pct"].max() * 1.2], ticksuffix="%")
    fig.update_yaxes(title=None)
    plot(box, fig)


def render_education(df):
    box = chart_card("Highest Education", "Share of respondents", icon=("school", "mid", 18))
    _hbar(box, _counts(df, "P3"), len(df), label_map=L.EDUCATION_MAP)


def render_occupation(df):
    box = chart_card("Occupation", "Share of respondents", icon=("work", "soft", 18))
    counts = _counts(df, "P4")
    if counts.empty:
        empty_state(box); return
    counts.index = counts.index.map(lambda x: L.OCCUPATION_MAP.get(x, x))
    counts = counts.groupby(level=0).sum().sort_values(ascending=False)
    top = counts.head(7)
    others = int(counts.iloc[7:].sum())
    data = top.reset_index()
    data.columns = ["Occupation", "Count"]
    if others > 0:
        data = pd.concat([data, pd.DataFrame([{"Occupation": "Other", "Count": others}])], ignore_index=True)
    fig = px.treemap(data, path=[px.Constant("All Respondents"), "Occupation"], values="Count")
    style_treemap(fig, dict(zip(data["Occupation"], data["Count"])))
    fig.update_layout(height=330, margin=dict(l=10, r=10, t=20, b=10), paper_bgcolor="white",
                      font=dict(color="#0f172a", size=12))
    plot(box, fig)


def render_other_banks(df):
    box = chart_card("Other Banks Used", "Share of respondents using each bank alongside Bank XYZ",
                     icon=("account_balance", "dark", 18))
    counts = _multi_counts(df, "A1A")
    counts = counts[counts.index != "Bank XYZ"]
    _hbar(box, counts, len(df), top_n=8)


def render_motivation(df):
    box = chart_card("Account Opening Motivation", "Share of respondents (A2)", icon=("savings", "teal", 18))
    counts = _multi_counts(df, "A2")
    if counts.empty:
        empty_state(box); return
    short = {
        "Untuk menabung": "To save money",
        "Untuk menerima gaji dari tempat saya bekerja": "To receive salary",
        "Untuk melakukan transaksi finansial saya sehari-hari (seperti pembayaran tagihan listrik, telepon, pembelian pulsa telepon, pembelian token listrik, dll)": "Daily transactions",
        "Untuk investasi": "For investment",
        "Untuk menunjang bisnis saya (menerima transfer dana dari klien/konsumen saya)": "To support my business",
    }
    counts.index = counts.index.map(lambda x: short.get(x, (x[:40] + "…") if len(x) > 42 else x))
    _hbar(box, counts.groupby(level=0).sum(), len(df), top_n=8)


def render_insights(df):
    total = len(df)
    top_age = _counts(df, "S2_2")
    top_age = L.clean_age(top_age.idxmax()) if not top_age.empty else "-"
    g = _counts(df, "S1")
    top_gender = L.GENDER_MAP.get(g.idxmax(), g.idxmax()) if not g.empty else "-"

    st.markdown(
        f"""
    <div class="insight-box" style="min-height:auto;">
        <div class="insight-title">{mi("lightbulb", ICON["darkest"], 22)}Key Insights</div>
        <ul style="list-style:none; padding-left:0; margin:0;
                   display:grid; grid-template-columns:repeat(2, 1fr); gap:10px 36px;">
            <li>{mi("cake", ICON["dark"])}The most common age group is <b>{top_age}</b>.</li>
            <li>{mi("wc", ICON["mid"])}The largest gender group is <b>{top_gender}</b>.</li>
            <li>{mi("account_balance", ICON["teal"])}The "other banks used" chart reveals the competitors held alongside Bank XYZ.</li>
            <li>{mi("savings", ICON["soft"])}Saving and salary receipt dominate the reasons for opening an account.</li>
        </ul>
    </div>
    """,
        unsafe_allow_html=True,
    )


def render_respondent_profile(df, labels=None, mode="Mean"):
    load_icon_font()
    page_header("Respondent Profile", "Demographic characteristics and banking behaviour of the survey sample")
    render_kpis(df)

    spacer(28)
    r1c1, r1c2, r1c3 = st.columns([1.3, 0.85, 0.85])
    with r1c1:
        render_age(df)
    with r1c2:
        render_gender(df)
    with r1c3:
        render_marital(df)

    spacer()
    r2c1, r2c2 = st.columns([1, 1])
    with r2c1:
        render_education(df)
    with r2c2:
        render_occupation(df)

    spacer()
    r3c1, r3c2 = st.columns([1, 1])
    with r3c1:
        render_other_banks(df)
    with r3c2:
        render_motivation(df)

    spacer()
    render_insights(df)
