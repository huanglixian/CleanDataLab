import streamlit as st
from common.ui_style import apply_custom_style

def load_readme():
    """读取README.md文件内容"""
    try:
        with open("README.md", 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "README.md文件未找到"

def main():
    st.set_page_config(
        page_title="数据预处理-工具集",
        page_icon="🛠️",
        layout="centered",
        initial_sidebar_state="auto"
    )
    
    apply_custom_style()
    
    st.markdown("# 欢迎使用数据预处理工具集")
    st.markdown("**请选择左侧工具开始数据处理，下方是开发说明，用户无需理会～**")
    st.markdown("---")
    
    # 显示README内容
    readme_content = load_readme()
    st.markdown(readme_content)
    
    # 版本信息
    #st.sidebar.markdown("---")
    #st.sidebar.markdown("**版本信息**")
    #st.sidebar.info("Excel工具集 v1.0\n\n包含3个数据处理工具")

if __name__ == "__main__":
    main()