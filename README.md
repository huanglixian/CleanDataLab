# 数据预处理工具集

## 运行方式
```bash
streamlit run 首页.py
```

## 现有功能
- **Excel表头清洗** - 删除标题，处理多行表头
- **Excel主体清洗** - 提取表格主体信息  
- **Excel合并填充** - 取消合并单元格并填充

## 技术栈
- **Streamlit** 多页应用框架
- **common/ui_style.py** 统一样式库

## 添加新功能

1. 在`pages/`目录创建新文件，格式：`序号_名称.py`
2. **必须导入统一样式**：`from common.ui_style import apply_custom_style`

**模板代码**:
```python
import streamlit as st
from common.ui_style import apply_custom_style

st.set_page_config(page_title="功能名称", layout="centered")
apply_custom_style()  # 必须调用，统一样式

st.title("🔧 功能名称")
# 具体功能代码...
```

**开发要求**：代码尽量简洁，功能直接有效