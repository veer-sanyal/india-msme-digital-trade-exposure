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

## Entry 008. 2026-05-27

**Decision:** Shipped Exposure Index v0 as a two-component, equally weighted, additive, min-max-normalised score per EBOPS level-1 category. Deliberately stopping at the formula question rather than tuning weights or picking a more sophisticated functional form solo. This entry frames the open methodology question and is the central thing to bring to Dr. Gopalakrishnan in the May 30 follow-up.

**What v0 actually does:** For each of the 11 EBOPS level-1 service categories the WTO publishes, the score is the sum of:

1. *MSME scale* = Udyam-registered MSME count (Sep 2021) in the ISIC section(s) that EBOPS category maps to, min-max normalised across the 11 rows to [0, 1].
2. *Trade intensity* = India's Mode 1 exports + imports in that EBOPS category in 2022, in USD billions, min-max normalised across the 11 rows to [0, 1].

Exposure score = component 1 + component 2, range [0, 2]. Ranked descending.

**Why two components, not three:** Digital adoption (planned third component) was going to be backed by ICRIER 2025, which Entry 007 ruled out. ASUSE 2023-24's "internet use for entrepreneurial activities" (26.7%) is the working substitute but not yet pulled and verified, and Entry 007's "read methodology before treating a survey as a fit" rule applies here as much as it did to ICRIER. Two real components beats three components where one is unverified. Policy sensitivity (planned fourth component) waits on OECD Digital STRI in Week 4.

**The open question (this is the Dr. G question):** What is the principled way to combine components in an exposure index when the components measure structurally different things?

Concretely, four sub-problems sit inside that:

- *Additive vs multiplicative.* Additive (current v0) lets one component compensate for zero in another. *Tourism and business travel* has 372k MSMEs and effectively zero Mode 1 trade, and still scores 0.47 because its MSME-scale component alone carries it. Multiplicative would zero that row out: no Mode 1 trade means no digital exposure, regardless of how many tourism MSMEs exist. Which framing is right depends on what "exposure" is supposed to mean. If exposure means "how many firms could be affected by a digital-trade policy shock," additive is closer. If exposure means "how much activity actually flows through the digital channel that policy operates on," multiplicative is closer. The dashboard's stated frame (which small businesses are most exposed to global digital platforms and policy changes) reads ambiguous between the two.

- *Components measure structurally different things.* MSME scale is a count of firms. Trade intensity is USD billion. Min-max normalising puts both on [0, 1] but the sum has no economic interpretation: a 0.4 on firm-count plus a 0.6 on dollar-flow is not 1.0 of anything. The visible symptom in v0 is Transport ranking second at 1.37. Transport scores high because (a) division 49 has 418k MSMEs and (b) India runs ~$133B of Mode 1 Transport trade in 2022. But that $133B is overwhelmingly freight invoices and airline tickets paid to foreign carriers, not platform-mediated digital activity. The Service Categories page already flags this in narrative; the Exposure Index reproduces it as a high rank that overstates the conceptual exposure for Transport MSMEs. The fix probably is not "tweak weights" but "rethink what the components are supposed to be measuring jointly."

- *Weighting.* Equal weights are a placeholder, not a principled choice. The dashboard could weight by something defensible (variance explained, expert assignment from STRI categories once STRI lands, sensitivity of MSMEs to platform fees) but each of those rests on data not yet pulled, and tuning weights solo without that data would be arbitrary.

- *Normalisation.* Min-max is dominated by the maximum row. *Other business services* (SJXSJ34) is the max on both components and pins both at 1.0, so its score is 2.0 by construction. Z-score normalisation would handle outliers differently but introduces negative values. Rank-based normalisation throws away magnitude entirely. Each choice changes the ranking, particularly the gap between rank 1 and rank 2.

There is a related but separate join issue worth mentioning to Dr. G as context, even though it sits below the methodology question in priority. The WTO TiSMoS items-and-correspondence workbook maps SJXSJ34 *Other business services* to ISIC L+M+N as a unit, not to L, M, and N individually. That means the v0 row for SJXSJ34 sums MSME counts across three ISIC sections, which gives it a structural advantage on the firm-count side relative to the other ten rows that map to a single ISIC section each. A v2 could either disaggregate SJXSJ34 into its EBOPS sub-codes (which the TiSMoS data supports) or split the MSME count across L, M, N proportionally. Neither move is hard; the question is whether the disaggregation makes the index more meaningful or just more complicated.

**What I am hoping Dr. G points to:** Either a published framework for combining structurally different components in a composite index (the OECD JRC Handbook on Composite Indicators is the obvious starting reference but it is written for indicators of the same type, e.g. all socio-economic outcomes, not for joining firm counts with trade flows), or a sharper definition of what "exposure" means in this dashboard that resolves the additive-vs-multiplicative question by being precise about what is being exposed to what.

**What stays unresolved on purpose:** The formula. Locking in additive equal-weighted min-max as the permanent shape would be the kind of methodology call Sunday review exists to catch. v0 ships as-is, labelled v0, with this entry on the page as the source of the visible footnote about known issues.

