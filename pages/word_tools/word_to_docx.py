import streamlit as st
import subprocess
import tempfile
import io
import zipfile
import pandas as pd
from pathlib import Path
from datetime import datetime
from common.ui_style import apply_custom_style


def convert_doc_to_docx(file_data, file_name, zip_writer):
    """使用LibreOffice将doc转换为docx并添加到zip"""
    with tempfile.NamedTemporaryFile(suffix='.doc', delete=False) as input_temp:
        input_temp.write(file_data.getvalue())
        input_path = input_temp.name
    
    output_path = input_path.replace('.doc', '.docx')
    
    try:
        subprocess.run([
            '/Applications/LibreOffice.app/Contents/MacOS/soffice', '--headless', '--convert-to', 'docx', 
            '--outdir', str(Path(input_path).parent), input_path
        ], check=True, timeout=60)
        
        with open(output_path, 'rb') as f:
            zip_writer.writestr(f"{Path(file_name).stem}.docx", f.read())
        
    finally:
        Path(input_path).unlink(missing_ok=True)
        Path(output_path).unlink(missing_ok=True)


def process_files(files_data):
    """处理所有文件并返回ZIP"""
    zip_buffer = io.BytesIO()
    results = []
    total_files = len(files_data)
    
    # 创建进度条
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for i, (file_data, file_name) in enumerate(files_data):
            # 更新进度
            progress = (i + 1) / total_files
            progress_bar.progress(progress)
            status_text.text(f"正在转换: {file_name} ({i + 1}/{total_files})")
            
            try:
                convert_doc_to_docx(file_data, file_name, zipf)
                results.append([file_name, '✅ 转换成功'])
            except Exception as e:
                results.append([file_name, f'❌ {str(e)[:15]}...'])
    
    # 清除进度显示
    progress_bar.empty()
    status_text.empty()
    
    return zip_buffer, results


def main():
    st.set_page_config(page_title="Word DOC 转 DOCX 工具", page_icon="📄", layout="centered")
    apply_custom_style()
    
    st.title("📄 Word DOC 转 DOCX 工具")
    st.markdown("将 .doc 格式文件转换为 .docx 格式")
    st.markdown("---")
    
    uploaded_files = st.file_uploader(
        "选择DOC文件进行转换（可多选）",
        type=['doc'],
        accept_multiple_files=True,
        help="支持单个或多个 .doc 文件上传，使用 LibreOffice 转换引擎"
    )
    
    if uploaded_files:
        st.info(f"📊 已选择 {len(uploaded_files)} 个DOC文件")
        
        if st.button("🔄 开始转换", type="primary", use_container_width=True):
            files_data = [(f, f.name) for f in uploaded_files]
            zip_buffer, results = process_files(files_data)
            
            st.success("✅ 转换完成!")
            
            # 显示结果和统计
            st.dataframe(pd.DataFrame(results, columns=['文件名', '状态']), use_container_width=True, hide_index=True)
            
            success_count = sum(1 for r in results if r[1].startswith('✅'))
            col1, col2 = st.columns(2)
            col1.metric("转换成功", success_count)
            col2.metric("转换失败", len(results) - success_count)
            
            # 下载
            if success_count > 0:
                timestamp = datetime.now().strftime("%Y%m%d%H%M")
                filename = f"doc_to_docx_转换_{timestamp}.zip" if len(uploaded_files) > 1 else f"{Path(uploaded_files[0].name).stem}_{timestamp}.zip"
                st.download_button("📥 下载转换文件", zip_buffer.getvalue(), filename, "application/zip", type="primary", use_container_width=True)


if __name__ == "__main__":
    main()