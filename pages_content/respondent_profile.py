"""Page 2 — Respondent Profile.

Who the respondents are (demographics & banking behaviour) and a sanity check on
sample representativeness. All distribution bars are shown as share of respondents.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from components.cards import kpi_card
from components.theme import PALETTE, PALETTE_CONTINUOUS, ICON, mi, load_icon_font, style_treemap, base_layout
from utils import labels as L
from pages_content._common import page_header, spacer, chart_card, plot, empty_state


def _counts(df, col):
    if col not in df.columns:
        return pd.Series(dtype=int)
    return df[col].dropna().astype(str).replace("", pd.NA).dropna().value_counts()


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


def _ordinal_data(df, col, label_map, order):
    """Ordered counts/percentages for an ordinal category (fixed order, not by count)."""
    counts = _counts(df, col)
    if counts.empty:
        return None
    counts.index = counts.index.map(lambda x: label_map.get(x, x))
    counts = counts.groupby(level=0).sum()
    total = len(df)
    display = [c for c in order if c in counts.index] + [c for c in counts.index if c not in order]
    data = pd.DataFrame({"Category": display, "Count": [int(counts.get(c, 0)) for c in display]})
    data["pct"] = (data["Count"] / total * 100).round(1)
    return data


def render_tenure(df):
    box = chart_card("Length of Relationship", "Customer lifecycle by tenure with Bank XYZ",
                     icon=("history", "teal", 18))
    data = _ordinal_data(df, "S4", L.TENURE_MAP, L.TENURE_ORDER)
    if data is None:
        empty_state(box); return
    fig = px.funnel(data, x="Count", y="Category")
    fig.update_traces(
        marker=dict(color=data["Count"], colorscale=PALETTE_CONTINUOUS, line=dict(color="white", width=1.5)),
        text=data["pct"], texttemplate="%{text}%", textposition="inside",
        textfont=dict(color="white", size=12), customdata=data["Count"],
        hovertemplate="<b>%{y}</b><br>%{customdata} resp. (%{text}%)<extra></extra>",
    )
    fig.update_layout(height=330, margin=dict(l=10, r=20, t=20, b=30), paper_bgcolor="white",
                      plot_bgcolor="white", font=dict(color="#0f172a", size=12), showlegend=False)
    fig.update_yaxes(title=None)
    plot(box, fig)


def render_frequency(df):
    box = chart_card("Transaction Frequency", "Share of respondents by how often they transact",
                     icon=("sync", "dark", 18))
    data = _ordinal_data(df, "S7", L.FREQUENCY_MAP, L.FREQUENCY_ORDER)
    if data is None:
        empty_state(box); return
    cats = data["Category"].tolist()
    counts = data["Count"].tolist()
    pcts = data["pct"].tolist()
    max_r = max(counts) if counts else 1
    fig = go.Figure(go.Scatterpolar(
        r=counts + [counts[0]], theta=cats + [cats[0]],
        fill="toself", fillcolor="rgba(10,65,116,0.25)", line=dict(color="#0A4174", width=2.5),
        marker=dict(size=8, color="#0A4174"), mode="lines+markers+text",
        text=[f"{p}%" for p in pcts] + [f"{pcts[0]}%"], textposition="top center",
        textfont=dict(size=11, color="#0f172a"), customdata=counts + [counts[0]],
        hovertemplate="<b>%{theta}</b><br>%{customdata} resp.<extra></extra>",
    ))
    fig.update_layout(
        height=330, margin=dict(l=60, r=60, t=40, b=40), paper_bgcolor="white",
        font=dict(color="#0f172a", size=12), showlegend=False,
        polar=dict(bgcolor="white",
                   radialaxis=dict(visible=True, range=[0, max_r * 1.15], gridcolor="#E2E8F0",
                                   tickfont=dict(size=10, color="#64748b")),
                   angularaxis=dict(gridcolor="#E2E8F0", tickfont=dict(size=11, color="#0f172a"))),
    )
    plot(box, fig)


def render_insights(df):
    top_age = _counts(df, "S2_2")
    top_age = L.clean_age(top_age.idxmax()) if not top_age.empty else "-"
    g = _counts(df, "S1")
    top_gender = L.GENDER_MAP.get(g.idxmax(), g.idxmax()) if not g.empty else "-"
    ten = _counts(df, "S4")
    top_tenure = L.TENURE_MAP.get(ten.idxmax(), ten.idxmax()) if not ten.empty else "-"
    freq = _counts(df, "S7")
    top_freq = L.FREQUENCY_MAP.get(freq.idxmax(), freq.idxmax()) if not freq.empty else "-"

    st.markdown(
        f"""
    <div class="insight-box" style="min-height:auto;">
        <div class="insight-title">{mi("lightbulb", ICON["darkest"], 22)}Key Insights</div>
        <ul style="list-style:none; padding-left:0; margin:0;
                   display:grid; grid-template-columns:repeat(2, 1fr); gap:10px 36px;">
            <li>{mi("cake", ICON["dark"])}The most common age group is <b>{top_age}</b>.</li>
            <li>{mi("wc", ICON["mid"])}The largest gender group is <b>{top_gender}</b>.</li>
            <li>{mi("history", ICON["teal"])}Most respondents have banked with Bank XYZ for <b>{top_tenure}</b>.</li>
            <li>{mi("sync", ICON["soft"])}The most common transaction frequency is <b>{top_freq}</b>.</li>
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
        render_tenure(df)
    with r3c2:
        render_frequency(df)

    spacer()
    render_insights(df)
