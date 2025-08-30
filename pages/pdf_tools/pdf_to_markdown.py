import streamlit as st
import io
import zipfile
import pandas as pd
import time
from pathlib import Path
from datetime import datetime
from common.ui_style import apply_custom_style
from common.file_processing_queue import fp_queue

def convert_pdf_to_markdown_safe(pdf_content, filename):
    """安全地转PDF为Markdown，防止临时文件冲突"""
    try:
        import pymupdf4llm
        import os
        import tempfile
        import uuid
        
        # 使用UUID保证临时文件名唯一
        unique_id = str(uuid.uuid4())
        with tempfile.NamedTemporaryFile(suffix=f'_{unique_id}.pdf', delete=False) as temp_file:
            temp_pdf = temp_file.name
            temp_file.write(pdf_content)
        
        try:
            markdown_content = pymupdf4llm.to_markdown(temp_pdf)
            return markdown_content, None
        except Exception as e:
            return None, str(e)[:20]
        finally:
            if os.path.exists(temp_pdf):
                os.remove(temp_pdf)
    
    except ImportError:
        return None, "缺少pymupdf4llm库"
    except Exception as e:
        return None, str(e)[:20]

def process_files_batch(files_data):
    """批处理PDF文件并返回结果"""
    zip_buffer = io.BytesIO()
    results = []
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_name, file_content in files_data:
            markdown_content, error = convert_pdf_to_markdown_safe(file_content, file_name)
            
            if markdown_content:
                md_filename = f"{Path(file_name).stem}.md"
                zipf.writestr(md_filename, markdown_content.encode('utf-8'))
                results.append([file_name, '✅ 转换成功'])
            else:
                results.append([file_name, f'❌ {error}'])
    
    return zip_buffer, results

def main():
    st.set_page_config(page_title="PDF 转 Markdown 工具", page_icon="📋", layout="centered")
    apply_custom_style()
    
    # 初始化
    if "key" not in st.session_state:
        st.session_state.key = 0
    
    st.title("📋 PDF 转 Markdown 工具")
    st.markdown("将 PDF 文件转换为 Markdown 格式")
    st.markdown("---")
    
    uploaded_files = st.file_uploader(
        "选择PDF文件进行转换（可多选）",
        type=['pdf'],
        accept_multiple_files=True,
        help="支持单个或多个 PDF 文件上传，使用 pymupdf4llm 转换引擎",
        key=f"uploader_{st.session_state.key}"
    )
    
    if uploaded_files:
        file_count = len(uploaded_files)
        st.info(f"📋 已选择 {file_count} 个PDF文件")
        
        if st.button("🔄 开始转换", type="primary", use_container_width=True):
            files_data = [(file.name, file.getvalue()) for file in uploaded_files]
            task_id = fp_queue.submit_task(files_data, process_files_batch)
            
            # 状态显示
            status_placeholder = st.empty()
            
            while True:
                position = fp_queue.get_task_position(task_id)
                task_status = fp_queue.get_task_status(task_id)
                
                if position > 0:
                    status_placeholder.warning(f"⏳ 排队中，第 {position} 位")
                elif task_status == "processing":
                    status_placeholder.info("🔄 正在转换中...")
                elif task_status == "completed":
                    status_placeholder.success("✅ 转换完成")
                    zip_buffer, results = fp_queue.wait_for_task(task_id)
                    break
                else:
                    zip_buffer, results = None, None
                    break
                
                time.sleep(1)
            
            if zip_buffer and results:
                st.session_state.result = (zip_buffer, results)
                status_placeholder.empty()
            else:
                status_placeholder.error("转换超时，请重试")
        
        # 显示结果
        if st.session_state.get('result'):
            zip_buffer, results = st.session_state.result
            success_count = sum(1 for r in results if r[1].startswith('✅'))
            
            st.success("✅ 转换完成!")
            st.dataframe(pd.DataFrame(results, columns=['文件名', '状态']), use_container_width=True, hide_index=True)
            
            col1, col2 = st.columns(2)
            col1.metric("转换成功", success_count)
            col2.metric("转换失败", len(results) - success_count)
            
            if success_count > 0:
                timestamp = datetime.now().strftime("%Y%m%d%H%M")
                filename = f"pdf_to_markdown_转换_{timestamp}.zip" if file_count > 1 else f"{Path(uploaded_files[0].name).stem}_{timestamp}.zip"
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.download_button("📥 下载转换文件", zip_buffer.getvalue(), filename, "application/zip", type="primary", use_container_width=True)
                with col2:
                    if st.button("🔄 重置页面", type="secondary", use_container_width=True):
                        st.session_state.key += 1
                        del st.session_state.result
                        st.rerun()
                
                st.markdown("**如对转换效果不满意（复杂PDF），请跳转[MinerU](https://mineru.net/OpenSourceTools/Extractor)**")


if __name__ == "__main__":
    main()
