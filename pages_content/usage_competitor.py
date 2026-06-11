"""Page — Usage & Competitor.

Banking usage behaviour and the competitive landscape. All bars are expressed as
share of respondents (%).
"""

import pandas as pd
import plotly.express as px
import streamlit as st

from components.cards import kpi_card
from components.theme import PALETTE, PALETTE_CONTINUOUS, ICON, mi, load_icon_font, base_layout
from pages_content._common import page_header, spacer, chart_card, plot, empty_state


TRANSACTION_REASON_MAP = {
    "Kemudahan dalam bertransaksi dengan bank lain": "Easy Interbank Transfers",
    "Bank digunakan oleh banyak orang": "Widely Used",
    "Memberikan kecepatan dalam transaksi": "Fast Transactions",
    "Memiliki banyak ATM": "Extensive ATM Network",
    "Memiliki banyak cabang": "Extensive Branch Network",
    "Fitur transaksi di ATM lengkap": "Comprehensive ATM Features",
    "Memiliki banyak pilihan channel untuk melakukan transaksi (sms banking, internet banking, mobile banking, dll)": "Multiple Transaction Channels",
    "Fitur transaksi di e-channel lengkap": "Comprehensive E-Channel Features",
    "Didukung oleh layanan e-channel/e-banking yang baik": "Strong E-Banking Service",
    "Memberikan keuntungan saat digunakan untuk bertransaksi (diskon, cashback, point rewards)": "Promos & Cashback",
    "Lainnya": "Other",
}

SAVING_REASON_MAP = {
    "Aman menabung di bank tersebut/keamanannya terjamin": "Safe & Secure",
    "Bank tersebut memiliki reputasi yang baik": "Good Reputation",
    "Biaya administrasi bulanannya rendah": "Low Admin Fees",
    "Memiliki banyak produk tabungan untuk kebutuhan yang berbeda": "Comprehensive Savings Products",
    "Menawarkan suku bunga yang kompetitif": "Competitive Interest Rates",
    "Batas saldo mengendap minimalnya rendah": "Low Minimum Balance",
    "Banyak melakukan promosi produk tabungan dengan memberikan hadiah langsung (saat pembukaan awal rekening, berdasarkan rata-rata saldo mengendap)": "Direct Rewards",
    "Banyak melakukan promosi dengan undian berhadiah": "Prize Draws",
    "Banyak memberikan promo-promo berhadiah (cashback, point reward, dsb)": "Cashback Promos",
    "Tanpa biaya admin bulanan": "No Monthly Admin Fee",
    "Banyak memberikan undiah berhadiah": "Prize Giveaways",
    "Banyak memberikan hadiah langsung": "Direct Gifts",
    "Lainnya": "Other",
}

ACCOUNT_PURPOSE_MAP = {
    "Untuk menabung": "Saving",
    "Untuk menerima gaji dari tempat saya bekerja": "Salary Receipt",
    "Untuk melakukan transaksi finansial saya sehari-hari (seperti pembayaran tagihan listrik, telepon, pembelian pulsa telepon, pembelian token listrik, dll)": "Daily Transactions",
    "Untuk menunjang bisnis saya (menerima transfer dana dari klien/konsumen saya)": "Business Needs",
    "Sebagai syarat ketika mengambil kredit": "Loan Requirement",
    "Lainnya": "Other",
}

PURPOSE_STYLE = {
    "Saving": ("savings", "#0A4174"),
    "Salary Receipt": ("payments", "#4E8EA2"),
    "Daily Transactions": ("receipt_long", "#49769F"),
    "Business Needs": ("storefront", "#001D39"),
    "Loan Requirement": ("request_quote", "#6EA2B3"),
    "Other": ("more_horiz", "#7BBDE8"),
}


def _explode(df, col):
    s = df[col].dropna().astype(str) if col in df.columns else pd.Series(dtype=str)
    s = s[s.str.strip() != ""]
    return s.str.split(";").explode().str.strip()


def _pct_hbar(box, counts, total, label_map=None, top_n=10):
    if counts.empty or total == 0:
        empty_state(box); return
    if label_map:
        counts.index = counts.index.map(lambda x: label_map.get(x, str(x)[:40]))
        counts = counts.groupby(level=0).sum()
    counts = counts.sort_values(ascending=False).head(top_n).sort_values(ascending=True)
    data = counts.reset_index()
    data.columns = ["Category", "Count"]
    data["pct"] = (data["Count"] / total * 100).round(1)
    fig = px.bar(data, x="pct", y="Category", orientation="h", text="pct",
                 color="pct", color_continuous_scale=PALETTE_CONTINUOUS, custom_data=["Count"])
    fig.update_traces(textposition="outside", cliponaxis=False, texttemplate="%{text}%",
                      hovertemplate="<b>%{y}</b><br>%{x}% (%{customdata[0]} resp.)<extra></extra>")
    fig = base_layout(fig, height=max(320, 32 * len(data) + 60), margin=dict(l=10, r=50, t=30, b=30))
    fig.update_layout(coloraxis_showscale=False)
    fig.update_xaxes(title="% of respondents", range=[0, data["pct"].max() * 1.2], ticksuffix="%")
    fig.update_yaxes(title=None)
    plot(box, fig)


