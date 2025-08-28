import streamlit as st
import pandas as pd
import io
import zipfile
from pathlib import Path
from datetime import datetime
from common.ui_style import apply_custom_style


def excel_col_to_index(col_str):
    """Excel列名转索引 A->0, B->1"""
    result = 0
    for char in col_str.upper():
        result = result * 26 + (ord(char) - ord('A') + 1)
    return result - 1

def index_to_excel_col(index):
    """索引转Excel列名 0->A, 1->B"""
    result = ""
    while index >= 0:
        result = chr(index % 26 + ord('A')) + result
        index = index // 26 - 1
    return result

def detect_data_boundary(df):
    """检测数据边界"""
    start_col = 0
    end_col = df.shape[1] - 1
    body_end_row = df.shape[0]
    return start_col, end_col, body_end_row


def clean_excel_data(df, start_col, end_col, body_end_row, title_check_rows=3, max_value_cols=2, header_rows=2):
    """清洗指定区域的Excel数据"""
    # 选择指定区域
    selected_df = df.iloc[:body_end_row, start_col:end_col+1].copy()
    
    # 删除标题行
    removed_title_rows = 0
    for i in range(min(title_check_rows, len(selected_df))):
        if selected_df.iloc[i].notna().sum() <= max_value_cols:
            removed_title_rows += 1
        else:
            break
    
    if removed_title_rows > 0:
        selected_df = selected_df.drop(selected_df.index[:removed_title_rows]).reset_index(drop=True)
    
    # 处理表头
    if len(selected_df) >= header_rows:
        header_data = [selected_df.iloc[i].ffill() for i in range(header_rows)]
        new_headers = []
        for col_idx in range(len(selected_df.columns)):
            parts = [str(header_data[i].iloc[col_idx]) for i in range(header_rows) 
                    if pd.notna(header_data[i].iloc[col_idx]) and str(header_data[i].iloc[col_idx])]
            unique_parts = list(dict.fromkeys(parts))
            new_headers.append("-".join(unique_parts) if unique_parts else f"Col_{col_idx}")
        
        selected_df = selected_df.iloc[header_rows:].copy()
        if not selected_df.empty:
            selected_df.columns = new_headers[:len(selected_df.columns)]
    
    # 填充左侧合并单元格
    for col_idx in range(len(selected_df.columns)):
        col_data = selected_df.iloc[:, col_idx]
        if col_data.isna().any() and col_data.count() > 0:
            non_null_ratio = col_data.count() / len(col_data)
            if non_null_ratio < 0.8 or (col_idx == 0 and pd.notna(col_data.iloc[0])):
                selected_df.iloc[:, col_idx] = col_data.ffill()
        elif col_idx > 0 and col_data.count() == len(col_data):
            break
    
    return selected_df

def clean_excel_file(file_data, file_name, zip_writer, title_check_rows=3, max_value_cols=2, header_rows=2):
    """清洗Excel文件并添加到zip"""
    df = pd.read_excel(file_data, header=None)
    start_col, end_col, body_end_row = detect_data_boundary(df)
    cleaned_df = clean_excel_data(df, start_col, end_col, body_end_row, title_check_rows, max_value_cols, header_rows)
    
    # 生成文件
    base_name = Path(file_name).stem
    
    # Excel文件
    excel_buffer = io.BytesIO()
    cleaned_df.to_excel(excel_buffer, index=False)
    zip_writer.writestr(f"excel/{base_name}_clean.xlsx", excel_buffer.getvalue())
    
    # JSON文件
    json_data = cleaned_df.to_json(orient='records', force_ascii=False, indent=2)
    zip_writer.writestr(f"json/{base_name}_clean.json", json_data)
    
    # 返回处理信息
    boundary_info = f"{index_to_excel_col(start_col)}-{index_to_excel_col(end_col)}列,{body_end_row}行"
    return boundary_info, df.shape[0], cleaned_df.shape[0]


