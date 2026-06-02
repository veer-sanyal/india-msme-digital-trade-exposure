# Data

This project uses two raw WTO datasets. The raw files are **not committed to git**; they total ~150 MB and are reproducible from the original sources. The cleaned India slices under `data/processed/` *are* committed and are what the site is built from.

## Folder layout

```
data/
├── raw/                                       # gitignored, you download these
│   ├── wto_dds/
│   │   └── dds_bulk_download.csv
│   ├── wto_tismos/
│   │   ├── tismos_exports.csv
│   │   ├── tismos_imports.csv
│   │   └── tismos_items_and_correspondence.xlsx
│   └── msme_udyam/
│       └── Bulletin-VII.pdf
└── processed/                                 # committed, built by the script
    ├── dds_india.csv
    ├── tismos_india.csv
    ├── ebops_isic_crosswalk.csv
    ├── msme_nic_5digit.csv
    ├── msme_nic_division.csv
    └── msme_nic_top5_msm.csv
```

## Downloading the raw data

### 1. WTO Digitally Delivered Services (DDS)

- Page: https://data.wto.org/en/dataset/wto-digitally-delivered-services-trade-dataset
- Click **Download Full Dataset** (Excel file, zipped).
- Unzip; place the bulk CSV at `data/raw/wto_dds/dds_bulk_download.csv`.

### 2. WTO Trade in Services by Mode of Supply (TiSMoS)

- Page: https://data.wto.org/en/dataset/tismos
- Click **Download Full Dataset** (Excel file, zipped). The archive contains separate exports and imports CSVs plus an items/correspondence workbook.
- Place them at:
  - `data/raw/wto_tismos/tismos_exports.csv`
  - `data/raw/wto_tismos/tismos_imports.csv`
  - `data/raw/wto_tismos/tismos_items_and_correspondence.xlsx`

### 3. MSME Udyam Registration Bulletin VII

- Page: https://dcmsme.gov.in/Buletin-VII-Analysis-of-Udyam-Registration-Data.pdf
- The bulletin is the Office of Development Commissioner (MSME)'s "Analysis of Udyam Registration Data", dated 13 Oct 2021, covering registrations through 30 Sep 2021.
- Save it at `data/raw/msme_udyam/Bulletin-VII.pdf`.
- The build script does not parse the PDF directly; the relevant tables (Annexures 3A and 3B and Section 15) are transcribed into `scripts/build_msme_nic.py` since the source is a frozen historical document. The PDF is kept locally for verification only.

## Building the processed slices

From the repo root:

```
python scripts/build_processed.py
python scripts/build_msme_nic.py
```

This produces the files under `data/processed/`. Expected row counts:

| File | Rows |
|---|---|
| `dds_india.csv` | 378 |
| `tismos_india.csv` | 7,920 |
| `ebops_isic_crosswalk.csv` | 12 |
| `msme_nic_5digit.csv` | 100 |
| `msme_nic_division.csv` | 43 |
| `msme_nic_top5_msm.csv` | 5 |

The script is deterministic; re-running it from the same raw inputs yields identical output.

## What the datasets cover

| Dataset | Years | Modes | Categories | Partner |
|---|---|---|---|---|
| DDS | 2005-2025 | Mode 1 only | 8 | World only |
| TiSMoS | 2005-2022 | All 4 GATS modes | 55 | World only |
| MSME Udyam | cutoff 30 Sep 2021 | n/a | NIC 5-digit (top 50 mfg + top 50 svc) and NIC 2-digit (top 5 with size split) | India only |

No bilateral (country-to-country) data is available in either WTO dataset. All flows are reported against "World" as the partner.

### MSME data limitations

MoMSME does not publish a full NIC 2-digit by Micro/Small/Medium cross-tab; the only published splits are (a) the top 5 NIC 2-digit divisions by size in Bulletin VII Section 15, and (b) totals (no size split) for the top 50 NIC 5-digit codes in each of manufacturing and services. The current totals (5.77 crore registrations as of 31 Dec 2024) come from the MSME Annual Report 2024-25 Table 2.1 and are used for headline figures only; sector-level cuts come from Bulletin VII and so reflect the Sep 2021 distribution.

### How the MSME slices are built

`scripts/build_msme_nic.py` is self-contained: the source tables are transcribed inline from Bulletin VII (the PDF in `data/raw/msme_udyam/` is kept for verification only). Three outputs:

| File | Rows | Source | What it is |
|---|---|---|---|
| `msme_nic_5digit.csv` | 100 | Bulletin VII Annexures 3A and 3B | Top 50 NIC 5-digit codes for manufacturing and top 50 for services, with totals. No Micro/Small/Medium split (the bulletin does not publish one at this level). |
| `msme_nic_division.csv` | 43 | Aggregated from `msme_nic_5digit.csv` | NIC 2-digit division totals (sum across all 5-digit codes that landed in the top 50 for that division), with the ISIC Rev 4 section the division belongs to. |
| `msme_nic_top5_msm.csv` | 5 | Bulletin VII Section 15 (Figure 28) | The five NIC 2-digit divisions (10, 49, 56, 96, 32) for which the bulletin actually does publish a Micro/Small/Medium split. |

The rollup uses two mappings, both encoded as constants in the build script:

1. **NIC 5-digit to NIC 2-digit:** floor-divide the code by 1000 (e.g. 62099 → 62, "Other information technology and computer service activities"). NIC 2-digit division names follow NIC 2008.
2. **NIC 2-digit to ISIC section:** range-based mapping that mirrors ISIC Rev 4 (e.g. NIC 58-63 → ISIC J Information and Communication, NIC 64-66 → ISIC K Finance). This is the join key that connects MSME counts to the `ebops_isic_crosswalk.csv` produced from the WTO TiSMoS workbook, so MSME sector counts line up with the same service categories the Overview page uses.

Reading the outputs together: `msme_nic_division.csv` is the primary table for sectoral exposure scoring; `msme_nic_top5_msm.csv` is the only place a Micro/Small/Medium split exists at sector level and is useful for narrative ("X% of MSMEs in food products are micro" type statements) but cannot be generalised to other divisions; `msme_nic_5digit.csv` is the underlying detail if a 5-digit cut is ever needed.

The top-100 underlying codes (50 mfg + 50 svc) cover about 78% of the ~50 lakh MSMEs registered by Sep 2021, so the division-level table is a good but not complete picture of the distribution. Divisions whose top-N codes did not crack the top-50 list are absent from `msme_nic_division.csv`; this is a known gap inherent to the published source.
