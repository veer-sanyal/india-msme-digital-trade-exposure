# Infisum Dashboard Project Roadmap

The build plan for the India MSME Digital Trade Exposure Dashboard. This is Pillar 1 (Ship Something Real) of the broader PM internship execution system.

The roadmap exists so weekly Sunday sessions have a target to plan against, and so mid-week decisions can be checked against the larger arc rather than re-derived every time.

---

## The project in one sentence

An interactive dashboard that connects India's digital services trade data with MSME sector data to show which small businesses are most exposed to global digital platforms, cloud services, e-commerce, and digital trade policy changes.

## Why this project

Two roles, equally important:

1. **Pillar 1 evidence for PM applications.** A shipped artifact with real users, real iteration, real decisions, real telemetry. Defensible in interviews. The thing that turns "well-prepared candidate with no proof" into "candidate with shipped work."

2. **Substantive update for Dr. Gopalakrishnan.** A working prototype on his research turf shows you read his work and built something rather than waited. Transforms the May 30 follow-up from "checking in" to "here's what I made."

If Infisum opportunity materializes, dashboard pivots into client work. If not, dashboard stays yours and keeps iterating. Either way, this is the v1 — not the final form.

---

## What the dashboard does

Four pages in the MVP shape:

| Page | What it shows | Data source |
|---|---|---|
| Overview | India digitally delivered services trade trend over time | WTO Digitally Delivered Services |
| Service Categories | India services trade by category, Mode 1 | WTO TiSMoS |
| MSME Base | MSME counts by activity, category, geography | MSME Dashboard (India) + ICRIER |
| Exposure Index | Ranked sectors by digital trade exposure score | All sources + manual crosswalk |

The exposure score combines four components, each weighted 25% in v0:

- **MSME scale** — how many firms/workers in this sector (MSME Dashboard)
- **Digital trade intensity** — how active is digital services trade in this category (WTO/TiSMoS/BaTIS)
- **Digital adoption** — are firms in this sector actually using digital tools (ICRIER)
- **Policy sensitivity** — what regulations could shift the picture (OECD Digital STRI)

Scenario toggle on a fifth page in Phase B: let users see how data localization, digital taxes, or e-commerce moratorium changes affect sector exposure.

---

## What this project is NOT

Important so I do not overclaim in conversations with Dr. G, in interviews, or in the README:

- Not proving causal impact of digital trade on MSME growth
- Not tracking every Indian MSME firm individually
- Not a full econometric model
- Not policy advocacy

It is:
- A decision-support tool
- A data storytelling product
- An exposure/risk/opportunity index
- A way to connect three data worlds (trade, MSME, policy) that usually sit apart

---

## Data sources (priority order)

| Priority | Dataset | Status |
|---|---|---|
| 1 | WTO Digitally Delivered Services | Downloaded May 19, pivot built |
| 2 | WTO TiSMoS (Trade in Services by Mode of Supply) | Pending — Wed May 20 |
| 3 | OECD-WTO BaTIS | Pending — Thu May 21 |
| 4 | MSME Dashboard (Government of India) | Pending — Week 2 |
| 5 | ICRIER 2025 MSME Digitalisation Survey | Pending — Week 2 |
| 6 | OECD Digital STRI | Pending — Week 4 |
| 7 | MoSPI Supply and Use Tables | Optional — Week 7+ |
| 8-9 | NSS 73rd Round / Data.gov India | Optional fallback |

The first three give the trade layer. The next two give the MSME and adoption layer. The sixth gives the policy layer. Everything after that is depth, not MVP.

---

## Constraints that set the schedule

- **Dr. G follow-up window opens ~May 30.** This is the first hard date. Determines what must exist in 11 days from May 19.
- **v1 target ship date ~June 5.** All four pages exist in some form, deployed publicly.
- **Summer ends ~August 7.** 12 weeks total. After v1 ships, that's ~9 weeks of iteration.
- **Google APM expected to close early-to-mid October 2026.** The project needs to be in resume-bullet shape and demo-ready by end of September. Iteration through August means September is polish, not building.

---

## Phase A: May 30 follow-up readiness (May 19-30, 11 days)

