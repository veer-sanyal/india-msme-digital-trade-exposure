import streamlit as st

st.set_page_config(
    page_title="India Digital Services Trade Exposure",
    layout="wide",
)

st.title("India Digital Services Trade Exposure")
st.caption(
    "v0 — Mapping India's digital services trade against MSME sectors to "
    "surface which small businesses are most exposed to global digital "
    "platforms and policy shifts."
)

st.subheader("Status")
st.info("TiSMoS data exploration is in progress. Visualizations will appear here as the dataset is integrated.")

st.divider()
st.markdown(
    "Source: [GitHub repository](https://github.com/veer-sanyal/india-msme-digital-trade-exposure)"
)
