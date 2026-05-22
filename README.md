# India Digital Services Trade Exposure Dashboard

An interactive dashboard that connects India's digital services trade data with MSME sector data to show which small businesses are most exposed to global digital platforms, cloud services, and digital trade policy changes.

**Status:** v0 — scaffolding deployed, data exploration in progress.

**Deployed at:** https://india-msme-digital-trade-exposure-ofqfnhltmh4afgsgyxepjp.streamlit.app/

## Data sources

Not all of the following are integrated yet — the v0 scaffolding stands up the shell while data exploration continues. See [data/README.md](data/README.md) for download steps and the limitations of each source, and [ROADMAP.md](ROADMAP.md) for the priority order and current status.

- WTO Digitally Delivered Services (staged; wired into Overview)
- WTO TiSMoS (Trade in Services by Mode of Supply) (staged; pending Service Categories page)
- MoMSME Udyam Bulletin VII + MSME Annual Report 2024-25 (staged as `msme_nic_*.csv`; pending MSME Base page)
- ICRIER 2025 MSME Digitalisation Survey (pending)
- OECD Digital STRI (pending, Week 4)
- OECD-WTO BaTIS (deferred; the EBOPS-ISIC crosswalk it would have supplied is already in the TiSMoS workbook)

## Tech stack

Python, Streamlit, pandas, Plotly. Deployed via Streamlit Community Cloud.

## Local development

```bash
git clone https://github.com/veer-sanyal/india-msme-digital-trade-exposure.git
cd india-msme-digital-trade-exposure
python -m venv venv
source venv/bin/activate  # on Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Project structure

```
.
├── app.py                  # Streamlit entry point
├── data/
│   ├── raw/                # Source files (not committed)
│   └── processed/          # Cleaned/derived data (not committed)
├── notebooks/              # Exploratory Jupyter notebooks
├── DECISIONS.md            # Decision log
├── README.md
├── requirements.txt
├── .gitignore
└── .streamlit/
    └── config.toml         # Streamlit theme and server config
```

## Decision log

See [DECISIONS.md](DECISIONS.md) for the running log of architectural and scoping decisions.
