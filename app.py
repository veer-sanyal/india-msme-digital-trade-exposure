from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

DATA = Path(__file__).parent / "data" / "processed"


st.set_page_config(
    page_title="India Digital Services Trade Exposure",
    layout="wide",
)


@st.cache_data
def load_dds() -> pd.DataFrame:
    return pd.read_csv(DATA / "dds_india.csv")


dds = load_dds()
total = dds[dds["indicator"] == "DDS"].copy()
categories = dds[dds["indicator"] != "DDS"].copy()
latest_year = int(total["year"].max())

st.title("India Digital Services Trade Exposure")
st.caption(
    "v0 — Mapping India's digital services trade against MSME sectors to "
    "surface which small businesses are most exposed to global digital "
    "platforms and policy shifts."
)

st.subheader("Overview — India's digitally delivered services trade")

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
st.plotly_chart(trend, use_container_width=True)

st.markdown("##### By service category")
flow_choice = st.radio(
    "Flow",
    options=["export", "import"],
    horizontal=True,
    label_visibility="collapsed",
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
st.plotly_chart(breakdown, use_container_width=True)

st.divider()
st.caption(
    f"**Source:** WTO Digitally Delivered Services Trade Dataset (Mode 1 cross-border "
    f"supply only; 2005-{latest_year}). Partner is the World aggregate — bilateral "
    "country-level cuts are not available in this dataset. Processed via "
    "`scripts/build_processed.py` from `data/processed/dds_india.csv`."
)
st.markdown(
    "[GitHub repository](https://github.com/veer-sanyal/india-msme-digital-trade-exposure)"
)
