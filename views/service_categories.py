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


@st.cache_data
def load_tismos() -> pd.DataFrame:
    return pd.read_csv(DATA / "tismos_india.csv")


@st.cache_data
def load_crosswalk() -> pd.DataFrame:
    return pd.read_csv(DATA / "ebops_isic_crosswalk.csv")


def render() -> None:
    tismos = load_tismos()
    crosswalk = load_crosswalk()
    level1 = tismos[tismos["indicator"].isin(LEVEL_1_EBOPS)].copy()
    year_min, year_max = int(level1["year"].min()), int(level1["year"].max())

    st.subheader(f"Service categories: where India's services trade concentrates, {year_min}-{year_max}")

    st.markdown(
        "The Overview tracked the headline digitally delivered services total. "
        "This page zooms into the eleven EBOPS service categories the WTO publishes and "
        "splits them across the four GATS modes of supply. The story is uneven concentration. "
        "Two categories make most of the money, two more drag the trade balance down, and "
        "a handful of smaller categories have quietly gone digital in the last decade."
    )

    top_c1, top_c2 = st.columns([1, 2])
    with top_c1:
        flow = st.radio(
            "Flow",
            options=["export", "import"],
            horizontal=True,
            key="svc_flow",
        )
    with top_c2:
        year = st.slider(
            "Year",
            min_value=year_min,
            max_value=year_max,
            value=year_max,
            step=1,
            key="svc_year",
        )

    selected = (
        level1[(level1["flow"] == flow) & (level1["year"] == year)]
        .groupby(["indicator", "indicator_name"], as_index=False)["value_musd"]
        .sum()
    )
    selected = selected.merge(
        crosswalk[["ebops_code", "isic_section", "isic_section_name"]],
        left_on="indicator",
        right_on="ebops_code",
        how="left",
    )
    selected["value_busd"] = selected["value_musd"] / 1000
    selected_sorted = selected.sort_values("value_busd", ascending=False).reset_index(drop=True)

    top1 = selected_sorted.iloc[0]
    top2 = selected_sorted.iloc[1]
    top2_share = (top1["value_busd"] + top2["value_busd"]) / selected_sorted["value_busd"].sum() * 100

    st.markdown(f"##### The shape of the {flow} side, {year}")
    st.markdown(
        f"In {year}, **{top1['indicator_name']}** ({top1['isic_section_name']}) and "
        f"**{top2['indicator_name']}** ({top2['isic_section_name']}) together account "
        f"for **{top2_share:.0f}% of India's services {flow}s** across all four modes. "
        f"The remaining nine categories share what's left. This concentration is one of "
        "the cleanest reasons to be specific about MSME exposure: the platforms and "
        "policy shifts that touch these two categories touch most of the trade."
    )

    bar = px.bar(
        selected_sorted.sort_values("value_busd"),
        x="value_busd",
        y="indicator_name",
        orientation="h",
        labels={"value_busd": "USD billion", "indicator_name": ""},
        custom_data=["isic_section", "isic_section_name"],
        color="value_busd",
        color_continuous_scale="Blues",
    )
    bar.update_traces(
        hovertemplate=(
            "<b>%{y}</b><br>"
            "%{x:.2f} USD billion<br>"
            "ISIC section %{customdata[0]}: %{customdata[1]}"
            "<extra></extra>"
        )
    )
    bar.update_layout(
        title=f"India services {flow}s by category, {year} (all four modes)",
        coloraxis_showscale=False,
        margin=dict(l=10, r=10, t=60, b=10),
    )
    st.plotly_chart(bar, width="stretch")

    st.divider()

    exp_year = (
        level1[(level1["year"] == year) & (level1["flow"] == "export")]
        .groupby(["indicator", "indicator_name"])["value_musd"]
        .sum()
    )
    imp_year = (
        level1[(level1["year"] == year) & (level1["flow"] == "import")]
        .groupby(["indicator", "indicator_name"])["value_musd"]
        .sum()
    )
    net = (
        pd.concat([exp_year.rename("exp"), imp_year.rename("imp")], axis=1)
        .fillna(0)
        .assign(net_busd=lambda d: (d["exp"] - d["imp"]) / 1000)
        .reset_index()
        .sort_values("net_busd")
    )
    biggest_surplus = net.iloc[-1]
    biggest_deficit = net.iloc[0]
    total_net = net["net_busd"].sum()

    st.markdown(f"##### Net trade balance by category, {year}")
    st.markdown(
        f"India ran a **\\${total_net:.0f}B services trade surplus** in {year}, but the "
        f"per-category picture is anything but uniform. **{biggest_surplus['indicator_name']}** "
        f"contributed the biggest surplus at **+\\${biggest_surplus['net_busd']:.0f}B**, with "
        "the IT-and-business-services duo carrying most of the gains. On the other end, "
        f"**{biggest_deficit['indicator_name']}** ran the biggest deficit at "
        f"**−\\${abs(biggest_deficit['net_busd']):.0f}B**: Indian firms pay foreign shipping lines, "
        "airlines, and logistics providers far more than the country earns moving foreign "
        "trade. Transport MSMEs sit on the wrong side of this gap."
    )

    balance_chart = px.bar(
        net,
        x="net_busd",
        y="indicator_name",
        orientation="h",
        labels={"net_busd": f"Net trade, USD billion ({year})", "indicator_name": ""},
        color="net_busd",
        color_continuous_scale="RdBu",
        color_continuous_midpoint=0,
    )
    balance_chart.update_layout(
        title=f"India services net trade by category, {year}",
        coloraxis_showscale=False,
        margin=dict(l=10, r=10, t=60, b=10),
    )
    balance_chart.add_vline(x=0, line_color="#888", line_width=1)
    st.plotly_chart(balance_chart, width="stretch")

    st.divider()

    mode_shares = (
        level1[(level1["year"] == year) & (level1["flow"] == flow)]
        .groupby(["indicator_name", "mode"], as_index=False)["value_musd"]
        .sum()
    )
    totals = mode_shares.groupby("indicator_name")["value_musd"].sum().reset_index(name="total")
    mode_shares = mode_shares.merge(totals, on="indicator_name")
    mode_shares["share_pct"] = (mode_shares["value_musd"] / mode_shares["total"] * 100).where(
        mode_shares["total"] > 0, 0
    )
    mode_order = ["Mode 1", "Mode 2", "Mode 3", "Mode 4"]
    category_order = (
        mode_shares.groupby("indicator_name")["total"].max().sort_values(ascending=True).index.tolist()
    )

    m1_2022 = mode_shares[mode_shares["mode"] == "Mode 1"].set_index("indicator_name")
    most_digital = m1_2022["share_pct"].idxmax()
    most_digital_pct = m1_2022["share_pct"].max()

    st.markdown(f"##### Mode mix: how digital is each category, {year}")
    st.markdown(
        "The WTO splits services trade into four GATS modes. **Mode 1 is cross-border supply**: "
        "the service crosses a border digitally (or by phone, mail, etc.) without anyone moving. "
        "Mode 2 is consumption abroad (tourism, foreign students). Mode 3 is commercial presence "
        "(local subsidiaries of foreign firms). Mode 4 is the temporary movement of workers. "
        f"For India's {flow}s in {year}, **{most_digital}** is the most digital category at "
        f"**{most_digital_pct:.0f}% Mode 1**. Categories that lean Mode 1 are also the ones where "
        "global digital platforms have the most leverage over Indian firms supplying the service. "
        "Tourism, by definition, has no Mode 1 component at all (a tourist has to physically travel)."
    )

    mix_chart = px.bar(
        mode_shares,
        x="share_pct",
        y="indicator_name",
        color="mode",
        orientation="h",
        labels={"share_pct": "Share of category total, %", "indicator_name": "", "mode": "Mode"},
        category_orders={"mode": mode_order, "indicator_name": category_order},
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    mix_chart.update_layout(
        title=f"India services {flow}s, mode share by category, {year}",
        barmode="stack",
        legend_title_text="",
        margin=dict(l=10, r=10, t=60, b=10),
        xaxis=dict(ticksuffix="%"),
    )
    st.plotly_chart(mix_chart, width="stretch")

    st.divider()

    st.markdown("##### The digital shift over time")

    m1_export_year = (
        level1[(level1["flow"] == "export") & (level1["mode"] == "Mode 1")]
        .groupby(["indicator", "indicator_name", "year"], as_index=False)["value_musd"]
        .sum()
    )
    all_export_year = (
        level1[level1["flow"] == "export"]
        .groupby(["indicator", "indicator_name", "year"], as_index=False)["value_musd"]
        .sum()
    )
    m1_share_year = m1_export_year.merge(
        all_export_year, on=["indicator", "indicator_name", "year"], suffixes=("_m1", "_all")
    )
    m1_share_year["m1_share_pct"] = (
        m1_share_year["value_musd_m1"] / m1_share_year["value_musd_all"] * 100
    ).where(m1_share_year["value_musd_all"] > 0, 0)

    shift = m1_share_year[m1_share_year["year"].isin([year_min, year_max])].pivot(
        index="indicator_name", columns="year", values="m1_share_pct"
    ).rename(columns={year_min: "pct_2005", year_max: "pct_2022"})
    shift["delta"] = shift["pct_2022"] - shift["pct_2005"]
    shift = shift.dropna(subset=["delta"]).sort_values("delta", ascending=False)

    biggest_shifters = shift.head(3)
    shifter_lines = []
    for name, row in biggest_shifters.iterrows():
        shifter_lines.append(
            f"**{name}** rose from {row['pct_2005']:.0f}% Mode 1 in {year_min} to "
            f"{row['pct_2022']:.0f}% in {year_max}"
        )

    st.markdown(
        f"Some categories went digital in real time over {year_min}-{year_max}. "
        + "; ".join(shifter_lines)
        + ". Telemedicine, ed-tech, and remote consultancy all show up in the WTO data as "
        "Mode 1 shares climbing. Pick a category below to see how its mode mix evolved over "
        "the full series."
    )

    category_options = (
        level1[["indicator", "indicator_name"]]
        .drop_duplicates()
        .sort_values("indicator_name")
    )
    default_name = "Telecommunications, computer, information and audiovisual services"
    default_index = (
        category_options["indicator_name"].tolist().index(default_name)
        if default_name in category_options["indicator_name"].tolist()
        else 0
    )
    chosen_name = st.selectbox(
        "Category",
        options=category_options["indicator_name"].tolist(),
        index=default_index,
        key="svc_category",
    )
    chosen_code = category_options.loc[
        category_options["indicator_name"] == chosen_name, "indicator"
    ].iloc[0]

    mode_mix = level1[
        (level1["indicator"] == chosen_code) & (level1["flow"] == flow)
    ].copy()
    mode_mix["value_busd"] = mode_mix["value_musd"] / 1000
    mode_mix = mode_mix.sort_values(["year", "mode"])

    area = px.area(
        mode_mix,
        x="year",
        y="value_busd",
        color="mode",
        title=f"{chosen_name}: India {flow}s by mode of supply, {year_min}-{year_max}",
        labels={"value_busd": "USD billion", "year": "Year", "mode": "Mode"},
        category_orders={"mode": ["Mode 1", "Mode 2", "Mode 3", "Mode 4"]},
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    area.update_layout(hovermode="x unified", legend_title_text="")
    st.plotly_chart(area, width="stretch")

    st.divider()
    st.caption(
        f"**Source:** WTO TiSMoS (Trade in Services by Mode of Supply), {year_min}-{year_max}, "
        "all four GATS modes. Partner is the World aggregate; bilateral country-level cuts are not "
        "available. ISIC section labels come from the WTO TiSMoS items-and-correspondence workbook. "
        "Processed via `scripts/build_processed.py` from `data/processed/tismos_india.csv` and "
        "`data/processed/ebops_isic_crosswalk.csv`. TiSMoS coverage ends 2022; the Overview "
        "extends Mode 1 totals to the latest year via the WTO DDS dataset."
    )


if __name__ == "__main__":
    render()
