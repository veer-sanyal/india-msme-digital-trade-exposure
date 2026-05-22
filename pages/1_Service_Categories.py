from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

DATA = Path(__file__).resolve().parents[1] / "data" / "processed"

LEVEL_1_EBOPS = [
    "SC",
    "SDASDB3",
    "SDB1SK21",
    "SDB2SK22",
    "SE",
    "SFSG",
    "SISK1",
    "SJXSJ34",
    "SK23",
    "SK24",
    "SWSJ34",
]


st.set_page_config(
    page_title="Service Categories | India Digital Services Trade Exposure",
    layout="wide",
)


@st.cache_data
def load_tismos() -> pd.DataFrame:
    return pd.read_csv(DATA / "tismos_india.csv")


@st.cache_data
def load_crosswalk() -> pd.DataFrame:
    return pd.read_csv(DATA / "ebops_isic_crosswalk.csv")


tismos = load_tismos()
crosswalk = load_crosswalk()

st.title("Service Categories")
st.caption(
    "All 11 EBOPS service categories, all four GATS modes of supply. "
    "Mode 1 (cross-border) is what reconciles to the Overview page's "
    "digitally delivered services series."
)

level1 = tismos[tismos["indicator"].isin(LEVEL_1_EBOPS)].copy()
year_min, year_max = int(level1["year"].min()), int(level1["year"].max())

c1, c2 = st.columns([1, 2])
with c1:
    flow_choice = st.radio(
        "Flow",
        options=["export", "import"],
        horizontal=True,
    )
with c2:
    year_choice = st.slider(
        "Year",
        min_value=year_min,
        max_value=year_max,
        value=year_max,
        step=1,
    )

st.markdown(f"### By service category, Mode 1 ({year_choice})")
st.caption(
    "Cross-border supply only. Hover for the ISIC section each EBOPS category maps to."
)

mode1 = level1[
    (level1["mode"] == "Mode 1")
    & (level1["flow"] == flow_choice)
    & (level1["year"] == year_choice)
].copy()

joined = mode1.merge(
    crosswalk[["ebops_code", "isic_section", "isic_section_name"]],
    left_on="indicator",
    right_on="ebops_code",
    how="left",
)
joined["value_busd"] = joined["value_musd"] / 1000
joined = joined.sort_values("value_busd", ascending=True)

bar = px.bar(
    joined,
    x="value_busd",
    y="indicator_name",
    orientation="h",
    title=f"India services {flow_choice}s, Mode 1, by category ({year_choice})",
    labels={"value_busd": "USD billion", "indicator_name": ""},
    custom_data=["isic_section", "isic_section_name"],
)
bar.update_traces(
    hovertemplate=(
        "<b>%{y}</b><br>"
        "%{x:.2f} USD billion<br>"
        "ISIC section %{customdata[0]}: %{customdata[1]}"
        "<extra></extra>"
    )
)
bar.update_layout(hovermode="closest", margin=dict(l=10, r=10, t=60, b=10))
st.plotly_chart(bar, width="stretch")

st.divider()

defaults_by_flow = {
    "export": "Other business services (excluding trade-related)",
    "import": "Other business services (excluding trade-related)",
}
category_options = (
    level1[["indicator", "indicator_name"]]
    .drop_duplicates()
    .sort_values("indicator_name")
)
default_name = defaults_by_flow.get(flow_choice, category_options["indicator_name"].iloc[0])
default_index = int(
    category_options["indicator_name"].tolist().index(default_name)
    if default_name in category_options["indicator_name"].tolist()
    else 0
)

st.markdown("### Mode mix over time, within a category")
chosen_name = st.selectbox(
    "Category",
    options=category_options["indicator_name"].tolist(),
    index=default_index,
)
chosen_code = category_options.loc[
    category_options["indicator_name"] == chosen_name, "indicator"
].iloc[0]

mode_mix = level1[
    (level1["indicator"] == chosen_code) & (level1["flow"] == flow_choice)
].copy()
mode_mix["value_busd"] = mode_mix["value_musd"] / 1000
mode_mix = mode_mix.sort_values(["year", "mode"])

area = px.area(
    mode_mix,
    x="year",
    y="value_busd",
    color="mode",
    title=f"{chosen_name}: India {flow_choice}s by mode of supply, {year_min}-{year_max}",
    labels={"value_busd": "USD billion", "year": "Year", "mode": "Mode"},
    category_orders={"mode": ["Mode 1", "Mode 2", "Mode 3", "Mode 4"]},
)
area.update_layout(hovermode="x unified", legend_title_text="")
st.plotly_chart(area, width="stretch")

st.divider()
st.caption(
    f"**Source:** WTO TiSMoS (Trade in Services by Mode of Supply), {year_min}-{year_max}. "
    "Partner is the World aggregate; bilateral country-level cuts are not available. "
    "Processed via `scripts/build_processed.py` from `data/processed/tismos_india.csv`. "
    "ISIC section labels come from the WTO TiSMoS items-and-correspondence workbook "
    "via `data/processed/ebops_isic_crosswalk.csv`. TiSMoS coverage ends 2022; the "
    "Overview page extends Mode 1 totals to the latest year via the DDS dataset."
)
