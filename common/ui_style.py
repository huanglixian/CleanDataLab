import streamlit as st

def apply_custom_style():
    """
    通用验证程序样式 - 高级白色背景 + 灰蓝色点缀
    
    色彩搭配：
    - 主色调：#5A7A8B（沉稳灰蓝）
    - 辅助色：#7B98AA（柔和蓝灰）  
    - 强调色：#4A6B7D（深度蓝灰）
    - 边框色：#A8BCC8（淡雅蓝灰）
    """
    st.markdown("""
    <style>
    /* 在顶栏添加应用标题 */
    [data-testid="stHeader"]::before {
        content: "🛠️ 广东院-数据预处理-工具集";
        display: block;
        padding: 12px 20px;
        font-size: 26px;
        font-weight: 900;
        color: #5A7A8B;
        text-align: right;
        width: 100%;
    }

    
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
    </style>
    """, unsafe_allow_html=True)