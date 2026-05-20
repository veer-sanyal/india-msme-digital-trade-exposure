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
