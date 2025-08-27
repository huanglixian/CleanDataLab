## 现有功能
- **Excel Sheet 拆分** - 批量拆分多Sheet文件，完整保留样式
- **Excel 标题表头清理** - 删除标题，处理多行表头，填充合并单元格

## 技术栈
- **Streamlit** 多页应用框架
- **common/ui_style.py** 统一样式库

## 添加新功能

1. 在`pages/`目录创建新文件，格式：`序号_名称.py`
2. 在`.streamlit/pages.toml`中配置分类和页面
3. **必须导入统一样式**：`from common.ui_style import apply_custom_style`

**页面模板**:
```python
import streamlit as st
from common.ui_style import apply_custom_style

st.set_page_config(page_title="功能名称", layout="centered")
apply_custom_style()

# 功能代码...
```

**配置分类**:
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
path = "pages/3_1.新功能.py"
```

## 项目运行方式
```bash
streamlit run app.py
```