import streamlit as st
import pandas as pd
import io
import zipfile
import glob
from pathlib import Path
from common.ui_style import apply_custom_style


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

def generate_downloads(cleaned_df):
    """生成Excel和JSON下载文件"""
    excel_buffer = io.BytesIO()
    cleaned_df.to_excel(excel_buffer, index=False)
    excel_buffer.seek(0)
    json_data = cleaned_df.to_json(orient='records', force_ascii=False, indent=2)
    return excel_buffer, json_data

def process_batch_files(folder_path, title_check_rows, max_value_cols, header_rows):
    """批量处理文件夹中的Excel文件"""
    excel_files = []
    for ext in ['*.xlsx', '*.xls']:
        excel_files.extend(glob.glob(f"{folder_path}/**/{ext}", recursive=True))
    
    if not excel_files:
        return None, "📂 未找到Excel文件"
    
    zip_buffer = io.BytesIO()
    results = []
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in excel_files:
            try:
                df = pd.read_excel(file_path, header=None)
                cleaned_df, removed_title_rows = clean_excel_data(df, title_check_rows, max_value_cols, header_rows)
                
                # 保存文件到ZIP
                original_name = Path(file_path).stem
                excel_buffer, json_data = generate_downloads(cleaned_df)
                zipf.writestr(f"excel/{original_name}_clean.xlsx", excel_buffer.getvalue())
                zipf.writestr(f"json/{original_name}_clean.json", json_data)
                
                results.append([Path(file_path).name, df.shape[0], removed_title_rows, cleaned_df.shape[0], "✅ 成功"])
                
            except Exception as e:
                results.append([Path(file_path).name, 0, 0, 0, f"❌ {str(e)[:15]}..."])
    
    return zip_buffer, results

def display_results(results, zip_buffer=None, folder_name=None):
    """显示处理结果和统计信息"""
    st.subheader("📦 处理结果")
    result_df = pd.DataFrame(results, columns=['文件名', '原始行数', '删除标题行数', '最终行数', '状态'])
    st.dataframe(result_df, use_container_width=True, hide_index=True)
    
    # 统计信息
    processed = sum(1 for r in results if r[4] == "✅ 成功")
    failed = len(results) - processed
    
    col1, col2 = st.columns(2)
    col1.metric("处理成功", processed)
    col2.metric("处理失败", failed)
    
    # 下载按钮
    if zip_buffer and folder_name:
        st.download_button(
            "📥 下载所有清理文件",
            zip_buffer.getvalue(),
            f"{folder_name}_cleaned.zip",
            "application/zip",
            type="primary",
            use_container_width=True
        )
        st.info("💡 已将Excel和JSON文件分别放在excel和json文件夹中")


def main():
    st.set_page_config(page_title="Excel 标题表头清理工具", page_icon="🧹", layout="centered")
    apply_custom_style()
    
    st.title("🧹 Excel 标题表头清理工具")
    st.markdown("自动删除表格标题，处理多行表头合并和左侧合并单元格填充")
    
    # 核心参数同行
    col1, col2 = st.columns([1, 1])
    
    with col1:
        mode = st.radio(
            "操作模式",
            ["🔹 单文件处理", "📁 批量文件夹处理"],
            horizontal=True,
            help="批量模式会递归处理文件夹中所有Excel文件"
        )
    
    with col2:
        header_rows = st.number_input("📏 表头行数", 1, 10, 2, help="合并多行表头的行数")
    
    # 高级参数折叠
    with st.expander("⚙️ 高级参数"):
        col1, col2 = st.columns(2)
        title_check_rows = col1.number_input("标题检测行数", 1, 10, 3, help="检查前几行作为标题删除")  
        max_value_cols = col2.number_input("标题最大含值列数", 1, 5, 2, help="标题行最多包含几列有值")
    
    if mode == "📁 批量文件夹处理":
        folder_path = st.text_input(
            "📁 请输入Excel文件夹路径",
            placeholder="例如: /Users/用户名/Documents/Excel文件夹",
            help="输入包含Excel文件的文件夹绝对路径，支持递归搜索子文件夹"
        )
        
        if folder_path and st.button("🧹 开始批量清理", type="primary"):
            if Path(folder_path).exists():
                with st.spinner("正在批量处理Excel文件..."):
                    zip_buffer, results = process_batch_files(folder_path, title_check_rows, max_value_cols, header_rows)
                
                if isinstance(results, str):
                    st.warning(results)
                else:
                    st.success("✅ 批量处理完成！")
                    display_results(results, zip_buffer, Path(folder_path).name)
            else:
                st.error("❌ 文件夹路径不存在，请检查路径是否正确")
    
    else:  # 🔹 单文件处理
        uploaded_file = st.file_uploader("选择Excel文件", type=['xlsx', 'xls'], help="支持.xlsx和.xls格式")
        
        if uploaded_file:
            try:
                df = pd.read_excel(uploaded_file, header=None)  # 只读取一次
                
                # 显示预览
                st.subheader("数据预览")
                st.dataframe(df.head(10), use_container_width=True)
                st.info(f"数据维度: {df.shape[0]} 行 × {df.shape[1]} 列")
                
                if st.button("🧹 开始清理", type="primary"):
                    with st.spinner("正在处理中..."):
                        cleaned_df, removed_title_rows = clean_excel_data(df, title_check_rows, max_value_cols, header_rows)
                    
                    st.success("✅ 清洗完成！")
                    
                    # 显示清理后结果
                    st.subheader("清洗后数据")
                    st.dataframe(cleaned_df.head(10), use_container_width=True)
                    
                    # 下载按钮
                    original_name = Path(uploaded_file.name).stem
                    excel_buffer, json_data = generate_downloads(cleaned_df)
                    
                    col1, col2 = st.columns(2)
                    col1.download_button("📊 下载Excel", excel_buffer, f"{original_name}_clean.xlsx", 
                                       "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                    col2.download_button("📄 下载JSON", json_data, f"{original_name}_clean.json", "application/json")
                            
            except Exception as e:
                st.error(f"❌ 文件处理出错: {str(e)}")
                st.info("请确保上传的是有效的Excel文件")

if __name__ == "__main__":
    main()