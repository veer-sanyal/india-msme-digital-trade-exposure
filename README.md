# India Digital Services Trade Exposure Dashboard

An interactive dashboard that connects India's digital services trade data with MSME sector data to show which small businesses are most exposed to global digital platforms, cloud services, and digital trade policy changes.

**Status:** v0 — scaffolding deployed, data exploration in progress.

**Deployed at:** [URL pending Streamlit Community Cloud setup]

## Data sources

Not all of the following are integrated yet — the v0 scaffolding stands up the shell while data exploration continues.

- WTO TiSMoS (Trade in Services by Mode of Supply)
- WTO Digitally Delivered Services
- OECD-WTO BaTIS
- MSME Dashboard (Government of India)
- ICRIER 2025 MSME Digitalisation Survey
- OECD Digital STRI

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