def render_kpis(df):
    total = len(df)
    xyz_pct = df["A1A"].astype(str).str.contains("Bank XYZ", na=False).mean() * 100 if total else 0
    saving_pct = (df["A1B"] == "Bank XYZ").mean() * 100 if total and "A1B" in df.columns else 0
    txn_pct = (df["A1C"] == "Bank XYZ").mean() * 100 if total and "A1C" in df.columns else 0
    multi_pct = df["A1A"].astype(str).str.contains(";").mean() * 100 if total else 0

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        kpi_card("groups", "Total Respondents", f"{total:,}", sub_text="survey participants", accent=ICON["dark"])
    with c2:
        kpi_card("account_balance", "Bank XYZ Users", f"{xyz_pct:.1f}%", sub_text="use Bank XYZ", accent=ICON["mid"])
    with c3:
        kpi_card("savings", "Primary Savings", f"{saving_pct:.1f}%", sub_text="XYZ as main savings", accent=ICON["teal"])
    with c4:
        kpi_card("sync_alt", "Primary Transactions", f"{txn_pct:.1f}%", sub_text="XYZ as main transactions", accent=ICON["darkest"])
    with c5:
        kpi_card("account_tree", "Multi-Bank Users", f"{multi_pct:.1f}%", sub_text="use more than one bank", accent=ICON["soft"])


def render_used_banks(df):
    box = chart_card("Most Frequently Used Banks", "Share of respondents using each bank",
                     icon=("account_balance", "dark", 18))
    _pct_hbar(box, _explode(df, "A1A").value_counts(), len(df), top_n=10)


def render_competitors(df):
    box = chart_card("Top Competitors", "Share of respondents naming each competitor",
                     icon=("leaderboard", "teal", 18))
    counts = df["KOMP"].dropna().astype(str) if "KOMP" in df.columns else pd.Series(dtype=str)
    counts = counts[counts.str.strip() != ""].value_counts()
    _pct_hbar(box, counts, len(df), top_n=10)


def render_savings_vs_transaction(df):
    box = chart_card("Primary Bank — Savings vs Transaction", "Share of respondents (%)",
                     icon=("compare_arrows", "dark", 18))
    total = len(df)
    if total == 0 or "A1B" not in df.columns:
        empty_state(box); return
    save = df["A1B"].value_counts(normalize=True).mul(100)
    txn = df["A1C"].value_counts(normalize=True).mul(100)
    compare = pd.concat([save.rename("Savings"), txn.rename("Transaction")], axis=1).fillna(0)
    compare["total"] = compare.sum(axis=1)
    compare = compare.sort_values("total", ascending=False).head(8).drop(columns="total").reset_index()
    compare.rename(columns={"index": "Bank"}, inplace=True)

    fig = px.bar(compare, x="Bank", y=["Savings", "Transaction"], barmode="group",
                 color_discrete_sequence=[PALETTE[1], PALETTE[3]])
    fig.update_traces(texttemplate="%{y:.1f}%", textposition="outside", cliponaxis=False,
                      hovertemplate="%{x}<br>%{y:.1f}%<extra>%{fullData.name}</extra>")
    fig = base_layout(fig, height=400, showlegend=True, margin=dict(l=10, r=20, t=40, b=60))
    fig.update_layout(legend_title_text="")
    fig.update_xaxes(title=None, tickangle=-20)
    fig.update_yaxes(title="% of respondents", ticksuffix="%")
    plot(box, fig)


def render_reason_transaction(df):
    box = chart_card("Reason to Use Bank for Transactions", "Share of respondents (B3)",
                     icon=("sync_alt", "mid", 18))
    _pct_hbar(box, _explode(df, "B3").value_counts(), len(df), label_map=TRANSACTION_REASON_MAP, top_n=10)


def render_reason_saving(df):
    box = chart_card("Reason to Use Bank for Savings", "Share of respondents (B4)",
                     icon=("savings", "teal", 18))
    _pct_hbar(box, _explode(df, "B4").value_counts(), len(df), label_map=SAVING_REASON_MAP, top_n=10)


