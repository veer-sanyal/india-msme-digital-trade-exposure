"""Build India-only processed slices from WTO DDS + TiSMoS raw data.

Run from repo root:
    python scripts/build_processed.py
"""

from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
RAW = REPO / "data" / "raw"
OUT = REPO / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)

FLOW_MAP = {"X": "export", "M": "import"}


def build_dds_india() -> pd.DataFrame:
    df = pd.read_csv(RAW / "wto_dds" / "dds_bulk_download.csv", low_memory=False)
    india = (
        df[df["REPORTER_NAME"] == "India"]
        .drop(columns=["REPORTER_CODE", "PARTNER", "MODE", "UNIT", "BREAKING_SERIES"])
        .rename(
            columns={
                "FLOW": "flow",
                "REPORTER_NAME": "reporter",
                "YEAR": "year",
                "INDICATOR": "indicator",
                "INDICATOR_NAME": "indicator_name",
                "VALUE": "value_musd",
            }
        )
        .assign(flow=lambda d: d["flow"].map(FLOW_MAP))
        .sort_values(["flow", "indicator", "year"])
        .reset_index(drop=True)
    )
    india.to_csv(OUT / "dds_india.csv", index=False)
    return india


def build_tismos_india() -> pd.DataFrame:
    parts = []
    for name in ("tismos_exports.csv", "tismos_imports.csv"):
        df = pd.read_csv(RAW / "wto_tismos" / name, low_memory=False)
        parts.append(df[df["REPORTER_NAME"] == "India"])
    india = (
        pd.concat(parts, ignore_index=True)
        .drop(columns=["REPORTER_CODE", "PARTNER", "UNIT"])
        .rename(
            columns={
                "FLOW": "flow",
                "REPORTER_NAME": "reporter",
                "YEAR": "year",
                "INDICATOR": "indicator",
                "INDICATOR_NAME": "indicator_name",
                "MODE": "mode",
                "VALUE": "value_musd",
            }
        )
        .assign(flow=lambda d: d["flow"].map(FLOW_MAP))
        .sort_values(["flow", "mode", "indicator", "year"])
        .reset_index(drop=True)
    )
    india.to_csv(OUT / "tismos_india.csv", index=False)
    return india


def build_crosswalk() -> pd.DataFrame:
    corr = pd.read_excel(
        RAW / "wto_tismos" / "tismos_items_and_correspondence.xlsx"
    )
    crosswalk = (
        corr.rename(
            columns={
                "EBOPS-like code": "ebops_code",
                "level": "level",
                "Description of EBOPS-like code": "ebops_name",
                "ISIC rev. 4 section code": "isic_section",
                "Description": "isic_section_name",
            }
        )
        .dropna(subset=["isic_section"])
        .reset_index(drop=True)
    )
    crosswalk.to_csv(OUT / "ebops_isic_crosswalk.csv", index=False)
    return crosswalk


def main() -> None:
    dds = build_dds_india()
    tismos = build_tismos_india()
    crosswalk = build_crosswalk()
    print(f"dds_india.csv             {len(dds):>6} rows")
    print(f"tismos_india.csv          {len(tismos):>6} rows")
    print(f"ebops_isic_crosswalk.csv  {len(crosswalk):>6} rows")


if __name__ == "__main__":
    main()
