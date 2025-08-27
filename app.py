import streamlit as st
from common.ui_style import apply_custom_style
from st_pages import add_page_title, get_nav_from_toml

st.set_page_config(
    page_title="数据预处理-工具集",
    page_icon="🛠️",
    layout="centered"
)

# 在左上角显示应用标题logo
st.logo("logo.svg")

nav = get_nav_from_toml(".streamlit/pages.toml")
pg = st.navigation(nav, position="top")
add_page_title(pg)


apply_custom_style()

pg.run()