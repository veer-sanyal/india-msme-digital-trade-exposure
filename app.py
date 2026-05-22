import streamlit as st

st.set_page_config(
    page_title="India Digital Services Trade Exposure",
    layout="wide",
)

overview = st.Page(
    "views/overview.py",
    title="Overview",
    default=True,
)
service_categories = st.Page(
    "views/service_categories.py",
    title="Service Categories",
)

nav = st.navigation([overview, service_categories], position="top")
nav.run()
