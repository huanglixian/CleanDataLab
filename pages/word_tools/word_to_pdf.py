import streamlit as st
import io
import zipfile
import pandas as pd
import time
from pathlib import Path
from datetime import datetime
from common.ui_style import apply_custom_style
from common.libreoffice_queue import lo_queue

def main():
    st.set_page_config(page_title="Word 转 PDF 工具", page_icon="📄", layout="centered")
    apply_custom_style()
    
    
    # 初始化
    if "word_pdf_key" not in st.session_state:
        st.session_state.word_pdf_key = 0
    
    st.title("📄 Word 转 PDF 工具")
    st.markdown("将 .doc 或 .docx 格式文件转换为 PDF 格式")
    st.markdown("---")
    
    uploaded_files = st.file_uploader(
        "选择Word文件进行转换（可多选）",
        type=['doc', 'docx'],
        accept_multiple_files=True,
        help="支持单个或多个 .doc/.docx 文件上传，使用 LibreOffice 转换引擎",
        key=f"uploader_{st.session_state.word_pdf_key}"
    )
    
    if uploaded_files:
        file_count = len(uploaded_files)
        st.info(f"📄 已选择 {file_count} 个Word文件")
        
        if st.button("🔄 开始转换", type="primary", use_container_width=True, disabled="word_pdf_task_running" in st.session_state):
            st.session_state.word_pdf_task_running = True
            st.rerun()
        
        # 处理任务
        if st.session_state.get('word_pdf_task_running') and not st.session_state.get('word_pdf_result'):
            files_data = [(file.name, file.getvalue()) for file in uploaded_files]
            task_id = lo_queue.submit_task(files_data, 'docx', 'pdf')
            
            # 状态显示
            status_placeholder = st.empty()
            
            while True:
                position = lo_queue.get_task_position(task_id)
                task_status = lo_queue.get_task_status(task_id)
                
                if position > 0:
                    status_placeholder.warning(f"⏳ 排队中，第 {position} 位")
                elif task_status == "processing":
                    status_placeholder.info("🔄 正在转换中...")
                elif task_status == "completed":
                    status_placeholder.success("✅ 转换完成")
                    conversion_results = lo_queue.wait_for_task(task_id)
                    break
                else:
                    conversion_results = None
                    break
                
                time.sleep(1)
            
            if conversion_results:
                zip_buffer = io.BytesIO()
                results = []
                
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for filename, content, error in conversion_results:
                        if content:
                            zipf.writestr(f"{Path(filename).stem}.pdf", content)
                            results.append([filename, '✅ 转换成功'])
                        else:
                            results.append([filename, f'❌ {error}'])
                
                st.session_state.word_pdf_result = (zip_buffer, results)
                status_placeholder.empty()
            else:
                status_placeholder.error("转换超时，请重试")
        
        # 显示结果
        if st.session_state.get('word_pdf_result'):
            zip_buffer, results = st.session_state.word_pdf_result
            success_count = sum(1 for r in results if r[1].startswith('✅'))
            
            st.success("✅ 转换完成!")
            st.dataframe(pd.DataFrame(results, columns=['文件名', '状态']), use_container_width=True, hide_index=True)
            
            col1, col2 = st.columns(2)
            col1.metric("转换成功", success_count)
            col2.metric("转换失败", len(results) - success_count)
            
            if success_count > 0:
                timestamp = datetime.now().strftime("%Y%m%d%H%M")
                filename = f"word_to_pdf_转换_{timestamp}.zip" if file_count > 1 else f"{Path(uploaded_files[0].name).stem}_{timestamp}.zip"
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.download_button("📥 下载PDF文件", zip_buffer.getvalue(), filename, "application/zip", type="primary", use_container_width=True)
                with col2:
                    if st.button("🔄 重置页面", type="secondary", use_container_width=True):
                        st.session_state.word_pdf_key += 1
                        st.session_state.pop('word_pdf_result', None)
                        st.session_state.pop('word_pdf_task_running', None)
                        st.rerun()


if __name__ == "__main__":
    main()
