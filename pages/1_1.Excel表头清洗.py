import streamlit as st
import pandas as pd
import io
from pathlib import Path
from common.ui_style import apply_custom_style

def detect_and_remove_title(df, title_check_rows=3, max_value_cols=2):
    """
    检测并删除表格标题行
    """
    title_rows_to_remove = []
    
    for i in range(min(title_check_rows, len(df))):
        non_empty_count = df.iloc[i].notna().sum()
        if non_empty_count <= max_value_cols:
            title_rows_to_remove.append(i)
        else:
            break  # 遇到不是标题的行就停止
    
    if title_rows_to_remove:
        df_no_title = df.drop(df.index[title_rows_to_remove]).reset_index(drop=True)
        return df_no_title, len(title_rows_to_remove)
    else:
        return df, 0

def process_headers(df, header_rows=2):
    """
    处理多行表头的合并单元格
    """
    if len(df) < header_rows:
        return df
    
    # 1. 提取并处理表头行
    header_data = []
    for i in range(header_rows):
        header_data.append(df.iloc[i].ffill())  # 每行表头向右填充
    
    # 2. 生成新表头：组合多层表头
    new_headers = []
    for col_idx in range(len(df.columns)):
        header_parts = []
        for row_idx in range(header_rows):
            val = str(header_data[row_idx].iloc[col_idx]) if pd.notna(header_data[row_idx].iloc[col_idx]) else ""
            if val:
                header_parts.append(val)
        
        # 去重并组合
        unique_parts = []
        for part in header_parts:
            if part not in unique_parts:
                unique_parts.append(part)
        
        new_headers.append("-".join(unique_parts) if unique_parts else f"Col_{col_idx}")
    
    # 3. 提取数据区域
    data_df = df.iloc[header_rows:].copy() if len(df) > header_rows else pd.DataFrame()
    
    # 4. 重建DataFrame
    if not data_df.empty:
        data_df.columns = new_headers[:len(data_df.columns)]
        return data_df
    else:
        result_df = pd.DataFrame(columns=new_headers)
        return result_df

def main():
    st.set_page_config(
        page_title="Excel 标题表头清理工具",
        page_icon="🧹",
        layout="centered"
    )
    
    # 应用通用样式
    apply_custom_style()
    
    st.title("🧹 Excel 标题表头清理工具")
    st.markdown("自动删除表格标题，处理多行表头合并")
    
    # 参数设置
    with st.expander("⚙️ 参数设置", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            title_check_rows = st.number_input("标题检测行数", min_value=1, max_value=10, value=3)
        with col2:
            max_value_cols = st.number_input("标题最大含值列数", min_value=1, max_value=5, value=2)
        with col3:
            header_rows = st.number_input("表头行数", min_value=1, max_value=10, value=2)
    
    # 文件上传
    uploaded_file = st.file_uploader(
        "选择Excel文件", 
        type=['xlsx', 'xls'],
        help="支持.xlsx和.xls格式"
    )
    
    if uploaded_file is not None:
        try:
            # 读取Excel文件（不设表头，全部作为数据读取）
            df = pd.read_excel(uploaded_file, header=None)
            
            st.subheader("原始数据预览")
            st.dataframe(df.head(10), use_container_width=True)
            
            # 显示原始数据信息
            st.info(f"数据维度: {df.shape[0]} 行 × {df.shape[1]} 列")
            
            # 处理按钮
            if st.button("🧹 开始清理", type="primary"):
                with st.spinner("正在处理中..."):
                    # 1. 删除标题行
                    df_no_title, removed_title_rows = detect_and_remove_title(
                        df, title_check_rows, max_value_cols
                    )
                    
                    # 2. 处理表头
                    cleaned_df = process_headers(df_no_title, header_rows)
                    
                    st.success("✅ 清理完成！")
                    
                    # 显示处理步骤
                    if removed_title_rows > 0:
                        st.info(f"已删除 {removed_title_rows} 行标题")
                    
                    # 显示处理后的数据
                    st.subheader("清理后数据预览")
                    st.dataframe(cleaned_df.head(10), use_container_width=True)
                    
                    # 生成输出文件名
                    original_name = Path(uploaded_file.name).stem
                    output_filename = f"{original_name}_clean.xlsx"
                    
                    # 转换为Excel字节流
                    buffer = io.BytesIO()
                    cleaned_df.to_excel(buffer, index=False)
                    buffer.seek(0)
                    
                    # 下载按钮
                    st.download_button(
                        label="💾 下载清理后文件",
                        data=buffer,
                        file_name=output_filename,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                    
                    # 显示统计信息
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("原始行数", df.shape[0])
                    with col2:
                        st.metric("删除标题行数", removed_title_rows)
                    with col3:
                        st.metric("最终行数", cleaned_df.shape[0])
                        
        except Exception as e:
            st.error(f"❌ 文件处理出错: {str(e)}")
            st.info("请确保上传的是有效的Excel文件")

if __name__ == "__main__":
    main()