import streamlit as st

st.set_page_config(
    page_title="India Digital Services Trade Exposure",
    layout="wide",
)

st.title("India Digital Services Trade Exposure")
st.caption(
    "v0. Mapping India's digital services trade against MSME sectors to surface "
    "which small businesses are most exposed to global digital platforms and policy shifts."
)

st.markdown(
    """
### What's here

Use the sidebar to navigate:

- **Overview** &mdash; India's total digitally delivered services trade since 2005, with
  a category breakdown of exports and imports.
- **Service Categories** &mdash; All 11 EBOPS service categories across modes of supply,
  with year and category drilldowns.

More pages land as the project moves from Phase A (Dr. G follow-up readiness) into
Phase B (v1 ship and iteration). Roadmap and decision log are in the repo.
"""
)

st.divider()
st.markdown(
    "[GitHub repository](https://github.com/veer-sanyal/india-msme-digital-trade-exposure) "
    "&middot; "
    "[Decision log](https://github.com/veer-sanyal/india-msme-digital-trade-exposure/blob/main/DECISIONS.md) "
    "&middot; "
    "[Roadmap](https://github.com/veer-sanyal/india-msme-digital-trade-exposure/blob/main/ROADMAP.md)"
)
