import streamlit as st
import pandas as pd
import io
import zipfile
from pathlib import Path
from datetime import datetime
from common.ui_style import apply_custom_style


def index_to_excel_col(index):
    """索引转Excel列名 0->A, 1->B"""
    result = ""
    while index >= 0:
        result = chr(index % 26 + ord('A')) + result
        index = index // 26 - 1
    return result


def clean_excel_data(df, title_check_rows=3, max_value_cols=2, header_rows=2):
    """清洗Excel数据"""
    # 删除标题行
    for i in range(min(title_check_rows, len(df))):
        if df.iloc[i].notna().sum() > max_value_cols:
            df = df.iloc[i:].reset_index(drop=True)
            break
    else:
        df = df.iloc[title_check_rows:].reset_index(drop=True)
    
    # 处理表头
    if len(df) >= header_rows:
        new_headers = []
        for col_idx in range(len(df.columns)):
            parts = []
            for row_idx in range(header_rows):
                val = df.iloc[row_idx, col_idx]
                if pd.notna(val):
                    val = str(val).strip()
                    if val and val not in parts:
                        parts.append(val)
            new_headers.append("-".join(parts) if parts else f"Col_{col_idx}")
        
        df = df.iloc[header_rows:].reset_index(drop=True)
        if not df.empty:
            df.columns = new_headers[:len(df.columns)]
    
    # 填充左侧合并单元格
    for col_idx in range(len(df.columns)):
        col_data = df.iloc[:, col_idx]
        if col_data.isna().any() and col_data.count() > 0:
            if col_data.count() / len(col_data) < 0.8 or (col_idx == 0 and pd.notna(col_data.iloc[0])):
                df.iloc[:, col_idx] = col_data.ffill()
        elif col_idx > 0 and col_data.count() == len(col_data):
            break
    
    return df



def process_files(files_data, title_check_rows, max_value_cols, header_rows):
    """处理所有文件并返回ZIP"""
    zip_buffer = io.BytesIO()
    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for i, (file_data, file_name) in enumerate(files_data):
            progress_bar.progress((i + 1) / len(files_data))
            status_text.text(f"正在清洗: {file_name} ({i + 1}/{len(files_data)})")
            
            try:
                df = pd.read_excel(file_data, header=None)
                cleaned_df = clean_excel_data(df, title_check_rows, max_value_cols, header_rows)
                
                base_name = file_name.rsplit('.', 1)[0]
                
                # Excel文件
                excel_buffer = io.BytesIO()
                cleaned_df.to_excel(excel_buffer, index=False)
                zipf.writestr(f"excel/{base_name}_clean.xlsx", excel_buffer.getvalue())
                
                # JSON文件
                json_data = cleaned_df.to_json(orient='records', force_ascii=False, indent=2)
                zipf.writestr(f"json/{base_name}_clean.json", json_data)
                
                boundary_info = f"A-{index_to_excel_col(df.shape[1]-1)}列,{df.shape[0]}行"
                results.append([file_name, boundary_info, df.shape[0], cleaned_df.shape[0], "✅ 成功"])
            except Exception as e:
                results.append([file_name, "处理失败", 0, 0, f"❌ {str(e)[:15]}..."])
    
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
        st.markdown("📏 表头行数")
        header_rows = st.number_input("", 1, 10, 2, help="合并多行表头的行数", label_visibility="collapsed")
    
    with col2:
        st.markdown("⚙️ 高级参数")
        with st.expander("展开设置"):
            sub_col1, sub_col2 = st.columns(2)
            title_check_rows = sub_col1.number_input("标题检测行数", 1, 10, 3, help="检查前几行作为标题删除", label_visibility="collapsed")  
            max_value_cols = sub_col2.number_input("标题最大含值列数", 1, 5, 2, help="标题行最多包含几列有值", label_visibility="collapsed")
    
    # 文件上传
    uploaded_files = st.file_uploader(
        "请选择需要清洗的Excel文件（可多选）。**注意！只支持.xlsx格式！**",
        type=['xlsx'],
        accept_multiple_files=True,
        help="只支持.xlsx格式以确保处理质量，如有.xls文件请先转换为.xlsx"
    )
   
    if uploaded_files:
        st.info(f"📊 已选择 {len(uploaded_files)} 个Excel文件")
        
        # 预览文件信息
        file_info = []
        for file in uploaded_files:
            try:
                df = pd.read_excel(file, header=None, nrows=50)
                boundary = f"A-{index_to_excel_col(df.shape[1]-1)}列"
                file_info.append([file.name, boundary, df.shape[0], df.shape[1]])
            except Exception:
                file_info.append([file.name, "检测失败", 0, 0])
        
        st.dataframe(pd.DataFrame(file_info, columns=['文件名', '检测边界', '行数', '列数']), 
                    use_container_width=True, hide_index=True)
        
        if st.button("🧹 开始清洗", type="primary", use_container_width=True):
            zip_buffer, results = process_files(
                [(f, f.name) for f in uploaded_files], 
                title_check_rows, max_value_cols, header_rows
            )
            
            st.success("✅ 清洗完成!")
            st.dataframe(pd.DataFrame(results, columns=['文件名', '处理区域', '原始行数', '最终行数', '状态']), 
                        use_container_width=True, hide_index=True)
            
            success_count = sum(1 for r in results if r[4].startswith('✅'))
            col1, col2 = st.columns(2)
            col1.metric("处理成功", success_count)
            col2.metric("处理失败", len(results) - success_count)
            
            if success_count > 0:
                timestamp = datetime.now().strftime("%Y%m%d%H%M")
                st.download_button("📥 下载清洗文件", zip_buffer.getvalue(), 
                                 f"excel_标题清洗_{timestamp}.zip", "application/zip", 
                                 type="primary", use_container_width=True)
                st.info("💡 已将Excel和JSON文件分别放在excel和json文件夹中")

if __name__ == "__main__":
    main()