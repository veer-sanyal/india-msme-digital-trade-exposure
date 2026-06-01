# Guided Walkthrough (static site)

A single-page, scroll-driven walkthrough of the India digital-services-trade x
MSME exposure analysis. Plain HTML + CSS + client-side Plotly on the project
design system (IBM Plex, warm paper / cool ink, indigo + clay). No build step
and no server runtime: open `index.html` or serve the folder statically.

## Files

| File | Role |
|---|---|
| `index.html` | The page: hero, key concepts, four data acts, scope, findings, roadmap, sources. |
| `colors_and_type.css` | Design tokens (color, type, spacing, radii). Single source of truth. |
| `walkthrough.css` | Narrative layout on top of the tokens. |
| `chart_theme.js` | `ITE` Plotly template + the six named chart color scales. |
| `walkthrough.js` | Fills tiles/table from `data.js`, draws the Plotly charts, scroll-spy rail, definition popovers, scroll-reveal and grow-in animations. |
| `data.js` | **Generated** by `../scripts/build_site_data.py` from `data/processed/*.csv`. Do not edit by hand. |

## Preview locally

```bash
cd site
python -m http.server 8000
# open http://localhost:8000
```

Fonts and Plotly load from CDN, so a network connection is needed on first load.

## Rebuild the data

Every figure on the page is computed from the processed CSVs, never hardcoded
(DECISIONS Entry 005). After the processed CSVs change, regenerate `data.js`:

```bash
python scripts/build_site_data.py   # run from the repo root
```

The exposure score is the v0 formula from the analysis: two min-max-normalised
components (MSME scale in the mapped ISIC section(s), Mode 1 trade in USD
billion), summed. `build_site_data.py` emits the raw components; `walkthrough.js`
normalises and sums them client-side so the scatter, ranked bar and table always
agree.

## Deploy

Pushing to `main` triggers `.github/workflows/deploy-pages.yml`, which publishes
this folder to GitHub Pages. One-time setup: repo Settings -> Pages -> Source ->
"GitHub Actions".
