import streamlit as st

def apply_custom_style():
    """
    通用验证程序样式 - 高级白色背景 + 灰蓝色点缀
    
    色彩搭配：
    - 主色调：#5A7A8B（沉稳灰蓝）
    - 辅助色：#7B98AA（柔和蓝灰）  
    - 强调色：#4A6B7D（深度蓝灰）
    - 边框色：#A8BCC8（淡雅蓝灰）
    - 深灰调：#3D5A6B（偏灰深蓝）
    - 中蓝调：#476B84（偏蓝中灰）
    - 暗蓝调：#2F4A5C（深邃蓝灰）
    """
    st.markdown("""
    <style>

    
    /* 页面标题统一样式 */
    h1, [data-testid="stMarkdownContainer"] h1 { 
        font-size: 24px !important;
        color: #4A6B7D !important;
    }
    h2, [data-testid="stMarkdownContainer"] h2 {
        font-size: 23px !important;
        color: #4A6B7D !important;
    }
    h3, [data-testid="stMarkdownContainer"] h3 {
        font-size: 22px !important;
        color: #4A6B7D !important;
    }
    
    /* 减少页面顶部留白 */
    .block-container {
        padding-top: 3rem;
    }
    
    /* 主体背景 - 白色 */
    .stApp { 
        background: white; 
    }
    
    /* 顶栏浅灰色背景 */
    .stAppHeader {
        background: linear-gradient(135deg, #f8fafb 0%, #f4f7f9 100%);
    }
    
    /* 按钮样式 */
    .stButton > button { 
        background: linear-gradient(45deg, #5A7A8B, #7B98AA); 
        color: white; 
        border: none; 
        border-radius: 8px; 
        font-weight: 500; 
    }
    .stButton > button:hover { 
        background: linear-gradient(45deg, #4A6B7D, #5A7A8B); 
    }
    
    /* Primary按钮样式 */
    .stButton > button[kind="primary"], 
    .stDownloadButton > button[kind="primary"] { 
        background: linear-gradient(45deg, #476B84, #5A7A8B) !important; 
        color: white !important; 
        border: none !important;
    }
    .stButton > button[kind="primary"]:hover, 
    .stDownloadButton > button[kind="primary"]:hover { 
        background: linear-gradient(45deg, #3D5A6B, #476B84) !important; 
    }
    
    /* 文件上传框 */
    .stFileUploader > div { 
        border: 2px dashed #A8BCC8; 
        border-radius: 10px; 
    }
    
    /* 数据表格 */
    .stDataFrame { 
        border-radius: 10px; 
        overflow: hidden; 
        box-shadow: 0 2px 8px rgba(90, 122, 139, 0.1); 
    }
    
    /* 信息提示框 */
    .stInfo { 
        background: linear-gradient(45deg, #f0f4f6, #e8f0f3); 
        border-left: 4px solid #7B98AA; 
    }
    
    /* 成功提示框 */
    .stSuccess { 
        background: linear-gradient(45deg, #f0f8f4, #e8f5ec); 
        border-left: 4px solid #5A7A8B; 
    }
    
    /* Radio按钮样式优化 - 使用主题色 */
    .stRadio > div[role="radiogroup"] > label > div[data-testid="stMarkdownContainer"] {
        color: #4A6B7D;
    }
    
    .stRadio > div[role="radiogroup"] > label:has(input:checked) > div[data-testid="stMarkdownContainer"] {
        color: #5A7A8B;
        font-weight: 600;
    }
    
    /* Radio选择按钮颜色 */
    .stRadio > div[role="radiogroup"] > label > div:first-child {
        background-color: white;
        border: 2px solid #A8BCC8;
    }
    
    .stRadio > div[role="radiogroup"] > label:has(input:checked) > div:first-child {
        background-color: #5A7A8B;
        border: 2px solid #5A7A8B;
    }
    </style>
    """, unsafe_allow_html=True)