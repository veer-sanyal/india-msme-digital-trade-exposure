# Data

This project uses two raw WTO datasets. The raw files are **not committed to git** — they total ~150 MB and are reproducible from the original sources. The cleaned India slices under `data/processed/` *are* committed and are what the Streamlit app loads.

## Folder layout

```
data/
├── raw/                                       # gitignored, you download these
│   ├── wto_dds/
│   │   └── dds_bulk_download.csv
│   └── wto_tismos/
│       ├── tismos_exports.csv
│       ├── tismos_imports.csv
│       └── tismos_items_and_correspondence.xlsx
└── processed/                                 # committed, built by the script
    ├── dds_india.csv
    ├── tismos_india.csv
    └── ebops_isic_crosswalk.csv
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

## Building the processed slices

From the repo root:

```
python scripts/build_processed.py
```

This produces the three files under `data/processed/`. Expected row counts:

| File | Rows |
|---|---|
| `dds_india.csv` | 378 |
| `tismos_india.csv` | 7,920 |
| `ebops_isic_crosswalk.csv` | 12 |

The script is deterministic — re-running it from the same raw inputs yields identical output.

## What the datasets cover

| Dataset | Years | Modes | Categories | Partner |
|---|---|---|---|---|
| DDS | 2005-2025 | Mode 1 only | 8 | World only |
| TiSMoS | 2005-2022 | All 4 GATS modes | 55 | World only |

No bilateral (country-to-country) data is available in either. All flows are reported against "World" as the partner.
