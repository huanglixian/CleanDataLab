import streamlit as st
import pandas as pd
import io
from pathlib import Path
from common.ui_style import apply_custom_style

def detect_table_boundary(df):
    """
    使用连续性边界检测找到表格主体区域
    从左上角开始扩展，遇到大片空白停止
    """
    if df.empty:
        return df
    
    # 1. 找到数据的实际边界
    # 行边界：从上往下，找到连续空行的开始
    row_end = len(df)
    empty_row_count = 0
    for i in range(len(df)):
        if df.iloc[i].notna().sum() == 0:  # 空行
            empty_row_count += 1
            if empty_row_count >= 2:  # 连续2行为空，认为到边界
                row_end = i - 1
                break
        else:
            empty_row_count = 0
    
    # 列边界：从左往右，找到大部分为空的列
    col_end = len(df.columns)
    for j in range(len(df.columns)):
        col_data = df.iloc[:row_end, j]
        non_empty_ratio = col_data.notna().sum() / len(col_data)
        if non_empty_ratio < 0.1:  # 如果该列90%以上为空
            col_end = j
            break
    
    # 2. 提取主体区域
    cleaned_df = df.iloc[:row_end, :col_end].copy()
    
    return cleaned_df

def main():
    st.set_page_config(
        page_title="Excel 主体信息提取工具",
        page_icon="🎯",
        layout="centered"
    )
    
    apply_custom_style()
    
    st.title("🎯 Excel 主体信息提取工具")
    st.markdown("自动识别表格主体，删除外围描述性信息")
    
    uploaded_file = st.file_uploader(
        "选择Excel文件", 
        type=['xlsx', 'xls'],
        help="支持.xlsx和.xls格式"
    )
    
    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file, header=None)
            
            st.subheader("原始数据预览")
            st.dataframe(df.head(15), use_container_width=True)
            
            st.info(f"原始数据维度: {df.shape[0]} 行 × {df.shape[1]} 列")
            
            if st.button("🎯 提取主体区域", type="primary"):
                with st.spinner("正在分析表格结构..."):
                    cleaned_df = detect_table_boundary(df)
                    
                    st.success("✅ 主体区域提取完成！")
                    
                    st.subheader("提取后数据预览")
                    st.dataframe(cleaned_df, use_container_width=True)
                    
                    # 生成输出文件名
                    original_name = Path(uploaded_file.name).stem
                    output_filename = f"{original_name}_body.xlsx"
                    
                    # 转换为Excel字节流
                    buffer = io.BytesIO()
                    cleaned_df.to_excel(buffer, index=False, header=False)
                    buffer.seek(0)
                    
                    # 下载按钮
                    st.download_button(
                        label="💾 下载提取后文件",
                        data=buffer,
                        file_name=output_filename,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                    
                    # 显示对比信息
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("原始行数", df.shape[0])
                    with col2:
                        st.metric("提取行数", cleaned_df.shape[0])
                    with col3:
                        st.metric("删除行数", df.shape[0] - cleaned_df.shape[0])
                        
        except Exception as e:
            st.error(f"❌ 文件处理出错: {str(e)}")
            st.info("请确保上传的是有效的Excel文件")

if __name__ == "__main__":
    main()