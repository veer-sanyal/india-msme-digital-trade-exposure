from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

DATA = Path(__file__).resolve().parents[1] / "data" / "processed"


@st.cache_data
def load_dds() -> pd.DataFrame:
    return pd.read_csv(DATA / "dds_india.csv")


dds = load_dds()
total = dds[dds["indicator"] == "DDS"].copy()
categories = dds[dds["indicator"] != "DDS"].copy()
latest_year = int(total["year"].max())
earliest_year = int(total["year"].min())


def _cat_value_busd(flow: str, indicator_code: str, year: int) -> float:
    row = dds[
        (dds["flow"] == flow)
        & (dds["indicator"] == indicator_code)
        & (dds["year"] == year)
    ]
    return float(row["value_musd"].iloc[0]) / 1000


comp_exp_latest = _cat_value_busd("export", "SI2", latest_year)
obs_exp_latest = _cat_value_busd("export", "SJ", latest_year)
ip_imp_latest = _cat_value_busd("import", "SH", latest_year)
ip_imp_earliest = _cat_value_busd("import", "SH", earliest_year)
ip_growth_x = ip_imp_latest / ip_imp_earliest

st.title("India Digital Services Trade Exposure")
st.caption(
    "v0. Mapping India's digital services trade against MSME sectors to surface "
    "which small businesses are most exposed to global digital platforms and policy shifts."
)

st.subheader(f"Overview: India's digitally delivered services trade, 2005-{latest_year}")

exp_latest = total.loc[
    (total["flow"] == "export") & (total["year"] == latest_year), "value_musd"
].iloc[0]
imp_latest = total.loc[
    (total["flow"] == "import") & (total["year"] == latest_year), "value_musd"
].iloc[0]
exp_prev = total.loc[
    (total["flow"] == "export") & (total["year"] == latest_year - 1), "value_musd"
].iloc[0]
yoy_pct = (exp_latest - exp_prev) / exp_prev * 100

c1, c2, c3 = st.columns(3)
c1.metric(
    f"Exports ({latest_year})",
    f"${exp_latest/1000:.1f} B",
    f"{yoy_pct:+.1f}% YoY",
)
c2.metric(f"Imports ({latest_year})", f"${imp_latest/1000:.1f} B")
c3.metric("Net surplus", f"${(exp_latest - imp_latest)/1000:.1f} B")

st.markdown(
    "India's *digitally delivered services* (DDS) trade covers services "
    "supplied cross-border via the internet, telephone, or other electronic "
    "networks, as defined by the WTO DDS dataset. The chart below tracks "
    f"exports and imports in USD billions from 2005 through {latest_year}, "
    "with India measured against the rest of the world. The story is the "
    "post-2020 inflection. Exports grew at roughly 5 to 7 percent a year "
    "through the 2010s, then accelerated to about 18 percent annually after "
    "the pandemic, lifting the net DDS surplus from around $13B in 2005 to "
    "over $200B today. Digitally delivered services are now one of India's "
    "largest sources of foreign exchange, and they have decoupled sharply "
    "from import growth."
)

total_b = total.assign(value_busd=total["value_musd"] / 1000).sort_values("year")
trend = px.line(
    total_b,
    x="year",
    y="value_busd",
    color="flow",
    markers=True,
    title=f"Total digitally delivered services trade, 2005-{latest_year}",
    labels={"value_busd": "USD billion", "year": "Year", "flow": ""},
)
trend.update_layout(hovermode="x unified", legend_title_text="")
st.plotly_chart(trend, width="stretch")

st.markdown("##### By service category")
st.markdown(
    "The same WTO series, broken into the eight EBOPS service categories: "
    "computer services, other business services, IP licensing, telecoms, "
    "financial, insurance, information, and personal and cultural. Use the "
    "toggle below to switch between export and import flows. On the export "
    "side, two categories carry almost the entire story. *Computer services* "
    "(the traditional IT and BPO trade) reached about "
    f"${comp_exp_latest:.0f}B in {latest_year}, while *Other business "
    "services* (management consulting, R&D, technical and professional work) "
    f"reached about ${obs_exp_latest:.0f}B. The latter is now the larger of "
    "the two and growing faster, a quiet shift in what \"India's services "
    "exports\" actually means. On the import side, *Charges for the use of "
    f"intellectual property* has grown roughly {ip_growth_x:.0f}x since "
    f"{earliest_year} to around ${ip_imp_latest:.0f}B. That is a direct "
    "measure of the licensing fees Indian firms pay to foreign platforms "
    "and software vendors, and the clearest single proxy in this dataset "
    "for the platform exposure MSMEs face."
)
flow_choice = st.radio(
    "Flow",
    options=["export", "import"],
    horizontal=True,
    label_visibility="collapsed",
    key="overview_flow",
)
cat_data = categories[categories["flow"] == flow_choice].sort_values("year")
breakdown = px.area(
    cat_data,
    x="year",
    y="value_musd",
    color="indicator_name",
    title=f"India DDS {flow_choice}s by service category",
    labels={
        "value_musd": "USD million",
        "year": "Year",
        "indicator_name": "Category",
    },
)
breakdown.update_layout(legend_title_text="", hovermode="x unified")
st.plotly_chart(breakdown, width="stretch")

st.divider()
st.caption(
    f"**Source:** WTO Digitally Delivered Services Trade Dataset (Mode 1 cross-border "
    f"supply only; 2005-{latest_year}). Partner is the World aggregate; bilateral "
    "country-level cuts are not available in this dataset. Processed via "
    "`scripts/build_processed.py` from `data/processed/dds_india.csv`."
)