The point of Phase A is not to finish the project. It is to earn the right to a substantive follow-up message.

What needs to be true by May 30:

- Deployed prototype at a live public URL
- Two pages working: Overview + Service Categories
- Public GitHub repo with README and DECISIONS.md
- Decision log with at least 4-5 entries showing real thinking
- A specific question or ask drafted for Dr. G — not "what do you think" but "I'm trying to decide between X and Y, would value your read"

What does NOT need to be true by May 30:

- Full exposure score
- MSME Base page
- Policy toggles
- Polished UX
- All four data sources integrated

The follow-up message says "I started building. Here is where I am. Here is one specific thing I am working through. Open to your input." It does not say "I finished a thing."

---

## Phase B: v1 ship and iteration (June 1 through August 7)

After v1 ships ~June 5, the work shifts from building to iterating. This is where the project actually becomes credible Pillar 1 evidence. The bar is no longer "did I build it" — it is "what did I decide, what did I measure, what changed based on what I learned."

The pattern: each week, one feature add or one user feedback cycle, documented in the decision log.

---

## Week-by-week roadmap

Directional, not rigid. Sunday sessions tighten each week. Slippage on one week pushes everything right, not deletes the week.

### Week 1 (May 18-24) — Foundation

- **Mon May 18:** System setup (done)
- **Tue May 19:** Option B committed, WTO Digitally Delivered Services downloaded, pivot + chart built, decision log started (done)
- **Wed May 20:** TiSMoS download, stack chosen, repo live, decision log moved to repo
- **Thu May 21:** BaTIS processed, second visualization built (service category breakdown)
- **Fri May 22:** Streamlit app skeleton deployed at public URL with Overview chart working. Quality bar: it loads and shows one chart. That is enough.
- **Sun May 24:** First Sunday session, plan week 2 in detail

### Week 2 (May 25-31) — Phase A push

- **Mon-Tue:** Second page built (Service Category page from TiSMoS data)
- **Wed-Thu:** ICRIER report read, key stats extracted to manual CSV. MSME data already captured May 21 (Bulletin VII processed slices in repo). Content available for Week 3 without further scraping.
- **Fri May 29:** Decision day on Dr. G outreach. Read the prototype state honestly. Does it earn the send?
- **Sat May 30:** Send the follow-up. Draft together in Sunday/Friday session. Include link to live dashboard, link to decision log, one specific ask.

### Week 3 (Jun 1-7) — Third page and exposure score v0

- Build MSME Base page from collected data
- Draft sector crosswalk (manual CSV: mvp_sector, msme_activity, linked_service_categories, digital_dependency_reason)
- First version of exposure score, even if rough — three components instead of four is fine
- **v1 ship milestone:** all four pages exist in some form, score is computed end-to-end, deployed at a public URL

### Week 4-5 (Jun 8-21) — First real iteration cycle

This is the part that matters for the PM story. The MVP exists; now the work is iterating on contact with reality.

- Add OECD Digital STRI for policy sensitivity component
- Refine sector crosswalk based on what the data actually shows vs what was assumed in week 3
- Add policy scenario toggle (the most interesting feature for Dr. G)
- Add basic telemetry — Plausible or simple GA. Need to be able to answer "what do users actually do here" later.
- If Dr. G replied: this is the highest-signal iteration cycle of the summer. Incorporate his feedback explicitly, document in decision log.

### Week 6 (Jun 22-28) — User feedback round 1

- Send v1 to 2-3 people for actual feedback. Candidates: Dr. G if engaged, an econ professor at Purdue, a senior who has done PM-adjacent work
- Document feedback in decision log
- Pick top 2-3 changes worth making — not all of them

### Week 7-8 (Jun 29-Jul 12) — Iteration round 2

- Implement feedback changes
- Add Supply and Use Tables data if useful (priority 7)
- Write short blog-post-style writeup of what learned. Resume material + conversation material.

### Week 9-10 (Jul 13-26) — Polish and depth

- One technical depth-add: state-level breakdown if NSS data is workable, or a more interesting exposure model
- UX cleanup pass
- Second round of external feedback
- Resume v1 drafted around this work

