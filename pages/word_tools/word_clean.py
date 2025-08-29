import streamlit as st
import io
import zipfile
import pandas as pd

from pathlib import Path
from datetime import datetime
from common.ui_style import apply_custom_style

def main():
    st.set_page_config(page_title="Word DOCX 清理工具", page_icon="🧹", layout="centered")
    apply_custom_style()
    
    if "key" not in st.session_state:
        st.session_state.key = 0
    
    st.title("🧹 Word DOCX 清理工具")
    st.markdown("清理 DOCX 文件中的页眉和页脚元素")
    st.markdown("---")
    
    # 清理选项
    st.subheader("🔧 清理选项")
    col1, col2 = st.columns(2)
    with col1:
        remove_headers = st.checkbox("✂️ 去除页眉", value=True)
    with col2:
        remove_footers = st.checkbox("✂️ 去除页脚", value=True)
    
    st.markdown("---")
    
    uploaded_files = st.file_uploader(
        "选择DOCX文件进行清理（可多选）",
        type=['docx'],
        accept_multiple_files=True,
        help="支持单个或多个 .docx 文件上传，将清理页眉和页脚元素",
        key=f"uploader_{st.session_state.key}"
    )
    
    if uploaded_files:
        file_count = len(uploaded_files)
        st.info(f"📄 已选择 {file_count} 个DOCX文件")
        
        # 检查是否选择了任何清理选项
        if not (remove_headers or remove_footers):
            st.warning("⚠️ 请至少选择一个清理选项")
        else:
            if st.button("🧹 开始清理", type="primary", use_container_width=True):
                status_placeholder = st.empty()
                status_placeholder.info("🧹 正在清理中...")
                
                # 直接处理文件，不需要额外的函数抽象
                zip_buffer = io.BytesIO()
                results = []
                
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for uploaded_file in uploaded_files:
                        try:
                            # 直接用python-docx处理，无需复杂的解压重打包
                            from docx import Document
                            
                            # 从上传文件创建Document对象
                            doc = Document(io.BytesIO(uploaded_file.getvalue()))
                            
                            # 清理页眉页脚
                            for section in doc.sections:
                                if remove_headers:
                                    section.header.is_linked_to_previous = True
                                if remove_footers:
                                    section.footer.is_linked_to_previous = True
                            
                            # 保存到内存
                            cleaned_buffer = io.BytesIO()
                            doc.save(cleaned_buffer)
                            cleaned_content = cleaned_buffer.getvalue()
                            
                            # 添加到zip
                            clean_filename = f"{Path(uploaded_file.name).stem}_cleaned.docx"
                            zipf.writestr(clean_filename, cleaned_content)
                            results.append([uploaded_file.name, '✅ 清理成功'])
                            
                        except Exception as e:
                            results.append([uploaded_file.name, f'❌ {str(e)[:50]}'])
                
                st.session_state.result = (zip_buffer, results)
                status_placeholder.empty()
        
        # 显示结果
        if st.session_state.get('result'):
            zip_buffer, results = st.session_state.result
            success_count = sum(1 for r in results if r[1].startswith('✅'))
            
            st.success("✅ 清理完成!")
            st.dataframe(pd.DataFrame(results, columns=['文件名', '状态']), use_container_width=True, hide_index=True)
            
            col1, col2 = st.columns(2)
            col1.metric("清理成功", success_count)
            col2.metric("清理失败", len(results) - success_count)
            
            if success_count > 0:
                timestamp = datetime.now().strftime("%Y%m%d%H%M")
                filename = f"docx_cleaned_{timestamp}.zip" if file_count > 1 else f"{Path(uploaded_files[0].name).stem}_cleaned_{timestamp}.zip"
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.download_button("📥 下载清理文件", zip_buffer.getvalue(), filename, "application/zip", type="primary", use_container_width=True)
                with col2:
                    if st.button("🔄 重置页面", type="secondary", use_container_width=True):
                        st.session_state.key += 1
                        del st.session_state.result
                        st.rerun()

if __name__ == "__main__":
    main()