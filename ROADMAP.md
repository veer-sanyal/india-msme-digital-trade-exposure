# Roadmap

The build plan for the India Digital Services Trade Exposure dashboard: what ships in v0, what is deliberately deferred, and the order the remaining work runs in.

This file is forward-looking. For why each past decision was made, see [DECISIONS.md](DECISIONS.md).

## The project in one sentence

A guided walkthrough that connects India's digital-services-trade data with MSME sector data to show which small businesses are most exposed to global digital platforms, cloud services, and digital-trade policy shifts.

## What v0 ships

A single static walkthrough under `site/`, deployed on GitHub Pages, that reads top to bottom as one scroll narrative:

| Section | Question | Data source |
|---|---|---|
| Act I, Overview | Is the digital-services trade real and growing? | WTO Digitally Delivered Services (DDS) |
| Act II, Service categories | Where does it concentrate, and how digital is each slice? | WTO TiSMoS |
| Act III, MSME base | How many small firms sit in each industry? | MoMSME Udyam Bulletin VII + Annual Report 2024-25 |
| Act IV, Exposure index | Which sectors are most exposed? | All of the above + the EBOPS to ISIC crosswalk |

The exposure score is the v0 formula: two min-max-normalised components (MSME scale in the mapped ISIC section, and Mode 1 trade in USD billion), summed and ranked. Its open methodology questions are presented on the page itself and logged in DECISIONS Entry 008.

## What this project is NOT

Stated up front so the dashboard does not overclaim:

- Not proving causal impact of digital trade on MSME growth
- Not tracking every Indian MSME firm individually
- Not a full econometric model
- Not policy advocacy

It is a data-storytelling and decision-support tool: an exposure index that connects three data worlds (trade, MSME structure, and policy) that usually sit apart.

## Data sources

| Dataset | Role | Status |
|---|---|---|
| WTO Digitally Delivered Services (DDS) | Recent trade trend through 2025 | Integrated |
| WTO TiSMoS (Trade in Services by Mode of Supply) | Category and mode-of-supply depth through 2022 | Integrated |
| MoMSME Udyam Bulletin VII + Annual Report 2024-25 | MSME counts by NIC, headline registration total | Integrated |
| EBOPS to ISIC section crosswalk (WTO TiSMoS workbook) | The join that links trade categories to MSME sectors | Integrated |
| OECD Digital STRI | Policy-sensitivity component | Deferred to v2 |
| ASUSE 2023-24 | Digital-adoption component (verify methodology before use) | Deferred to v2 |
| OECD-WTO BaTIS | Bilateral partner view | Optional, low priority |

ICRIER's 2025 MSME Digitalisation Survey was evaluated and dropped; it is manufacturing-only and does not fit a services-side exposure score (DECISIONS Entry 007).

## Deferred to v2

These earn their place only after v0 is solid and only where the data supports them:

- **Resolve the exposure-index methodology.** The open questions (additive vs multiplicative, weighting, normalisation, and how to combine components that measure structurally different things) are documented in DECISIONS Entry 008 and are the subject of expert review before any formula is locked in.
- **Add a digital-adoption component** from ASUSE 2023-24, after reading its methodology to confirm it decomposes usefully by sector.
- **Add a policy-sensitivity component** from the OECD Digital STRI, and a scenario view that re-ranks exposure as policy levers (data localisation, local presence, e-payment restrictions) move. The first named policy to anchor this view is the WTO e-commerce moratorium (in play at MC14); the intended primary user is a digital-trade policy-research analyst (see DECISIONS Entry 012).
- **Replace the Sep 2021 MSME sector cut** with current numbers if MoMSME releases a full NIC 2-digit by enterprise-size cross-tab, possibly via an RTI request.
- **Refine the crosswalk disaggregation** where the underlying data supports a finer split than the published mapping.
- **Add lightweight usage telemetry** so later iteration is informed by what readers actually do on the page.
- **Optional depth:** a bilateral partner view (BaTIS) and a state-level MSME breakdown, both interesting extensions rather than core legs of the argument.

## Out of scope until at least v2

Tempting additions that are explicitly excluded for now:

- Causal modelling of digital trade impact on MSME growth
- State-level MSME granularity in v0
- User authentication
- ML or NLP features without a clear user problem they solve
- Adding a fifth section before the existing narrative works end to end

## Working principles

- One decision-log entry per work session, recording the honest trade-off, not a status update. See [DECISIONS.md](DECISIONS.md).
- Every figure on the page is computed from the processed source data at build time, never hardcoded (DECISIONS Entry 005).
- Where an authoritative crosswalk lumps a category and the data supports a finer split, the disaggregation is labelled as constructed wherever it appears.
- Ship the simplest honest version, label it v0, and surface its known limitations on the page rather than hiding them.
