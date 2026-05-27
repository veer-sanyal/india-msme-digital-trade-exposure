import streamlit as st

from views import exposure_index, msme_base, overview, service_categories

st.set_page_config(
    page_title="India Digital Services Trade Exposure",
    layout="wide",
)

st.title("India Digital Services Trade Exposure")
st.caption(
    "v0. Mapping India's digital services trade against MSME sectors to surface "
    "which small businesses are most exposed to global digital platforms and policy shifts."
)

tab_overview, tab_svc, tab_msme, tab_exposure = st.tabs(
    ["Overview", "Service Categories", "MSME Base", "Exposure Index"]
)

with tab_overview:
    overview.render()

with tab_svc:
    service_categories.render()

with tab_msme:
    msme_base.render()

with tab_exposure:
    exposure_index.render()