def render_purpose_tiles(df):
    box = chart_card("Account Opening Purpose", "Share of respondents (%)",
                     icon=("account_balance_wallet", "soft", 18))
    purpose = _explode(df, "A2").value_counts(normalize=True).mul(100).round(1).head(6)
    if purpose.empty:
        empty_state(box); return
    purpose.index = purpose.index.map(lambda x: ACCOUNT_PURPOSE_MAP.get(x, str(x)[:24]))
    purpose = purpose.groupby(level=0).sum().sort_values(ascending=False)
    max_pct = purpose.max() if len(purpose) else 1

    with box:
        cols = st.columns(3)
        for i, (label, pct) in enumerate(purpose.items()):
            icon, color = PURPOSE_STYLE.get(label, ("account_balance_wallet", PALETTE[2]))
            width = (pct / max_pct * 100) if max_pct else 0
            icon_html = (
                f"<span style=\"font-family:'Material Symbols Rounded';font-size:22px;line-height:1;color:{color};"
                f"font-variation-settings:'FILL' 0,'wght' 500,'GRAD' 0,'opsz' 24;\">{icon}</span>"
            )
            with cols[i % 3]:
                st.markdown(
                    f"""
                    <div style="background:#ffffff; border:1px solid #e5e7eb; border-radius:16px;
                                padding:16px 18px; box-shadow:0 2px 8px rgba(15,23,42,0.04); margin-bottom:14px;">
                        <div style="display:flex; align-items:center; gap:12px; margin-bottom:12px;">
                            <div style="width:42px; height:42px; border-radius:12px; background:{color}1a;
                                        display:flex; align-items:center; justify-content:center; flex-shrink:0;">{icon_html}</div>
                            <div style="font-size:13px; font-weight:800; color:#334155; line-height:1.25;">{label}</div>
                        </div>
                        <div style="font-size:28px; font-weight:900; color:#0f172a; line-height:1;">{pct:.1f}%</div>
                        <div style="margin-top:12px; background:#eef2f7; border-radius:999px; height:8px;">
                            <div style="width:{width:.0f}%; height:8px; background:{color}; border-radius:999px;"></div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


def render_insights(df):
    total = len(df)
    xyz_pct = df["A1A"].astype(str).str.contains("Bank XYZ").mean() * 100 if total else 0
    komp = df["KOMP"].dropna().astype(str) if "KOMP" in df.columns else pd.Series(dtype=str)
    komp = komp[komp.str.strip() != ""]
    if not komp.empty:
        top_comp = komp.value_counts(normalize=True).mul(100)
        top_comp_bank, top_comp_pct = top_comp.index[0], top_comp.iloc[0]
    else:
        top_comp_bank, top_comp_pct = "-", 0
    save_pct = (df["A1B"] == "Bank XYZ").mean() * 100 if "A1B" in df.columns else 0
    txn_pct = (df["A1C"] == "Bank XYZ").mean() * 100 if "A1C" in df.columns else 0
    txn = _explode(df, "B3").value_counts()
    save = _explode(df, "B4").value_counts()
    top_txn = TRANSACTION_REASON_MAP.get(txn.index[0], str(txn.index[0])[:40]) if not txn.empty else "-"
    top_save = SAVING_REASON_MAP.get(save.index[0], str(save.index[0])[:40]) if not save.empty else "-"

    st.markdown(
        f"""
    <div class="insight-box" style="min-height:auto;">
        <div class="insight-title">{mi("lightbulb", ICON["darkest"], 22)}Key Insights</div>
        <ul style="list-style:none; padding-left:0; margin:0;
                   display:grid; grid-template-columns:repeat(2, 1fr); gap:10px 36px;">
            <li>{mi("account_balance", ICON["dark"])}<b>{xyz_pct:.1f}%</b> of respondents use Bank XYZ — very strong penetration.</li>
            <li>{mi("leaderboard", ICON["teal"])}<b>{top_comp_bank}</b> is the leading competitor (<b>{top_comp_pct:.1f}%</b>).</li>
            <li>{mi("compare_arrows", ICON["mid"])}Bank XYZ is the primary bank for savings (<b>{save_pct:.1f}%</b>) and transactions (<b>{txn_pct:.1f}%</b>).</li>
            <li>{mi("sync_alt", ICON["darkest"])}Top transaction driver: <b>{top_txn}</b>; top savings driver: <b>{top_save}</b>.</li>
        </ul>
    </div>
    """,
        unsafe_allow_html=True,
    )


def render_usage_competitor(df, labels=None, mode="Mean"):
    load_icon_font()
    page_header("Usage & Competitor", "Banking usage behaviour and the competitive landscape")
    render_kpis(df)

    spacer(28)
    c1, c2 = st.columns(2)
    with c1:
        render_used_banks(df)
    with c2:
        render_competitors(df)

    spacer()
    render_savings_vs_transaction(df)

    spacer()
    c3, c4 = st.columns(2)
    with c3:
        render_reason_transaction(df)
    with c4:
        render_reason_saving(df)

    spacer()
    render_purpose_tiles(df)

    spacer()
    render_insights(df)
