import streamlit as st
import subprocess
import tempfile
import io
import zipfile
import glob
import pandas as pd
from pathlib import Path
from common.ui_style import apply_custom_style


def convert_doc_to_docx(file_data, file_name, output_folder_name, zip_writer):
    """使用LibreOffice将doc转换为docx"""
    base_name = Path(file_name).stem
    
    with tempfile.NamedTemporaryFile(suffix='.doc', delete=False) as input_temp:
        input_temp.write(file_data.read() if hasattr(file_data, 'read') else file_data.getvalue())
        input_path = input_temp.name
    
    output_path = input_path.replace('.doc', '.docx')
    
    try:
        subprocess.run([
            '/Applications/LibreOffice.app/Contents/MacOS/soffice', '--headless', '--convert-to', 'docx', 
            '--outdir', str(Path(input_path).parent), input_path
        ], check=True, timeout=60)
        
        with open(output_path, 'rb') as f:
            docx_data = f.read()
        
        zip_writer.writestr(f"{output_folder_name}/{base_name}.docx", docx_data)
        return True
        
    finally:
        Path(input_path).unlink(missing_ok=True)
        Path(output_path).unlink(missing_ok=True)


def convert_single_file(file_data, file_name):
    """转换单个文件并返回docx数据"""
    base_name = Path(file_name).stem
    
    with tempfile.NamedTemporaryFile(suffix='.doc', delete=False) as input_temp:
        input_temp.write(file_data.read() if hasattr(file_data, 'read') else file_data.getvalue())
        input_path = input_temp.name
    
    output_path = input_path.replace('.doc', '.docx')
    
    try:
        subprocess.run([
            '/Applications/LibreOffice.app/Contents/MacOS/soffice', '--headless', '--convert-to', 'docx', 
            '--outdir', str(Path(input_path).parent), input_path
        ], check=True, timeout=60)
        
        with open(output_path, 'rb') as f:
            return f.read()
        
    finally:
        Path(input_path).unlink(missing_ok=True)
        Path(output_path).unlink(missing_ok=True)


def process_and_display(files_data, is_batch=False):
    """统一处理和显示逻辑"""
    if not files_data:
        return st.warning("📂 未找到DOC文件")
    
    # 显示文件信息
    st.subheader("📋 发现的DOC文件")
    file_info = []
    for file_path, file_name in files_data:
        size = (Path(file_path).stat().st_size if isinstance(file_path, str) else len(file_path.getvalue())) / 1024
        file_info.append([file_name, f"{size:.1f}"])
    
    df = pd.DataFrame(file_info, columns=['文件名', '大小(KB)'])
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    if is_batch:
        st.success(f"📊 共发现 {len(files_data)} 个DOC文件")
    
    # 处理按钮和逻辑
    if st.button("🔄 开始批量转换" if is_batch else "🔄 开始转换", type="primary", use_container_width=True):
        with st.spinner("正在转换DOC文件..."):
            if is_batch:
                # 批量模式：使用zip打包
                first_file_path = files_data[0][0]
                source_folder = Path(first_file_path).parent.name if isinstance(first_file_path, str) else "批量"
                folder_name = f"{source_folder}_批量转换"
                
                zip_buffer = io.BytesIO()
                results = []
                
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for file_path, file_name in files_data:
                        try:
                            if isinstance(file_path, str):
                                with open(file_path, 'rb') as f:
                                    file_data = io.BytesIO(f.read())
                            else:
                                file_data = file_path
                            
                            convert_doc_to_docx(file_data, file_name, folder_name, zipf)
                            results.append([file_name, '✅ 转换成功'])
                            
                        except Exception as e:
                            results.append([file_name, f'❌ {str(e)[:15]}...'])
                
                # 显示结果
                st.success("✅ 转换完成!")
                st.subheader("📦 转换结果")
                result_df = pd.DataFrame(results, columns=['源文件', '状态'])
                st.dataframe(result_df, use_container_width=True, hide_index=True)
                
                # 统计信息
                success_count = sum(1 for r in results if r[1].startswith('✅'))
                failed_count = len(results) - success_count
                
                col1, col2 = st.columns(2)
                col1.metric("转换成功", success_count)
                col2.metric("转换失败", failed_count)
                
                # 下载zip
                if success_count > 0:
                    st.download_button(
                        "📥 下载转换文件",
                        zip_buffer.getvalue(),
                        f"{folder_name}.zip",
                        "application/zip",
                        type="primary",
                        use_container_width=True
                    )
                    st.info(f"💡 所有转换文件已统一放在 `{folder_name}` 文件夹中")
            
            else:
                # 单文件模式：直接下载docx文件
                file_path, file_name = files_data[0]
                base_name = Path(file_name).stem
                
                try:
                    if isinstance(file_path, str):
                        with open(file_path, 'rb') as f:
                            file_data = io.BytesIO(f.read())
                    else:
                        file_data = file_path
                    
                    docx_data = convert_single_file(file_data, file_name)
                    
                    st.success("✅ 转换成功!")
                    st.download_button(
                        "📥 下载DOCX文件",
                        docx_data,
                        f"{base_name}.docx",
                        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        type="primary",
                        use_container_width=True
                    )
                    
                except Exception as e:
                    st.error(f"❌ 转换失败: {str(e)}")


def main():
    st.set_page_config(page_title="Word DOC 转 DOCX 工具", page_icon="📄", layout="centered")
    apply_custom_style()
    
    st.title("📄 Word DOC 转 DOCX 工具")
    st.markdown("将 .doc 格式文件转换为 .docx 格式")
    st.markdown("---")
    
    mode = st.radio(
        "选择操作模式",
        ["🔹 单文件转换", "📁 批量文件夹转换"],
        horizontal=True,
        help="批量模式支持文件夹递归搜索，使用LibreOffice转换引擎"
    )
    
    if mode == "📁 批量文件夹转换":
        folder_path = st.text_input(
            "📁 请输入DOC文件夹路径",
            placeholder="例如: /Users/用户名/Documents/Word文件夹",
            help="输入包含DOC文件的文件夹绝对路径，支持子文件夹递归搜索"
        )
        
        if folder_path:
            if Path(folder_path).exists():
                doc_files = glob.glob(f"{folder_path}/**/*.doc", recursive=True)
                files_data = [(file_path, Path(file_path).name) for file_path in doc_files]
                process_and_display(files_data, is_batch=True)
            else:
                st.error("❌ 文件夹路径不存在，请检查路径是否正确")

    else:  # 单文件模式
        uploaded_files = st.file_uploader(
            "选择要转换的DOC文件", 
            type=['doc'], 
            accept_multiple_files=True,
            help="支持批量上传 .doc 文件，使用 LibreOffice 转换"
        )
        
        if uploaded_files:
            files_data = [(f, f.name) for f in uploaded_files]
            process_and_display(files_data, is_batch=False)


if __name__ == "__main__":
    main()