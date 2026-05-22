from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
        "Two categories make most of the digital trade, a few categories have quietly gone "
        "digital in the last decade, and the bulk of India's services trade deficit sits "
        "in non-digital modes the platforms barely touch."
    )

    year = st.slider(
        "Year",
        min_value=year_min,
        max_value=year_max,
        value=year_max,
        step=1,
        key="svc_year",
    )

    mode1_exp = (
        level1[(level1["year"] == year) & (level1["flow"] == "export") & (level1["mode"] == "Mode 1")]
        .groupby(["indicator", "indicator_name"], as_index=False)["value_musd"]
        .sum()
        .rename(columns={"value_musd": "exp_musd"})
    )
    mode1_imp = (
        level1[(level1["year"] == year) & (level1["flow"] == "import") & (level1["mode"] == "Mode 1")]
        .groupby(["indicator", "indicator_name"], as_index=False)["value_musd"]
        .sum()
        .rename(columns={"value_musd": "imp_musd"})
    )
    diverge = (
        mode1_exp.merge(mode1_imp, on=["indicator", "indicator_name"], how="outer")
        .fillna(0)
        .assign(
            exp_busd=lambda d: d["exp_musd"] / 1000,
            imp_busd=lambda d: d["imp_musd"] / 1000,
            total_busd=lambda d: (d["exp_musd"] + d["imp_musd"]) / 1000,
            net_busd=lambda d: (d["exp_musd"] - d["imp_musd"]) / 1000,
        )
        .sort_values("total_busd", ascending=True)
        .reset_index(drop=True)
    )

    top2 = diverge.sort_values("exp_busd", ascending=False).head(2)
    top_names = top2["indicator_name"].tolist()
    top2_share_exp = top2["exp_busd"].sum() / diverge["exp_busd"].sum() * 100
    mode1_net = diverge["net_busd"].sum()
    surplus_two = diverge.sort_values("net_busd", ascending=False).head(2)
    transport_row = diverge[diverge["indicator_name"] == "Transport"].iloc[0]

    st.markdown(f"##### Digital trade by category, {year}")
    st.markdown(
        f"Filtering to **Mode 1 (cross-border supply)** isolates the trade that crosses "
        f"the border without anyone moving. On the export side, **{top_names[0]}** and "
        f"**{top_names[1]}** together account for **{top2_share_exp:.0f}% of India's Mode 1 "
        f"services exports** in {year}. India's Mode 1 net balance is a "
        f"**\\${mode1_net:.0f}B surplus**: the IT-and-business-services duo earns "
        f"**+\\${surplus_two['net_busd'].sum():.0f}B** net between them, while Transport "
        f"(freight invoices and airline fees that Indian importers pay foreign carriers) "
        f"runs a **−\\${abs(transport_row['net_busd']):.0f}B** Mode 1 deficit that cancels "
        "much of those gains."
    )
    st.caption(
        "Note: \"Mode 1\" in WTO classification means the service is supplied across a "
        "border, including freight and passenger transport invoices. Transport's Mode 1 "
        "deficit here is shipping lines, airlines, and logistics providers, not "
        "platform-mediated digital trade. The platform-exposure story the dashboard "
        "tracks is concentrated in the top two bars (Telecoms/computer and Other business "
        "services), plus the IP licensing import flagged on the Overview."
    )

    diverge_chart = go.Figure()
    diverge_chart.add_trace(
        go.Bar(
            y=diverge["indicator_name"],
            x=diverge["exp_busd"],
            name="Exports",
            orientation="h",
            marker_color="#2e7bba",
            hovertemplate="<b>%{y}</b><br>Exports: $%{x:.2f}B<extra></extra>",
        )
    )
    diverge_chart.add_trace(
        go.Bar(
            y=diverge["indicator_name"],
            x=-diverge["imp_busd"],
            name="Imports",
            orientation="h",
            marker_color="#e07a5f",
            hovertemplate="<b>%{y}</b><br>Imports: $%{customdata:.2f}B<extra></extra>",
            customdata=diverge["imp_busd"],
        )
    )
    diverge_chart.update_layout(
        title=f"Services trade by category, India, {year} (Mode 1 only)",
        barmode="overlay",
        xaxis=dict(
            title="USD billion (imports left, exports right)",
            zeroline=True,
            zerolinewidth=1,
            zerolinecolor="#888",
        ),
        yaxis=dict(title=""),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=10, r=10, t=80, b=10),
    )
    st.plotly_chart(diverge_chart, width="stretch")

    st.divider()

    flow = st.radio(
        "Flow (mode mix and time series below)",
        options=["export", "import"],
        horizontal=True,
        key="svc_flow",
    )

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
    all_categories = mode_shares["indicator_name"].unique().tolist()
    m1_share = (
        mode_shares[mode_shares["mode"] == "Mode 1"]
        .set_index("indicator_name")["share_pct"]
        .reindex(all_categories, fill_value=0)
        .sort_values(ascending=True)
    )
    category_order = m1_share.index.tolist()

    most_digital = m1_share.idxmax()
    most_digital_pct = m1_share.max()

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
        title=(
            f"Services {flow}s mode share by category, India, {year} "
            "(sorted by Mode 1 share)"
        ),
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
    default_name = "Health services"
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
        title=(
            f"{chosen_name} {flow}s by mode of supply, India, "
            f"{year_min}-{year_max}"
        ),
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
