## 现有功能
- **Excel Sheet 拆分** - 批量拆分多Sheet文件，完整保留样式
- **Excel 标题表头清理** - 删除标题，处理多行表头，填充合并单元格

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
# 具体功能代码...（**开发时，编码合理、结构和流程清晰，代码尽量简洁、精简**）
# 新功能开发完，要在上方“现有功能”新增条目和一句话说明
```

## 项目运行方式
```bash
streamlit run 首页.py
```