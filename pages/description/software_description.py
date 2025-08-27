import streamlit as st
from common.ui_style import apply_custom_style

st.set_page_config(page_title="软件说明", layout="centered")
apply_custom_style()

st.title("数据预处理工具集")
st.markdown("专业的Excel数据处理解决方案")
st.markdown("---")

# 读取并显示README.md内容
def load_readme():
    """读取README.md文件内容"""
    try:
        with open("README.md", 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "README.md文件未找到"

readme_content = load_readme()
st.markdown(readme_content)