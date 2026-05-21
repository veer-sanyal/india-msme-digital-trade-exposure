# Decision Log

This file tracks key decisions made during the build of the India Digital Services Trade Exposure Dashboard — what was considered, what was chosen, and why. Entries are append-only and dated.

## Entry 001 — 2026-05-19

**Decision:** Project scope — chose Option B (India MSME digital services trade exposure) over Option C (WTO e-commerce moratorium impact visualizer).

**Why:** Option B aligns directly with Dr. Gopalakrishnan's published research focus at Infisum, making the prototype both a portfolio artifact and a substantive update for the May 30 follow-up. Option C was viable but more abstract and less connected to existing relationships.

**Trade-off:** Option B requires manually crosswalking trade categories to MSME activities, which is harder than C's cleaner policy-focused dataset. Accepting that complexity in exchange for stronger narrative fit.

## Entry 002 — 2026-05-20

**Decision:** Tech stack — Streamlit + Python + pandas + Plotly, deployed on Streamlit Community Cloud.

**Why:** Fastest path from pandas dataframe to public URL. Python is already a known language (prior Firmly SWE internship). Streamlit Community Cloud is free, GitHub-connected, and auto-redeploys on push.

**Considered and rejected:** Next.js/React (too much frontend overhead for a v1), Dash (heavier than Streamlit with no upside at this scale), Tableau/PowerBI (not code, not in a repo, doesn't read as a builder artifact).

## Entry 003 — 2026-05-20

**Decision:** v0 scaffolding deployed to Streamlit Community Cloud at https://india-msme-digital-trade-exposure-ofqfnhltmh4afgsgyxepjp.streamlit.app/.

**Why:** Getting an empty shell on a public URL before any feature work locks in the deploy pipeline early — every subsequent commit to `main` auto-redeploys, so data integration and visualizations ship continuously rather than as a big-bang launch.

**Note:** The auto-generated subdomain is long and not memorable. Acceptable for v0; revisit if a custom domain or rename becomes useful before the May 30 follow-up.

## Entry 004 — 2026-05-20

**Decision:** Data pipeline shape — raw WTO files (DDS, TiSMoS) stay out of git; a reproducible build script (`scripts/build_processed.py`) generates small India-only slices in `data/processed/` that the Streamlit app loads.

**Why:** The TiSMoS exports + imports CSVs are ~75MB each (~150MB total). Versioning them adds friction (slow clones, Streamlit Cloud deploy weight, eventual git-LFS surgery) for no benefit — the source is public and stable at data.wto.org, and the processed India slices are 25KB-512KB and deterministic from the raw inputs. `data/README.md` documents the download steps so the pipeline stays reproducible.

**Side discovery worth flagging for Week 3:** The TiSMoS items-and-correspondence workbook ships an EBOPS-to-ISIC-section crosswalk at the level-1 service categories (e.g. SISK1 → ISIC J Information and Communication; SFSG → ISIC K Finance; SJXSJ34 → ISIC L+M+N Professional and Admin). India's MSME data uses NIC codes that align with ISIC sections. A substantial portion of what the roadmap called a "manual sector crosswalk" is already specified by WTO/UN — refine, don't rebuild.

**Other finding worth logging:** DDS values reconcile to TiSMoS Mode 1 values to within rounding on overlapping codes for India 2022 (SF, SG, SH, SI1, SI3 identical; SI2 differs ~0.6%). Confirms the two datasets are coherent: DDS is essentially "TiSMoS Mode 1, digitally-deliverable subset" extended to 2025. So the Overview page can show the recent trend via DDS (through 2025) and the Service Categories page can pivot into category/mode depth via TiSMoS (through 2022), with a single footnote on the year gap rather than a reconciliation problem.

**No bilateral cut available:** Both datasets report "World" as the only partner. The dashboard cannot show India→US digital exports, only India→World. Worth saying up front in the dashboard caption to set expectations.

## Entry 005. 2026-05-21

**Decision:** Citation figures inside chart-framing prose are computed from the dataframe at render time, not typed as literals.

**Why:** When a chart description says "Computer services reached $127B" or "IP licensing imports have grown 29x since 2005," those numbers are a snapshot of a specific year's data. Hardcoding them means the chart itself updates when the WTO publishes the next annual release, but the surrounding narrative silently goes stale and lies about what the chart shows. Pulling the figures from the same dataframe the chart is drawn from guarantees the prose and the visual stay in lockstep on every refresh, with no annual copy-editing chore and no risk of "the chart says X, the paragraph says Y" embarrassment in front of a reader who notices.

**Trade-off:** A small amount of lookup and arithmetic logic sits in `app.py` alongside the rendering code, which is mildly less clean than pure presentation. Used WTO indicator codes (SI2, SJ, SH) as lookup keys rather than display names, because the codes are stable across releases while names occasionally get re-worded.

**Generalizes to:** Any future page or section that cites specific numbers in surrounding prose. The pattern is: compute, then format into the markdown string. Treat a hardcoded data value embedded in copy as a defect, not a shortcut, anywhere the underlying data is expected to refresh.
