from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

DATA = Path(__file__).resolve().parents[1] / "data" / "processed"

# Current Udyam registrations as of 31 Dec 2024, from MSME Annual Report
# 2024-25 Table 2.1. The sector cut on this page is frozen at Sep 2021
# (Bulletin VII); this headline number is the only piece of post-2021 data
# used and is shown for context.
UDYAM_TOTAL_DEC_2024 = 5_77_00_000  # 5.77 crore

SECTOR_COLORS = {
    "manufacturing": "#e07a5f",
    "services": "#2e7bba",
}

SIZE_COLORS = {
    "micro": "#1f4e79",
    "small": "#4a90c2",
    "medium": "#9ec5e0",
}


@st.cache_data
def load_division() -> pd.DataFrame:
    return pd.read_csv(DATA / "msme_nic_division.csv")


@st.cache_data
def load_top5_msm() -> pd.DataFrame:
    return pd.read_csv(DATA / "msme_nic_top5_msm.csv")


def render() -> None:
    division = load_division()
    top5 = load_top5_msm()

    bulletin_covered = int(division["msme_count"].sum())
    mfg_total = int(division[division["sector_type"] == "manufacturing"]["msme_count"].sum())
    svc_total = int(division[division["sector_type"] == "services"]["msme_count"].sum())

    st.subheader("MSME Base: where India's small businesses concentrate")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Udyam registrations", f"{UDYAM_TOTAL_DEC_2024/1e7:.2f} cr", "as of 31 Dec 2024")
    c2.metric("In this sector cut", f"{bulletin_covered/1e5:.1f} L", "Sep 2021, top-50 codes")
    c3.metric("Manufacturing", f"{mfg_total/1e5:.1f} L", "across 19 divisions")
    c4.metric("Services", f"{svc_total/1e5:.1f} L", "across 24 divisions")

    st.markdown(
        "India's Udyam registration system has accumulated **5.77 crore** MSME "
        "registrations as of 31 December 2024, per the MSME Annual Report 2024-25. "
        "That headline total is the only post-2021 figure on this page. The sectoral "
        "cuts below come from Udyam Bulletin VII (cutoff 30 September 2021), which "
        "is the most granular sector breakdown MoMSME has published. Bulletin VII "
        "lists the **top 50 NIC 5-digit codes** in manufacturing and the **top 50 in "
        "services**; rolled up to NIC 2-digit division, this captures roughly 78% of "
        f"the ~50 lakh registrations as of that date. Of those, "
        f"**{mfg_total/1e5:.1f} lakh sit in manufacturing divisions** and "
        f"**{svc_total/1e5:.1f} lakh in services divisions**. The Micro/Small/Medium "
        "split is published only for the five largest divisions; everything else is "
        "totals only."
    )

    st.divider()

    st.markdown("##### Top divisions by MSME count")
    st.markdown(
        "Each bar is a NIC 2-digit division, sorted by Udyam-registered MSME count "
        "as of September 2021. Bars on the right are services; bars on the left are "
        "manufacturing. The dashboard's exposure question lives in the services side: "
        "this is where digitally tradeable activity concentrates."
    )

    top_n = st.slider(
        "How many divisions to show on each side",
        min_value=5,
        max_value=20,
        value=12,
        step=1,
        key="msme_top_n",
    )

    mfg = (
        division[division["sector_type"] == "manufacturing"]
        .sort_values("msme_count", ascending=False)
        .head(top_n)
    )
    svc = (
        division[division["sector_type"] == "services"]
        .sort_values("msme_count", ascending=False)
        .head(top_n)
    )

    col_mfg, col_svc = st.columns(2)
    with col_mfg:
        mfg_chart = px.bar(
            mfg.sort_values("msme_count", ascending=True),
            x="msme_count",
            y="nic_2digit_name",
            orientation="h",
            title=f"Manufacturing, top {len(mfg)} divisions",
            labels={"msme_count": "MSME count (Sep 2021)", "nic_2digit_name": ""},
            color_discrete_sequence=[SECTOR_COLORS["manufacturing"]],
            hover_data={"nic_2digit": True, "isic_section_name": True},
        )
        mfg_chart.update_layout(
            showlegend=False,
            margin=dict(l=10, r=10, t=60, b=10),
            yaxis=dict(automargin=True),
        )
        st.plotly_chart(mfg_chart, width="stretch")

    with col_svc:
        svc_chart = px.bar(
            svc.sort_values("msme_count", ascending=True),
            x="msme_count",
            y="nic_2digit_name",
            orientation="h",
            title=f"Services, top {len(svc)} divisions",
            labels={"msme_count": "MSME count (Sep 2021)", "nic_2digit_name": ""},
            color_discrete_sequence=[SECTOR_COLORS["services"]],
            hover_data={"nic_2digit": True, "isic_section_name": True},
        )
        svc_chart.update_layout(
            showlegend=False,
            margin=dict(l=10, r=10, t=60, b=10),
            yaxis=dict(automargin=True),
        )
        st.plotly_chart(svc_chart, width="stretch")

    st.divider()

    st.markdown("##### Where MSMEs sit by ISIC section")
    st.markdown(
        "Rolling the same divisions up one more level: each NIC 2-digit division "
        "maps to one ISIC Rev 4 section (e.g. division 62, *Computer programming and "
        "consultancy*, sits in section **J Information and Communication**). This is "
        "the join that lets MSME counts line up with the EBOPS service categories "
        "the Service Categories page tracks. Sections **J** (ICT), **K** (Finance), "
        "**M** (Professional/scientific), and **N** (Admin/support) are the ones "
        "that carry most of India's digital services trade; their MSME bases here "
        "are what the Exposure Index page combines with trade values."
    )

    by_section = (
        division.groupby(["isic_section", "isic_section_name"], as_index=False)
        .agg(msme_count=("msme_count", "sum"), num_divisions=("nic_2digit", "count"))
        .sort_values("msme_count", ascending=True)
    )
    by_section["label"] = by_section["isic_section"] + " " + by_section["isic_section_name"]
    section_chart = px.bar(
        by_section,
        x="msme_count",
        y="label",
        orientation="h",
        title="MSME count by ISIC section, Sep 2021 (top-50 5-digit codes rolled up)",
        labels={"msme_count": "MSME count", "label": ""},
        color_discrete_sequence=["#5b8a72"],
    )
    section_chart.update_layout(
        showlegend=False,
        margin=dict(l=10, r=10, t=60, b=10),
        yaxis=dict(automargin=True),
    )
    st.plotly_chart(section_chart, width="stretch")

    st.divider()

    st.markdown("##### The only size split MoMSME publishes")
    micro_pct = top5["micro"].sum() / top5["total"].sum() * 100
    small_pct = top5["small"].sum() / top5["total"].sum() * 100
    medium_pct = top5["medium"].sum() / top5["total"].sum() * 100
    st.markdown(
        "Bulletin VII Section 15 publishes a Micro/Small/Medium breakdown for **five "
        "divisions only**: the five largest by total registrations. The skew is the "
        f"story: across all five, **micro enterprises** account for **{micro_pct:.0f}%** "
        f"of registrations, small for **{small_pct:.0f}%**, and medium for under "
        f"**{max(1, round(medium_pct))}%**. MoMSME does not publish this cut for any "
        "other division. A v2 of this page would replace this with a full NIC 2-digit "
        "by size table if an RTI request succeeds in producing one."
    )

    long = top5.melt(
        id_vars=["nic_2digit", "nic_2digit_name", "total", "isic_section", "isic_section_name"],
        value_vars=["micro", "small", "medium"],
        var_name="size",
        value_name="count",
    )
    long["size"] = pd.Categorical(long["size"], categories=["micro", "small", "medium"], ordered=True)
    long = long.sort_values(["total", "size"], ascending=[True, True])

    size_chart = px.bar(
        long,
        x="count",
        y="nic_2digit_name",
        color="size",
        orientation="h",
        title="Top 5 NIC divisions by MSME count, with Micro/Small/Medium split (Sep 2021)",
        labels={"count": "MSME count", "nic_2digit_name": "", "size": ""},
        category_orders={
            "nic_2digit_name": long.drop_duplicates("nic_2digit_name")["nic_2digit_name"].tolist(),
            "size": ["micro", "small", "medium"],
        },
        color_discrete_map=SIZE_COLORS,
    )
    size_chart.update_layout(
        barmode="stack",
        margin=dict(l=10, r=10, t=60, b=10),
        yaxis=dict(automargin=True),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(size_chart, width="stretch")

    st.divider()
    st.caption(
        "**Source:** MoMSME Udyam Bulletin VII, Annexures 3A and 3B (top-50 NIC "
        "5-digit codes for manufacturing and services) and Section 15 Figure 28 "
        "(Micro/Small/Medium split for top 5 divisions), cutoff 30 September 2021. "
        "Current Udyam registration total from MSME Annual Report 2024-25 Table 2.1. "
        "Bulletin VII source figures are transcribed in `scripts/build_msme_nic.py` "
        "and rolled up to `data/processed/msme_nic_division.csv` and "
        "`data/processed/msme_nic_top5_msm.csv`. NIC 2-digit to ISIC Rev 4 section "
        "mapping follows NIC 2008 (which aligns with ISIC Rev 4 structure). MoMSME "
        "does not publish a full NIC 2-digit by enterprise-size cross-tab; the cuts "
        "above are everything that is in the public record."
    )


if __name__ == "__main__":
    render()
