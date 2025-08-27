import streamlit as st
import pandas as pd
import io
import json
from pathlib import Path
from common.ui_style import apply_custom_style

def excel_col_to_index(col_str):
    result = 0
    for char in col_str.upper():
        result = result * 26 + (ord(char) - ord('A') + 1)
    return result - 1

def index_to_excel_col(index):
    result = ""
    while index >= 0:
        result = chr(index % 26 + ord('A')) + result
        index = index // 26 - 1
    return result

def clean_excel_data(df, title_check_rows=3, max_value_cols=2, header_rows=2):
    """
    一站式Excel数据清洗：删除标题、处理表头、填充合并单元格
    """
    # 1. 删除标题行
    removed_title_rows = 0
    for i in range(min(title_check_rows, len(df))):
        if df.iloc[i].notna().sum() <= max_value_cols:
            removed_title_rows += 1
        else:
            break
    
    if removed_title_rows > 0:
        df = df.drop(df.index[:removed_title_rows]).reset_index(drop=True)
    
    # 2. 处理表头
    if len(df) >= header_rows:
        header_data = [df.iloc[i].ffill() for i in range(header_rows)]
        new_headers = []
        for col_idx in range(len(df.columns)):
            parts = [str(header_data[i].iloc[col_idx]) for i in range(header_rows) 
                    if pd.notna(header_data[i].iloc[col_idx]) and str(header_data[i].iloc[col_idx])]
            unique_parts = list(dict.fromkeys(parts))  # 去重保持顺序
            new_headers.append("-".join(unique_parts) if unique_parts else f"Col_{col_idx}")
        
        df = df.iloc[header_rows:].copy()
        if not df.empty:
            df.columns = new_headers[:len(df.columns)]
    
    # 3. 填充左侧合并单元格
    for col_idx in range(len(df.columns)):
        col_data = df.iloc[:, col_idx]
        if col_data.isna().any() and col_data.count() > 0:
            non_null_ratio = col_data.count() / len(col_data)
            if non_null_ratio < 0.8 or (col_idx == 0 and pd.notna(col_data.iloc[0])):
                df.iloc[:, col_idx] = col_data.ffill()
        elif col_idx > 0 and col_data.count() == len(col_data):
            break
    
    return df, removed_title_rows

def main():
    st.set_page_config(page_title="Excel 标题表头清理工具", page_icon="🧹", layout="centered")
    apply_custom_style()
    
    st.title("🧹 Excel 标题表头清理工具")
    st.markdown("自动删除表格标题，处理多行表头合并和左侧合并单元格填充")
    
    with st.expander("⚙️ 参数设置", expanded=True):
        col1, col2, col3 = st.columns(3)
        title_check_rows = col1.number_input("标题检测行数", 1, 10, 3)
        max_value_cols = col2.number_input("标题最大含值列数", 1, 5, 2)
        header_rows = col3.number_input("表头行数", 1, 10, 2)
    
    uploaded_file = st.file_uploader("选择Excel文件", type=['xlsx', 'xls'], help="支持.xlsx和.xls格式")
    
    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file, header=None)
            
            st.subheader("原始数据预览")
            st.dataframe(df.head(10), use_container_width=True)
            st.info(f"数据维度: {df.shape[0]} 行 × {df.shape[1]} 列")
            
            st.subheader("📋 表体区域确认")
            col1, col2, col3 = st.columns(3)
            start_col = col1.text_input("起始列", "A").upper()
            end_col = col2.text_input("终止列", index_to_excel_col(df.shape[1]-1)).upper()
            body_end_row = col3.number_input("表体结束行", 1, df.shape[0], df.shape[0])
            
            if st.button("🧹 开始清理", type="primary"):
                try:
                    start_idx = excel_col_to_index(start_col)
                    end_idx = excel_col_to_index(end_col)
                    
                    if not (0 <= start_idx <= end_idx < df.shape[1]):
                        st.error("列范围超出数据范围")
                        st.stop()
                    
                    with st.spinner("正在处理中..."):
                        selected_df = df.iloc[:body_end_row, start_idx:end_idx+1].copy()
                        cleaned_df, removed_title_rows = clean_excel_data(
                            selected_df, title_check_rows, max_value_cols, header_rows
                        )
                except Exception as e:
                    st.error(f"列名格式错误或处理失败: {str(e)}")
                    st.stop()
                
                st.success("✅ 清理完成！")
                if removed_title_rows > 0:
                    st.info(f"已删除 {removed_title_rows} 行标题")
                
                st.subheader("清理后数据预览")
                st.dataframe(cleaned_df.head(10), use_container_width=True)
                
                # 生成下载文件
                original_name = Path(uploaded_file.name).stem
                excel_buffer = io.BytesIO()
                cleaned_df.to_excel(excel_buffer, index=False)
                excel_buffer.seek(0)
                json_data = cleaned_df.to_json(orient='records', force_ascii=False, indent=2)
                
                # 下载按钮和统计信息
                col1, col2, col3 = st.columns([1, 1, 2])
                col1.download_button("📊 下载Excel", excel_buffer, f"{original_name}_clean.xlsx", 
                                   "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                col2.download_button("📄 下载JSON", json_data, f"{original_name}_clean.json", "application/json")
                
                col1, col2, col3 = st.columns(3)
                col1.metric("原始行数", df.shape[0])
                col2.metric("删除标题行数", removed_title_rows)
                col3.metric("最终行数", cleaned_df.shape[0])
                        
        except Exception as e:
            st.error(f"❌ 文件处理出错: {str(e)}")
            st.info("请确保上传的是有效的Excel文件")

if __name__ == "__main__":
    main()