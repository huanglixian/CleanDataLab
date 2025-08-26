import streamlit as st
from common.ui_style import apply_custom_style

def main():
    st.set_page_config(
        page_title="广东院-数据预处理-工具集",
        page_icon="🛠️",
        layout="centered",
        initial_sidebar_state="auto"
    )
    
    apply_custom_style()
    
    st.markdown("## 欢迎使用数据预处理工具集")
    st.markdown("选择左侧工具开始数据处理")
    
    # 主页介绍
    st.markdown("""
    ## 📋 可用工具
    
    **🎯 Excel主体信息提取工具**  
    自动识别表格主体，删除外围描述性信息
    
    **📊 Excel合并单元格填充工具**  
    上传Excel文件，自动取消合并单元格并填充值
    
    **🧹 Excel标题表头清理工具**  
    自动删除表格标题，处理多行表头合并
    
    ---
    
    ## 🚀 使用方法
    1. 点击左侧侧边栏选择需要的工具
    2. 上传Excel文件进行处理
    3. 下载处理后的结果文件
    
    ## 💡 提示
    - 支持 `.xlsx` 和 `.xls` 格式文件
    - 所有工具都使用统一的高级样式
    - 处理结果会自动添加后缀标识
    """)
    
    # 版本信息
    st.sidebar.markdown("---")
    st.sidebar.markdown("**版本信息**")
    st.sidebar.info("Excel工具集 v1.0\n\n包含3个数据处理工具")

if __name__ == "__main__":
    main()