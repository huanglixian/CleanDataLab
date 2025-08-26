import streamlit as st
import pandas as pd
import io
from pathlib import Path
from common.ui_style import apply_custom_style

def fill_merged_cells(df):
    """
    智能表头合并处理：处理两行表头的合并单元格
    """
    if len(df) < 2:
        return df
    
    # 1. 提取并处理表头
    header1 = df.iloc[0].ffill()  # 第一行表头向右填充
    header2 = df.iloc[1].ffill()  # 第二行表头向右填充
    
    # 2. 生成新表头：组合两层表头
    new_headers = []
    for i in range(len(header1)):
        h1 = str(header1.iloc[i]) if pd.notna(header1.iloc[i]) else ""
        h2 = str(header2.iloc[i]) if pd.notna(header2.iloc[i]) else ""
        
        # 如果两行表头相同或第二行为空，只用第一行
        if h1 == h2 or h2 == "":
            new_headers.append(h1)
        else:
            # 否则组合：第一行-第二行
            new_headers.append(f"{h1}-{h2}")
    
    # 3. 提取数据区域（第3行开始），不做填充处理
    data_df = df.iloc[2:].copy() if len(df) > 2 else pd.DataFrame()
    
    # 4. 重建DataFrame：新表头 + 数据
    if not data_df.empty:
        data_df.columns = new_headers[:len(data_df.columns)]
        return data_df
    else:
        # 只有表头的情况
        result_df = pd.DataFrame(columns=new_headers)
        return result_df

def main():
    st.set_page_config(
        page_title="Excel 合并单元格填充工具",
        page_icon="📊",
        layout="centered"
    )
    
    # 应用通用样式
    apply_custom_style()
    
    st.title("📊 Excel 合并单元格填充工具")
    st.markdown("上传Excel文件，自动取消合并单元格并填充值")
    
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
            if st.button("🔄 开始处理", type="primary"):
                with st.spinner("正在处理中..."):
                    # 填充合并单元格
                    filled_df = fill_merged_cells(df)
                    
                    st.success("✅ 处理完成！")
                    
                    # 显示处理后的数据
                    st.subheader("处理后数据预览")
                    st.dataframe(filled_df.head(10), use_container_width=True)
                    
                    # 生成输出文件名
                    original_name = Path(uploaded_file.name).stem
                    output_filename = f"{original_name}_fill.xlsx"
                    
                    # 转换为Excel字节流
                    buffer = io.BytesIO()
                    filled_df.to_excel(buffer, index=False)
                    buffer.seek(0)
                    
                    # 下载按钮
                    st.download_button(
                        label="💾 下载处理后文件",
                        data=buffer,
                        file_name=output_filename,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                    
                    # 显示统计信息
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("处理前空值数量", df.isnull().sum().sum())
                    with col2:
                        st.metric("处理后空值数量", filled_df.isnull().sum().sum())
                        
        except Exception as e:
            st.error(f"❌ 文件处理出错: {str(e)}")
            st.info("请确保上传的是有效的Excel文件")

if __name__ == "__main__":
    main()