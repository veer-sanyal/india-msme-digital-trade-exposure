from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

DATA = Path(__file__).resolve().parents[1] / "data" / "processed"


@st.cache_data
def load_tismos() -> pd.DataFrame:
    return pd.read_csv(DATA / "tismos_india.csv")


@st.cache_data
def load_crosswalk() -> pd.DataFrame:
    return pd.read_csv(DATA / "ebops_isic_crosswalk.csv")


@st.cache_data
def load_division() -> pd.DataFrame:
    return pd.read_csv(DATA / "msme_nic_division.csv")


def _msme_count_for_sections(division: pd.DataFrame, section_field: str) -> int:
    """Sum MSME counts across the ISIC section(s) named in the crosswalk row.

    `SJXSJ34` maps to "L+M+N", a combined three-section group. Every other
    level-1 EBOPS code maps to a single section letter. Parsing the field
    as `+`-separated lets both cases share one path.
    """
    section_codes = [s.strip() for s in section_field.split("+")]
    return int(division[division["isic_section"].isin(section_codes)]["msme_count"].sum())


def _mode1_trade_busd(tismos: pd.DataFrame, ebops_code: str, year: int) -> float:
    mask = (
        (tismos["indicator"] == ebops_code)
        & (tismos["mode"] == "Mode 1")
        & (tismos["year"] == year)
        & (tismos["flow"].isin(["export", "import"]))
    )
    return float(tismos.loc[mask, "value_musd"].sum()) / 1000


def _normalize(series: pd.Series) -> pd.Series:
    lo, hi = series.min(), series.max()
    if hi == lo:
        return pd.Series([0.0] * len(series), index=series.index)
    return (series - lo) / (hi - lo)