### Week 11-12 (Jul 27-Aug 7) — Final iteration and wrap

- Final polish based on second feedback round
- Decision log finalized with full narrative arc
- Project README written for a recruiter audience: problem, user, decisions, trade-offs, what changed, what would do differently
- Practice the 90-second pitch out loud, recorded

---

## Success criteria for the project

Pulled from Pillar 1 in direction.md, made specific to this build:

- v1 live with at least one external viewer (Dr. Gopalakrishnan minimum) by June 5
- 8-12 weeks of documented iteration after v1
- At least one piece of real telemetry or usage data captured
- Public decision log maintained with weekly entries
- Can explain in 90 seconds: user, problem, decision, trade-off, metric, what changed
- Can answer "what did you cut from scope and why" without hesitation
- Can answer "what surprised you in the data" with a specific example
- Code public on GitHub, README readable by a recruiter

---

## Decision log discipline

The decision log is not optional. It is the artifact that converts the work into interview material in September.

Format per entry — keep simple, do not over-structure:

```
Date:
What I decided / did:
Why (the trade-off I made):
What's still unknown / next move:
```

Rules:

- One entry per work session, not per decision
- Write the honest "why," not the resume "why"
- Stored at `DECISIONS.md` in the public GitHub repo
- Reviewed in each Sunday session — do not let it become write-only

---

## What earns the May 30 follow-up message

Read this before the May 29 go/no-go decision:

The Berkeley referral-ask protocol says ask only after the person understands your fit and feels comfortable. Applied to this case: do not ask for an internship in the May 30 message. The ask is for input on a specific question, or for a brief conversation.

The Cornell follow-up framing says the strongest follow-up shows evidence of motion, not desire for attention. The dashboard link is the evidence of motion. The decision log is evidence of judgment.

Anti-pattern to avoid: long wall of text describing everything built. The Flynn-Lake research shows requesters underestimate compliance by up to 50% — the message does not need to over-justify. Short, specific, one ask.

Target message length: under 400 characters where possible. Under 800 maximum. Format:

- One line of context (what was discussed last time)
- One line on what was built and why
- One specific question or ask
- Link to the dashboard
- Link to the decision log

---

## When to push back on the roadmap

Signs the roadmap needs to be adjusted at a Sunday session, not mid-week:

- Same week pattern slipping twice in a row (e.g. data download tasks consistently pushed)
- v1 milestone slipping past June 12 — this means Phase A succeeded but Phase B is not starting
- Telemetry not added by end of week 5
- Decision log has fewer than 4 entries by end of any given week
- Trying to add a fifth page before the four-page MVP works end-to-end

Signs the roadmap is working:

- Sunday sessions are tightening the plan, not rebuilding it
- Decision log entries are about real trade-offs, not status updates
- Each week ends with one shipped change visible to external viewers
- The pitch gets shorter and sharper over time, not longer

---

## Stack and infrastructure (working assumptions)

- **Frontend / app:** Streamlit + Python (fast to build, deployable to Streamlit Cloud, handles pandas natively)
- **Data:** Pandas in a `/data` folder; raw CSVs version-controlled until size becomes an issue
- **Deploy:** Streamlit Community Cloud (free, public)
- **Code:** GitHub, public repo
- **Decision log:** `DECISIONS.md` in repo root
- **Telemetry:** Plausible or simple GA, added week 4-5
- **Alternative if Streamlit hits a wall:** Plotly Dash, Next.js + Recharts

Stack decisions get logged in DECISIONS.md when made or changed.

---

## What this roadmap deliberately leaves out

Things that are tempting but explicitly out of scope until Phase B at earliest:

- Causal modeling of digital trade impact on MSME growth
- State-level MSME granularity in v1
- Mobile-responsive design
- User authentication
- ML models, NLP, or "AI features" without a clear user problem they solve
- Reading every ICRIER paper end-to-end (extract what is needed, move on)
- Switching stacks before v1 ships
- Adding pages 5+ before pages 1-4 work end-to-end

These are the things that will feel important during weeks 3-5 and that the Sunday session should refuse to add.
