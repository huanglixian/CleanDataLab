import streamlit as st
from common.ui_style import apply_custom_style

st.set_page_config(page_title="开发指南", layout="centered")
apply_custom_style()

st.title("开发指南")
st.markdown("项目开发和扩展说明")
st.markdown("---")

st.markdown("""

## 🛠️ 技术栈
- **Streamlit** 多页应用框架
- **common/ui_style.py** 统一样式库
- **st-pages** 页面导航管理

## ➕ 添加新功能

### 1. 创建页面文件
在`pages/`对应的目录创建新文件，格式：`功能名称.py`（英文命名）

### 2. 配置页面导航！！！
在`.streamlit/pages.toml`中添加页面配置

### 3. 导入统一样式
**必须导入统一样式**：`from common.ui_style import apply_custom_style`

### 4. 添加队列和交互优化
- **选择队列**：LibreOffice任务用 `lo_queue`，其他文件处理用 `fp_queue`
- **状态隔离**：每个工具使用独立前缀，如 `tool_prefix_key`、`tool_prefix_result`、`tool_prefix_task_running`
- **按钮防误点击**：转换按钮加 `disabled="tool_prefix_task_running" in st.session_state`，点击时设置状态并刷新
- **添加重置按钮**：下载区域添加重置按钮，清理 `tool_prefix_result` 和 `tool_prefix_task_running` 状态
- **文件上传器重置**：使用 `key=f"uploader_{st.session_state.tool_prefix_key}"` 实现重置
            
### 5. 对新应用增加说明
（1）**更新readme.md**：应用创建后，需要更新根目录下的`readme.md`文件，添加应用说明
（2）**补充依赖**：在`requirements.txt`中添加依赖

## 📝 页面模板
```python
import streamlit as st
from common.ui_style import apply_custom_style

def main():
    st.set_page_config(page_title="功能名称", layout="centered")
    apply_custom_style()
    
    # 初始化（使用工具独立前缀）
    if "tool_prefix_key" not in st.session_state:
        st.session_state.tool_prefix_key = 0
    
    st.title("功能名称")
    st.markdown("功能描述")
    st.markdown("---")
    
    # 文件上传器
    uploaded_files = st.file_uploader(
        "选择文件",
        key=f"uploader_{st.session_state.tool_prefix_key}"
    )
    
    # 转换按钮（防误点击）
    if st.button("开始转换", disabled="tool_prefix_task_running" in st.session_state):
        st.session_state.tool_prefix_task_running = True
        st.rerun()
    
    # 重置按钮
    if st.button("重置页面"):
        st.session_state.tool_prefix_key += 1
        st.session_state.pop('tool_prefix_result', None)
        st.session_state.pop('tool_prefix_task_running', None)
        st.rerun()

if __name__ == "__main__":
    main()
```

## 📋 TOML配置模板
```toml
# 新增分类
[[pages]]
name = "新分类"
icon = "🛠️"
is_section = true

# 新增页面
[[pages]]
name = "新功能"
icon = "⚡"
path = "pages/新功能.py"
```

## 📁 目录结构
```
DataSpace/
├── app.py                    # 主应用入口
├── requirements.txt          # 项目依赖
├── README.md                # 项目说明文档
├── .streamlit/              # Streamlit配置
│   ├── config.toml         # Streamlit配置
│   └── pages.toml          # 页面导航配置
├── common/                  # 公共模块
│   ├── __init__.py         # 包初始化文件
│   ├── ui_style.py         # 统一样式库
│   └── libreoffice_queue.py # LibreOffice队列系统
├── pages/                   # 应用页面
│   ├── description/         # 项目说明页面
│   │   ├── dev_guide.py    # 开发指南
│   │   ├── software_description.py # 软件说明
│   │   └── st_pages_guide.py # 页面导航说明
│   ├── excel_tools/         # Excel工具集
│   │   ├── xls_to_xlsx.py  # XLS格式转换
│   │   ├── excel_sheet_splitter.py # Sheet拆分
│   │   └── excel_title_cleaner.py # 标题清洗
│   └── word_tools/          # Word工具集
│       └── word_to_docx.py # DOC格式转换
```

## 🔧 开发建议
- 使用统一的色彩搭配（common/ui_style.py）
- 保持一致的交互模式（队列、按钮防误点击、重置按钮）
- 添加简洁且必要的注释
- 最后这一点是最重要的！！！在生成代码时，先保证简单清晰（KISS），不要提前做没必要的抽象（YAGNI）；只有在出现明显重复逻辑时，才考虑抽象成 公共方法（DRY）
""")            