def render() -> None:
    tismos = load_tismos()
    crosswalk = load_crosswalk()
    division = load_division()

    year = int(tismos["year"].max())
    level1 = crosswalk[crosswalk["level"] == 1].copy()

    rows = []
    for _, c in level1.iterrows():
        msme = _msme_count_for_sections(division, c["isic_section"])
        trade = _mode1_trade_busd(tismos, c["ebops_code"], year)
        rows.append(
            {
                "ebops_code": c["ebops_code"],
                "ebops_name": c["ebops_name"],
                "isic_section": c["isic_section"],
                "isic_section_name": c["isic_section_name"],
                "msme_count": msme,
                "trade_busd": trade,
            }
        )
    score = pd.DataFrame(rows)
    score["msme_norm"] = _normalize(score["msme_count"])
    score["trade_norm"] = _normalize(score["trade_busd"])
    score["exposure_score"] = score["msme_norm"] + score["trade_norm"]
    score = score.sort_values("exposure_score", ascending=False).reset_index(drop=True)
    score.insert(0, "rank", score.index + 1)

    st.subheader("Exposure Index v0: MSME base meets digital trade")

    st.markdown(
        "This page joins the MSME base (Sep 2021 Bulletin VII, rolled to ISIC section) "
        "to India's Mode 1 services trade (WTO TiSMoS, latest year available: "
        f"**{year}**). One row per EBOPS level-1 service category. The score is the "
        "sum of two min-max-normalised components, each in [0, 1]:"
    )
    st.markdown(
        "1. **MSME scale.** Number of Udyam-registered MSMEs in the ISIC section(s) "
        "this EBOPS category maps to. Larger MSME base means more firms exposed to "
        "whatever happens in that trade flow.\n"
        "2. **Mode 1 trade intensity.** Sum of India's Mode 1 exports and imports "
        f"in this category in {year}, in USD billions. Larger Mode 1 flow means more "
        "of this category's activity is happening through the digital cross-border "
        "channel where platforms and policy operate."
    )
    st.markdown(
        "v0 is deliberately two components only. Digital adoption (planned third "
        "component) is dropped until ASUSE 2023-24 figures are pulled and verified. "
        "Policy sensitivity (planned fourth component) waits on OECD Digital STRI in "
        "Week 4. The score formula itself is the open methodology question, written "
        "up in DECISIONS.md Entry 008. Read the ranked table as *direction*, not "
        "calibrated magnitude."
    )

    st.divider()

    st.markdown(f"##### Ranked exposure, {year}")

    bar = px.bar(
        score.sort_values("exposure_score", ascending=True),
        x="exposure_score",
        y="ebops_name",
        orientation="h",
        color="trade_norm",
        color_continuous_scale="Blues",
        labels={
            "exposure_score": "Exposure score (0 to 2, higher = more exposed)",
            "ebops_name": "",
            "trade_norm": "Trade intensity",
        },
        title=f"India MSME digital trade exposure by EBOPS category, {year}",
        hover_data={
            "isic_section": True,
            "msme_count": ":,",
            "trade_busd": ":.2f",
            "msme_norm": ":.2f",
            "trade_norm": ":.2f",
            "exposure_score": ":.2f",
            "ebops_name": False,
        },
    )
    bar.update_layout(
        margin=dict(l=10, r=10, t=60, b=10),
        yaxis=dict(automargin=True),
        coloraxis_colorbar=dict(title="Trade<br>intensity", thickness=12),
    )
    st.plotly_chart(bar, width="stretch")

    top = score.iloc[0]
    second = score.iloc[1]
    st.markdown(
        f"**Top of the ranking:** *{top['ebops_name']}* (ISIC {top['isic_section']}). "
        f"MSME base of **{top['msme_count']:,}** firms in the relevant ISIC section(s) "
        f"and **${top['trade_busd']:.1f}B** in Mode 1 trade in {year}. Second is "
        f"*{second['ebops_name']}* (ISIC {second['isic_section']}) at "
        f"**{second['msme_count']:,}** firms and **${second['trade_busd']:.1f}B**. "
        "These are the categories where the dashboard's policy-scenario layer (Phase B) "
        "will move the most when STRI components and scenario toggles are added."
    )

    st.divider()

    st.markdown("##### Score table")
    display = score[
        [
            "rank",
            "ebops_name",
            "isic_section",
            "msme_count",
            "trade_busd",
            "msme_norm",
            "trade_norm",
            "exposure_score",
        ]
    ].rename(
        columns={
            "ebops_name": "EBOPS category",
            "isic_section": "ISIC section(s)",
            "msme_count": "MSME count (Sep 2021)",
            "trade_busd": f"Mode 1 trade ({year}, $B)",
            "msme_norm": "MSME scale (0-1)",
            "trade_norm": "Trade intensity (0-1)",
            "exposure_score": "Exposure score (0-2)",
        }
    )
    st.dataframe(
        display,
        hide_index=True,
        width="stretch",
        column_config={
            "MSME count (Sep 2021)": st.column_config.NumberColumn(format="%d"),
            f"Mode 1 trade ({year}, $B)": st.column_config.NumberColumn(format="%.2f"),
            "MSME scale (0-1)": st.column_config.NumberColumn(format="%.2f"),
            "Trade intensity (0-1)": st.column_config.NumberColumn(format="%.2f"),
            "Exposure score (0-2)": st.column_config.NumberColumn(format="%.2f"),
        },
    )

    st.divider()

    st.markdown("##### Known issues with this score (read before quoting it)")
    st.markdown(
        "- **EBOPS-to-ISIC is not one-to-one.** *Other business services* (SJXSJ34) "
        "maps to **three** ISIC sections combined (L, M, N), per the WTO TiSMoS "
        "items-and-correspondence workbook. The MSME scale for that row sums "
        "across all three sections, which gives it a structural advantage on the "
        "MSME side. A v2 would either disaggregate Other Business Services into "
        "its EBOPS sub-codes or split the MSME count across sections.\n"
        "- **Two structurally different quantities are being summed.** MSME scale "
        "is a count of firms. Trade intensity is USD billion. Min-max normalising "
        "puts them on a [0, 1] axis but does not make the addition meaningful in "
        "any economic sense. This is the question Entry 008 is about.\n"
        "- **Top-50 NIC code coverage gap.** ISIC sections whose constituent NIC "
        "divisions did not crack Bulletin VII's top-50 lists are missing from the "
        "MSME side, so their MSME scale is zero by omission, not by absence.\n"
        f"- **Time mismatch.** MSME counts are Sep 2021. Trade values are {year}. "
        "Small mismatch in this version; will widen as MSME data ages."
    )

    st.divider()
    st.caption(
        f"**Sources:** Mode 1 trade values from WTO TiSMoS {year}, summed across "
        "export and import flows. MSME counts from Udyam Bulletin VII (cutoff 30 Sep "
        "2021), rolled from NIC 2-digit divisions to ISIC Rev 4 sections via NIC 2008. "
        "EBOPS-to-ISIC mapping from `data/processed/ebops_isic_crosswalk.csv`, derived "
        "from the WTO TiSMoS items-and-correspondence workbook. Bilateral country-level "
        "cuts are not available; both trade datasets report against World aggregate."
    )


if __name__ == "__main__":
    render()
