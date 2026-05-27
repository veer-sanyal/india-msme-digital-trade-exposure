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

## Entry 006. 2026-05-21

**Decision:** MSME sector data captured ahead of schedule from MoMSME Udyam Bulletin VII (cutoff 30 Sep 2021). Three processed CSVs land in `data/processed/`: `msme_nic_5digit.csv` (top 50 manufacturing + top 50 services NIC 5-digit codes), `msme_nic_division.csv` (the same data rolled up to NIC 2-digit division and joined to ISIC section), and `msme_nic_top5_msm.csv` (the only NIC 2-digit by Micro/Small/Medium cross-tab the bulletin publishes, covering five divisions). Build is in `scripts/build_msme_nic.py`. Headline current totals (5.77 crore registrations as of 31 Dec 2024) come from MSME Annual Report 2024-25 Table 2.1 and are used for the headline figure only.

**Why:** The original roadmap entry "MSME Dashboard (Government of India)" was vague about which artifact to pull. After searching the obvious sources (MSME live dashboard, all four annual reports 2021-22 through 2024-25, the Udyam 2020-22 Publication, the data.gov.in OGD catalogue, SIDBI's 2025 MSME report, ICRIER's 2025 survey), the verdict is clean: MoMSME does not publish a full NIC 2-digit by enterprise-size cross-tab. The most granular published sector data is Bulletin VII's top-50 NIC 5-digit lists for manufacturing and services. Aggregating those up to NIC 2-digit and joining to ISIC section via the crosswalk found in Entry 004 turns a known gap into a usable cut. The trade-off accepted: the sector cut is frozen at Sep 2021 while the headline total is current to Dec 2024. Caption will say so.

**Why this matters for exposure:** The ISIC sections that map to digital services trade categories via `ebops_isic_crosswalk.csv` (J Information and Communication, K Finance, M Professional/Scientific, N Admin/Support) carry roughly 167k, 39k, 319k, and 404k MSMEs respectively in the top-50 aggregation. That is enough signal to build the MSME Base page and a defensible first cut of the exposure score in Week 3 without waiting for any additional source.

**What's still unknown:** Whether MoMSME would release the full NIC 2-digit by M/S/M cross-tab under RTI. Worth filing the request later (Phase B, optional Week 7+) so a v2 of the MSME Base page can replace the Sep 2021 cut with current numbers. Not blocking for v1.

**Side note on BaTIS:** Earlier roadmap had OECD-WTO BaTIS as Priority 3 alongside the manual sector crosswalk. Entry 004 showed the EBOPS-ISIC crosswalk is already published. With the MSME slice now joining cleanly to ISIC section, BaTIS no longer adds anything for the MVP and can be deferred or dropped.

## Entry 007. 2026-05-27

**Decision:** Dropped ICRIER 2025 MSME Digitalisation Survey from data sources after pulling and partially extracting it; the sample scope does not match the dashboard's thesis.

**Why:** ICRIER's Annual Survey of MSMEs (March 2025, n=2,365, fielded by Ipsos with Walmart support) is the most-cited recent India primary survey on MSME digital adoption, so it was the obvious next source after Bulletin VII. On reading the methodology section, the sample turned out to be Udyam-registered manufacturing firms only, across 7 hand-picked product clusters (apparel, consumer electronics, handicraft, furniture, processed food, sports goods, toys), with a forced 50/50 integrated vs non-integrated split by purposive design and no cut published by NIC division or ISIC section. The dashboard's exposure score joins digital services trade (TiSMoS/DDS, ISIC J, K, M, N) to MSME sector data; ICRIER measures manufacturing MSMEs in ISIC C. Using its e-commerce penetration figures inside a services-side exposure score would be a category error.

**Trade-off:** We lose the most-cited 2025 India-specific MSME digital adoption survey from the source list. The working substitute for services-side adoption is ASUSE 2023-24's generic "internet usage for entrepreneurial activities" cut (26.7% rural+urban combined, cited in the ICRIER report's own introduction). ASUSE is weaker than ICRIER on depth, but it is at least about the right firms.

**Note:** Even though ICRIER is dropped as a data source, the fact that the most-published India MSME digitalisation survey is manufacturing-only is itself evidence of the gap the dashboard fills. Worth a sentence in the methodology page when the dashboard ships.

**Generalizes to:** Read the methodology section before treating a survey as a fit, not just the title and headline numbers. Two hours of extraction work on this source was avoidable; the manufacturing-only design is on page 20 of the report.
