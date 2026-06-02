"""Generate site/data.js for the Guided Walkthrough static page.

Every figure on the page is computed here from the processed CSVs, never
hardcoded (DECISIONS Entry 005), so the prose, tiles and charts cannot drift
from the data. The exposure score uses the exact v0 formula from
views/exposure_index.py: two min-max-normalised components (MSME scale in the
mapped ISIC section(s), Mode 1 trade in USD billion), summed. The normalising
and summing happen client-side in walkthrough.js so the scatter, ranked bar
and table always agree; this script emits the raw components.

Run:  python scripts/build_site_data.py
Reads data/processed/*.csv ; writes site/data.js
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed"
OUT = ROOT / "site" / "data.js"

# Headline Udyam total (current). The only post-2021 figure used, from the
# MSME Annual Report 2024-25 Table 2.1. Mirrors UDYAM_TOTAL in views/msme_base.py.
UDYAM_TOTAL = 5_77_00_000  # 57.7 million

# Short labels for the exposure scatter/bar, keyed by EBOPS level-1 name.
SHORT = {
    "Transport": "Transport",
    "Tourism and business travel": "Tourism",
    "Health services": "Health",
    "Education services": "Education",
    "Construction": "Construction",
    "Insurance and financial services": "Insurance & finance",
    "Telecommunications, computer, information and audiovisual services": "Telecom/computer",
    "Other business services (excluding trade-related)": "Other business",
    "Heritage and recreational services": "Heritage & rec.",
    "Other personal services": "Personal services",
    "Trade-related services (Distribution)": "Distribution",
}


def load() -> dict[str, pd.DataFrame]:
    return {
        "dds": pd.read_csv(DATA / "dds_india.csv"),
        "tismos": pd.read_csv(DATA / "tismos_india.csv"),
        "crosswalk": pd.read_csv(DATA / "ebops_isic_crosswalk.csv"),
        "division": pd.read_csv(DATA / "msme_nic_division.csv"),
        "top5": pd.read_csv(DATA / "msme_nic_top5_msm.csv"),
    }


def dds_series(dds: pd.DataFrame):
    total = dds[dds["indicator"] == "DDS"]
    years = sorted(total["year"].unique().tolist())

    def series(flow: str) -> list[float]:
        s = total[total["flow"] == flow].set_index("year")["value_musd"]
        return [round(float(s.get(y, 0.0)), 2) for y in years]

    exp = series("export")
    imp = series("import")

    # IP-licensing fees paid (imports of SH) as a year series, for the tile and
    # finding. SH = "Charges for the use of intellectual property n.i.e."
    sh = dds[(dds["indicator"] == "SH") & (dds["flow"] == "import")].set_index("year")["value_musd"]
    ip_imp = [round(float(sh.get(y, 0.0)), 2) for y in years]

    return years, exp, imp, ip_imp


# Tidy chart labels for the DDS categories (the raw names are too long for a bar axis).
DDS_LABEL = {
    "SF": "Insurance & pension",
    "SG": "Financial services",
    "SH": "Charges for use of IP",
    "SI1": "Telecommunications",
    "SI2": "Computer services",
    "SI3": "Information services",
    "SJ": "Other business services",
    "SK": "Personal, cultural & rec.",
}


def dds_categories(dds: pd.DataFrame, year: int):
    """DDS category breakdown for one year, USD billion, exports + imports."""
    cats = dds[(dds["indicator"] != "DDS") & (dds["year"] == year)]
    rows = []
    for ind, grp in cats.groupby("indicator"):
        name = DDS_LABEL.get(ind, grp["indicator_name"].iloc[0])
        exp = grp.loc[grp["flow"] == "export", "value_musd"].sum() / 1000
        imp = grp.loc[grp["flow"] == "import", "value_musd"].sum() / 1000
        rows.append({"name": name, "exp": round(exp, 2), "imp": round(imp, 2)})
    rows.sort(key=lambda r: r["exp"], reverse=True)
    return rows


def isic_sections(division: pd.DataFrame):
    by_sec = (
        division.groupby(["isic_section", "isic_section_name"], as_index=False)["msme_count"]
        .sum()
        .sort_values("msme_count", ascending=False)
    )
    return [
        {"sec": r.isic_section, "name": r.isic_section_name, "count": int(r.msme_count)}
        for r in by_sec.itertuples()
    ]


def service_divisions(division: pd.DataFrame, top_n: int = 12):
    svc = (
        division[division["sector_type"] == "services"]
        .sort_values("msme_count", ascending=False)
        .head(top_n)
    )
    return [
        {"name": r.nic_2digit_name, "count": int(r.msme_count)}
        for r in svc.itertuples()
    ]


def mode_mix(tismos: pd.DataFrame, crosswalk: pd.DataFrame, year: int):
    """Real Mode 1-4 share of each level-1 EBOPS category, exports, latest year."""
    level1 = crosswalk[crosswalk["level"] == 1]
    codes = level1["ebops_code"].tolist()
    names = dict(zip(level1["ebops_code"], level1["ebops_name"]))
    sub = tismos[
        (tismos["indicator"].isin(codes))
        & (tismos["year"] == year)
        & (tismos["flow"] == "export")
    ]
    rows = []
    for code in codes:
        g = sub[sub["indicator"] == code]
        by_mode = g.groupby("mode")["value_musd"].sum()
        total = by_mode.sum()
        if total <= 0:
            continue
        rows.append(
            {
                "name": SHORT.get(names[code], names[code]),
                "m1": round(float(by_mode.get("Mode 1", 0)) / total * 100, 1),
                "m2": round(float(by_mode.get("Mode 2", 0)) / total * 100, 1),
                "m3": round(float(by_mode.get("Mode 3", 0)) / total * 100, 1),
                "m4": round(float(by_mode.get("Mode 4", 0)) / total * 100, 1),
            }
        )
    rows.sort(key=lambda r: r["m1"])
    return rows


def exposure(tismos: pd.DataFrame, crosswalk: pd.DataFrame, division: pd.DataFrame, year: int):
    """Raw exposure components per EBOPS level-1 category (v0 formula inputs).

    Mirrors views/exposure_index.py: MSME count summed across the mapped ISIC
    section(s) (SJXSJ34 -> L+M+N), Mode 1 trade = export+import in USD billion.
    walkthrough.js min-max normalises and sums these into the score.
    """
    level1 = crosswalk[crosswalk["level"] == 1]
    rows = []
    for c in level1.itertuples():
        sections = [s.strip() for s in c.isic_section.split("+")]
        msme = int(division[division["isic_section"].isin(sections)]["msme_count"].sum())
        mask = (
            (tismos["indicator"] == c.ebops_code)
            & (tismos["mode"] == "Mode 1")
            & (tismos["year"] == year)
            & (tismos["flow"].isin(["export", "import"]))
        )
        trade = round(float(tismos.loc[mask, "value_musd"].sum()) / 1000, 2)
        rows.append(
            {
                "cat": c.ebops_name,
                "short": SHORT.get(c.ebops_name, c.ebops_name),
                "isic": c.isic_section,
                "msme": msme,
                "trade": trade,
            }
        )
    rows.sort(key=lambda r: r["trade"] + r["msme"] / 1e6, reverse=True)
    return rows


def obs_composition(division: pd.DataFrame):
    """NIC 2-digit divisions inside 'Other business services' (ISIC L+M+N).

    The top exposure row, EBOPS SJXSJ34, maps to three ISIC sections at once.
    This unpacks what actually sits behind that firm count so the conclusion
    names concrete sectors rather than an opaque label.
    """
    lmn = division[division["isic_section"].isin(["L", "M", "N"])]
    total = int(lmn["msme_count"].sum())
    rows = [
        {
            "div": int(r.nic_2digit),
            "name": r.nic_2digit_name,
            "isic": r.isic_section,
            "count": int(r.msme_count),
        }
        for r in lmn.sort_values("msme_count", ascending=False).itertuples()
    ]
    return {"total": total, "divisions": rows}


# Constructed disaggregation of "Other business services" (SJXSJ34) into its
# EBOPS sub-codes, each paired with the NIC 2-digit division(s) that produce it.
# The published WTO crosswalk stops at the lumped L+M+N parent; this finer
# sub-code -> NIC mapping is constructed for this analysis. It is clean for the
# professional cluster; SJ35 is a mixed residual; SJ1 (R&D) maps to NIC 72,
# which is absent from the Sep 2021 top-50 cut (zero firms by omission). Real
# estate (NIC 68, ISIC L) has no Mode 1 trade sub-code and is left out.
# Sub-codes chosen so they sum to the parent: SJXSJ34 = SJ21 + SJ22 + SJ31 + SJ1 + SJ35.
OBS_SUBCODES = [
    {"code": "SJ21", "label": "Legal, accounting & management consulting", "divs": [69, 70], "kind": "clean"},
    {"code": "SJ31", "label": "Architecture, engineering & technical", "divs": [71], "kind": "clean"},
    {"code": "SJ22", "label": "Advertising & market research", "divs": [73], "kind": "clean"},
    {"code": "SJ1", "label": "Research & development", "divs": [72], "kind": "gap"},
    {"code": "SJ35", "label": "Other business services n.i.e.", "divs": [74, 77, 78, 79, 81, 82], "kind": "residual"},
]


def obs_subexposure(tismos: pd.DataFrame, division: pd.DataFrame, year: int):
    """Raw sub-exposure components per EBOPS sub-code of Other business services.

    Mode 1 trade comes straight from TiSMoS; the firm count is summed over the
    constructed NIC mapping above. walkthrough.js min-max normalises within this
    group and sums, mirroring the main index one level down. The kind flag drives
    the honesty labels in the prose (clean / residual / coverage gap).
    """
    rows = []
    for s in OBS_SUBCODES:
        mask = (
            (tismos["indicator"] == s["code"])
            & (tismos["mode"] == "Mode 1")
            & (tismos["year"] == year)
            & (tismos["flow"].isin(["export", "import"]))
        )
        trade = round(float(tismos.loc[mask, "value_musd"].sum()) / 1000, 2)
        msme = int(division[division["nic_2digit"].isin(s["divs"])]["msme_count"].sum())
        rows.append(
            {"code": s["code"], "label": s["label"], "kind": s["kind"], "msme": msme, "trade": trade}
        )
    return rows


def obs_trend(tismos: pd.DataFrame):
    """Mode 1 export series for the two children of Other business services.

    Professional & management consulting (SJ2) against the technical / other
    remainder (SJ3), 2005 to the latest TiSMoS year. Shows the category flip is
    almost entirely a consulting story. Values in USD million.
    """
    years = sorted(tismos["year"].unique().tolist())

    def series(code: str) -> list[float]:
        sub = tismos[
            (tismos["indicator"] == code)
            & (tismos["mode"] == "Mode 1")
            & (tismos["flow"] == "export")
        ].set_index("year")["value_musd"]
        return [round(float(sub.get(y, 0.0)), 2) for y in years]

    return {"years": years, "consulting": series("SJ2"), "technical": series("SJ3")}


def size_split(top5: pd.DataFrame):
    return [
        {
            "name": r.nic_2digit_name,
            "micro": int(r.micro),
            "small": int(r.small),
            "medium": int(r.medium),
        }
        for r in top5.sort_values("total", ascending=False).itertuples()
    ]


def main() -> None:
    d = load()
    dds, tismos, crosswalk, division, top5 = (
        d["dds"], d["tismos"], d["crosswalk"], d["division"], d["top5"]
    )

    dds_year = int(dds["year"].max())
    tismos_year = int(tismos["year"].max())
    years, dds_exp, dds_imp, ip_imp = dds_series(dds)

    mfg = division[division["sector_type"] == "manufacturing"]
    svc = division[division["sector_type"] == "services"]
    mfg_total = int(mfg["msme_count"].sum())
    svc_total = int(svc["msme_count"].sum())
    sector_cut = mfg_total + svc_total

    data = {
        "meta": {
            "ddsYear": dds_year,
            "tismosYear": tismos_year,
            "udyamTotal": UDYAM_TOTAL,
            "sectorCut": sector_cut,
            "mfgTotal": mfg_total,
            "svcTotal": svc_total,
            "mfgDivs": int(mfg["nic_2digit"].nunique()),
            "svcDivs": int(svc["nic_2digit"].nunique()),
        },
        "years": years,
        "ddsExp": dds_exp,
        "ddsImp": dds_imp,
        "ipImp": ip_imp,
        "cat2025": dds_categories(dds, dds_year),
        "isicSection": isic_sections(division),
        "svcDiv": service_divisions(division),
        "modeMix": mode_mix(tismos, crosswalk, tismos_year),
        "exposure": exposure(tismos, crosswalk, division, tismos_year),
        "obsComposition": obs_composition(division),
        "obsSubExposure": obs_subexposure(tismos, division, tismos_year),
        "obsTrend": obs_trend(tismos),
        "sizeSplit": size_split(top5),
    }

    payload = json.dumps(data, indent=2, ensure_ascii=False)
    header = (
        "/* AUTO-GENERATED by scripts/build_site_data.py from data/processed/*.csv.\n"
        "   Do not edit by hand. Every figure is computed from the source CSVs so\n"
        "   the page never drifts from the data. Exposure scores are min-max\n"
        "   normalised and summed in walkthrough.js (the v0 formula). */\n"
    )
    OUT.write_text(header + "window.DATA = " + payload + ";\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    print(f"  DDS {years[0]}-{dds_year}, TiSMoS to {tismos_year}")
    print(f"  exposure rows: {len(data['exposure'])}, mode-mix rows: {len(data['modeMix'])}")
    ip_growth = ip_imp[-1] / ip_imp[0] if ip_imp[0] else float("nan")
    print(f"  IP imports {dds_year}: ${ip_imp[-1]/1000:.1f}B  ({ip_growth:.1f}x since {years[0]})")
    print(f"  net surplus {dds_year}: ${(dds_exp[-1]-dds_imp[-1])/1000:.1f}B  "
          f"(from ${(dds_exp[0]-dds_imp[0])/1000:.1f}B in {years[0]})")


if __name__ == "__main__":
    main()
