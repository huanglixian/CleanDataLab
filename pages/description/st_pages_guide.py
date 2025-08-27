import streamlit as st
from common.ui_style import apply_custom_style

st.set_page_config(page_title="st-pages使用指南", layout="centered")
apply_custom_style()

st.title("st-pages 使用指南")
st.markdown("Streamlit页面导航配置说明")
st.markdown("---")

st.markdown("""
## 📦 安装依赖
```bash
pip install st-pages
```

## 📄 创建配置文件
在`.streamlit/pages.toml`中配置：
```toml
[[pages]]
name = "📊 Excel工具"
icon = "📊"
is_section = true

[[pages]]
name = "Excel-Sheet拆分"
icon = "📄"
path = "pages/Excel-Sheet拆分.py"

[[pages]]
name = "Excel标题与表头清洗"
icon = "🧹"
path = "pages/Excel标题与表头清洗.py"
```

## ⚙️ 应用配置

### 侧栏导航（默认）
```python
from st_pages import get_nav_from_toml

nav = get_nav_from_toml(".streamlit/pages.toml")
pg = st.navigation(nav)  # 默认侧栏位置
pg.run()
```

### 顶栏导航（TOML配置）
```python
from st_pages import get_nav_from_toml

nav = get_nav_from_toml(".streamlit/pages.toml")
pg = st.navigation(nav, position="top")  # 顶栏位置
pg.run()
```

### 顶栏导航（代码定义）

#### 平铺显示
```python
import streamlit as st

# 直接在app中定义页面
home = st.Page("pages/首页.py", title="首页", icon="🏠", default=True)
page1 = st.Page("pages/Excel-Sheet拆分.py", title="Excel拆分", icon="📄")
page2 = st.Page("pages/Excel标题与表头清洗.py", title="Excel清洗", icon="🧹")

# 平级顶栏导航
pg = st.navigation([home, page1, page2], position="top")
pg.run()
```

#### 分组显示
```python
import streamlit as st

# 定义页面
home = st.Page("pages/首页.py", title="首页", icon="🏠", default=True)
page1 = st.Page("pages/Excel-Sheet拆分.py", title="Excel拆分", icon="📄")
page2 = st.Page("pages/Excel标题与表头清洗.py", title="Excel清洗", icon="🧹")

# 分组顶栏导航
pg = st.navigation({
    "主页": [home],
    "📊 Excel工具": [page1, page2]
}, position="top")
pg.run()
```

## 📊 配置方式对比

| 配置方式 | 优点 | 缺点 | 适用场景 |
|----------|------|------|----------|
| TOML配置 | 配置驱动，易维护 | 需要文件管理 | 页面较多，结构稳定 |
| 代码定义-平铺 | 简单直观 | 代码较长 | 页面较少，扁平结构 |
| 代码定义-分组 | 灵活控制 | 代码复杂 | 需要动态分组逻辑 |

## 🎯 核心差异
- **侧栏**：`st.navigation(nav)`
- **顶栏**：`st.navigation(nav, position="top")`  
- **平铺**：`st.navigation([页面列表], position="top")`
- **分组**：`st.navigation({"分组": [页面]}, position="top")`

## 💡 使用建议
- 页面较多时建议使用TOML配置
- 需要动态控制时使用代码定义
- 图标使用emoji或Material Icons
- 分组名称简洁明了
- 保持导航结构层次清晰
""")