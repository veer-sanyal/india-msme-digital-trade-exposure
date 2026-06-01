# India Digital Services Trade Exposure

A guided walkthrough that connects India's digital-services-trade data with MSME
sector data to show which small businesses are most exposed to global digital
platforms, cloud services, and digital-trade policy shifts.

It reads top to bottom as a single scroll narrative: the question, the key
concepts, four data "acts" (is the trade real? where does it concentrate? who
are the firms? putting the two axes together), then scope, findings, roadmap and
full provenance. Every figure is computed from the processed source data, never
hardcoded.

**Status:** v0. Read the exposure ranking as direction, not calibrated magnitude.

**Live site:** https://veer-sanyal.github.io/india-msme-digital-trade-exposure/
(published from `site/` via GitHub Pages once Pages is enabled, see Deployment).

## What it shows

| Section | Question | Data source |
|---|---|---|
| Act I, Overview | Is the digital-services trade real and growing? | WTO Digitally Delivered Services (DDS) |
| Act II, Service categories | Where does it concentrate, and how digital is each slice? | WTO TiSMoS |
| Act III, MSME base | How many small firms sit in each industry? | MoMSME Udyam Bulletin VII + Annual Report 2024-25 |
| Act IV, Exposure index | Which sectors are most exposed? | All of the above + the EBOPS to ISIC crosswalk |

The exposure score is the v0 formula: two min-max-normalised components (MSME
scale in the mapped ISIC section(s), and Mode 1 trade in USD billion), summed.
Its open methodology questions are presented on the page itself.

## Headline finding

The most exposed category is "Other business services" (EBOPS `SJXSJ34`), which
maps to ISIC sections L+M+N. Act IV unpacks it: administrative and support and
professional and scientific activities (management consultancy, accounting,
legal, architecture and engineering, advertising) supply most of the firms,
real estate the least. Because part of that firm count is domestically oriented
activity (travel agencies, building support, vehicle leasing, real estate) that
does not cross a border digitally, the ranking is read as direction, not a
precise measure of digital exposure. All figures are computed from
`data/processed/` at build time.

## Tech

Static HTML + CSS + client-side Plotly on a small design system (IBM Plex; warm
paper / cool ink; indigo + clay). No server runtime. Python (pandas) is used only
to build the processed CSVs and the page's `data.js`.

## Local preview

```bash
git clone https://github.com/veer-sanyal/india-msme-digital-trade-exposure.git
cd india-msme-digital-trade-exposure
cd site && python -m http.server 8000
# open http://localhost:8000
```

Fonts and Plotly load from CDN, so a connection is needed on first load.

## Rebuilding the data

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python scripts/build_processed.py    # WTO DDS + TiSMoS -> processed CSVs (needs raw downloads, see data/README.md)
python scripts/build_msme_nic.py     # Udyam Bulletin VII -> processed CSVs
python scripts/build_site_data.py    # processed CSVs -> site/data.js
```

`build_site_data.py` is deterministic and reads only `data/processed/*.csv`, so
it is safe to run any time the processed data changes.

## Deployment

`.github/workflows/deploy-pages.yml` publishes `site/` to GitHub Pages on every
push to `main`. One-time setup: repo Settings -> Pages -> Build and deployment ->
Source -> "GitHub Actions".

## Project structure

```
.
├── site/                   # the published static walkthrough (index.html + assets)
│   ├── index.html
│   ├── colors_and_type.css # design tokens
│   ├── walkthrough.css     # narrative layout
│   ├── chart_theme.js      # Plotly brand template + color scales
│   ├── walkthrough.js      # charts, scroll-spy, popovers, animations
│   └── data.js             # generated from data/processed/*.csv
├── scripts/                # build the processed CSVs and site/data.js
├── data/processed/         # cleaned/derived data the page is built from
├── DECISIONS.md            # decision log
├── ROADMAP.md
└── .github/workflows/      # GitHub Pages deploy
```

## Decision log

See [DECISIONS.md](DECISIONS.md) for the running log of architectural and scoping
decisions, and [ROADMAP.md](ROADMAP.md) for what is deliberately deferred to v2.