def process_files(files_data, title_check_rows, max_value_cols, header_rows):
    """处理所有文件并返回ZIP"""
    zip_buffer = io.BytesIO()
    results = []
    
    # 创建进度条
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for i, (file_data, file_name) in enumerate(files_data):
            # 更新进度
            progress_bar.progress((i + 1) / len(files_data))
            status_text.text(f"正在清洗: {file_name} ({i + 1}/{len(files_data)})")
            
            try:
                boundary_info, original_rows, final_rows = clean_excel_file(
                    file_data, file_name, zipf, title_check_rows, max_value_cols, header_rows
                )
                results.append([file_name, boundary_info, original_rows, final_rows, "✅ 成功"])
            except Exception as e:
                results.append([file_name, "处理失败", 0, 0, f"❌ {str(e)[:15]}..."])
    
    # 清除进度显示
    progress_bar.empty()
    status_text.empty()
    
    return zip_buffer, results


def main():
    st.set_page_config(page_title="Excel 标题表头清理工具", page_icon="🧹", layout="centered")
    apply_custom_style()
    
    st.title("🧹 Excel 标题表头清理工具")
    st.markdown("自动删除表格标题，处理多行表头合并和左侧合并单元格填充")
    st.markdown("---")
    
    # 参数设置
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("**📏 表头行数**")
        header_rows = st.number_input("", 1, 10, 2, help="合并多行表头的行数", label_visibility="collapsed")
    
    with col2:
        st.markdown("**⚙️ 高级参数**")
        with st.expander("展开设置"):
            sub_col1, sub_col2 = st.columns(2)
            title_check_rows = sub_col1.number_input("标题检测行数", 1, 10, 3, help="检查前几行作为标题删除")  
            max_value_cols = sub_col2.number_input("标题最大含值列数", 1, 5, 2, help="标题行最多包含几列有值")
    
    # 文件上传
    uploaded_files = st.file_uploader(
        "请选择需要清洗的Excel文件（可多选）。**注意！只支持.xlsx格式！**",
        type=['xlsx'],
        accept_multiple_files=True,
        help="只支持.xlsx格式以确保处理质量，如有.xls文件请先转换为.xlsx"
    )
   
    if uploaded_files:
        st.info(f"📊 已选择 {len(uploaded_files)} 个Excel文件")
        
        # Excel预览（只显示边界检测）
        st.subheader("📋 处理预览")
        file_info = []
        
        for file in uploaded_files:
            try:
                df = pd.read_excel(file, header=None, nrows=50)  # 只读50行用于边界检测
                start_col, end_col, _ = detect_data_boundary(df)
                boundary_info = f"{index_to_excel_col(start_col)}-{index_to_excel_col(end_col)}列"
                file_info.append([file.name, boundary_info, df.shape[0], df.shape[1]])
            except Exception:
                file_info.append([file.name, "检测失败", 0, 0])
        
        df_preview = pd.DataFrame(file_info, columns=['文件名', '检测边界', '行数', '列数'])
        st.dataframe(df_preview, use_container_width=True, hide_index=True)
        
        if st.button("🧹 开始清洗", type="primary", use_container_width=True):
            files_data = [(f, f.name) for f in uploaded_files]
            zip_buffer, results = process_files(files_data, title_check_rows, max_value_cols, header_rows)
            
            st.success("✅ 清洗完成!")
            
            # 显示结果和统计
            st.dataframe(pd.DataFrame(results, columns=['文件名', '处理区域', '原始行数', '最终行数', '状态']), 
                        use_container_width=True, hide_index=True)
            
            success_count = sum(1 for r in results if r[4].startswith('✅'))
            failed_count = len(results) - success_count
            
            col1, col2 = st.columns(2)
            col1.metric("处理成功", success_count)
            col2.metric("处理失败", failed_count)
            
            # 下载
            if success_count > 0:
                timestamp = datetime.now().strftime("%Y%m%d%H%M")
                filename = f"excel_标题清洗_{timestamp}.zip"
                st.download_button("📥 下载清洗文件", zip_buffer.getvalue(), filename, "application/zip", 
                                 type="primary", use_container_width=True)
                st.info("💡 已将Excel和JSON文件分别放在excel和json文件夹中")

if __name__ == "__main__":
    main()