**Generalizes to:** When a methodology choice has more than one defensible answer and the project has access to a domain expert, the right move is to ship the simplest visible version, frame the question crisply, and bring it to the expert. Not to spend two days picking a formula in private.

## Entry 009. 2026-05-31

**Decision:** Replaced the four-tab Streamlit dashboard with a single static guided-walkthrough page under `site/`, deployed on GitHub Pages, recreating a Claude Design HTML/CSS/JS handoff on a new project design system (IBM Plex, warm paper and cool ink, indigo and clay, a reusable Plotly theme). The four old tabs become four narrative "acts" inside one scroll story that runs question, key concepts, the four acts, scope, findings, roadmap, and sources. `app.py`, `views/`, and `.streamlit/` are removed.

**Why:** The goal was to walk a reader through the analysis rather than hand them four tabs of charts to assemble themselves. The form that does that, a sticky-rail scroll narrative with a concepts primer, hover definitions, scroll-triggered chart entrances, and the two-axis frame drawn out before the final chart, is something Streamlit cannot render faithfully. Moving to plain HTML plus client-side Plotly buys that editorial control. The trade-off accepted: Streamlit's server-side interactivity goes away (the page keeps a single Exports/Imports toggle and otherwise reads top to bottom rather than offering sliders that recompute in Python), and the Streamlit Community Cloud deploy is retired in favour of a static host. A GitHub Pages Actions workflow publishes `site/` on push to `main`.

**Data stays computed from source:** Entry 005's rule is carried into the new architecture. `scripts/build_site_data.py` reads `data/processed/*.csv` and writes `site/data.js`; no figure on the page is typed by hand. The exposure components are emitted raw and min-max normalised and summed in `walkthrough.js`, so the scatter, the ranked bar, and the score table cannot disagree. The live build reproduces the v0 scores logged in Entry 008 (Other business services 2.00, Transport 1.37).

**Real categories over the design mock's stand-ins:** The handoff mock shipped a representative eight-row exposure set and placeholder mode-mix shares for layout purposes. The production page computes the real eleven EBOPS level-1 categories from the crosswalk (the same set as the retired `exposure_index.py`) and real Mode 1 to Mode 4 shares from `tismos_india.csv`, so the page reflects the actual analysis, not the design's illustrative data.

**A hardcoded figure the data caught:** The mock stated IP-licensing fees had grown roughly tenfold since 2005. Computing from `dds_india.csv` gives 29.4x (to $19.8B in 2025), matching the figure cited in the study material. The mock value was wrong; deriving it from the dataframe corrected it without a manual check. This is Entry 005's failure mode happening in practice.

**Side improvement, unpacking the top row:** Added a breakdown of the highest-ranked category to Act IV. `Other business services` (SJXSJ34) maps to ISIC L+M+N, so its firm count is a composite; `build_site_data.py` now emits the NIC 2-digit divisions behind it and the page charts them by section. Administrative and support and professional and scientific activities supply most of the firms, real estate the least, and a sizable share (travel agencies, building support, vehicle leasing, real estate) is domestically oriented rather than cross-border digital. The unpacking names concrete sectors for the conclusion and makes the existing L+M+N caveat concrete rather than abstract.

**Dropped:** The kit's React "Tweaks" panel (density and accent controls) is design-tool chrome and was not carried into production. `requirements.txt` is trimmed to pandas and openpyxl, which are now only used by the build scripts, not at runtime.

## Entry 010. 2026-06-01

**Decision:** Disaggregated the top exposure category, Other business services (EBOPS `SJXSJ34`), into its EBOPS sub-codes using a crosswalk constructed for this analysis, and added a within-category sub-exposure ranking to Act IV.

**Why:** The published WTO crosswalk maps `SJXSJ34` to ISIC L+M+N as a unit, so v0 could only report it as one lumped row whose firm count spans three sections. TiSMoS does carry Mode 1 trade at sub-code level (SJ21 legal/accounting/management consulting, SJ31 architecture/engineering, SJ22 advertising/market research, SJ1 R&D, SJ35 other n.i.e.), so pairing each sub-code with the NIC divisions that produce it gives a finer read. The payoff: the conclusion names a specific sub-sector, legal/accounting/management consulting (roughly $90B Mode 1 trade against about 92k firms), rather than an opaque lumped label.

**What is flagged:** The sub-code to NIC mapping is a judgment call, not from the WTO workbook, and is labelled as constructed on the page. R&D (SJ1) maps to NIC 72, absent from the Sep 2021 top-50 cut, so it shows zero firms by omission. SJ35 "other n.i.e." is a mixed residual (travel agencies, office support, employment, building services) that ranks high on firm count alone, reproducing the parent category's additive-compensation issue one level down. Real estate (NIC 68, ISIC L) has no Mode 1 trade sub-code and is excluded. Scores are normalised within the five sub-codes, so they rank against each other, not against the eleven top-level categories.

**Generalizes to:** When an authoritative crosswalk lumps a category and the underlying data supports a finer split, the disaggregation is worth doing for the actionable detail it buys, but the constructed mapping is labelled as constructed wherever it appears, and the rows where it does not join cleanly are named rather than hidden.
