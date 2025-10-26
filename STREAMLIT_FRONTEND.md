# 🎨 Streamlit前端（更稳定）

## ⚠️ 切换原因

Chainlit 1.0.x版本有pydantic兼容性bug，切换到**Streamlit**：
- ✅ 更稳定（成熟框架）
- ✅ 代码简洁（~100行）
- ✅ 无依赖冲突
- ✅ 美观的聊天界面

---

## 🚀 立即启动

### 方法1: 使用启动脚本

```bash
# 在项目根目录
./run_streamlit.sh
```

### 方法2: 手动启动

```bash
# 1. 进入frontend目录
cd frontend

# 2. 激活虚拟环境
source frontend_venv/bin/activate

# 3. 安装streamlit（如果还没安装）
pip install streamlit==1.29.0

# 4. 启动
streamlit run streamlit_app.py
```

---

## 📁 文件说明

```
frontend/
├── streamlit_app.py    # Streamlit应用（~100行，新）
├── app.py             # Chainlit应用（保留，可删除）
├── requirements.txt    # 已更新为streamlit
└── frontend_venv/      # 虚拟环境
```

---

## 🎨 Streamlit界面

### 特点

- ✅ 干净的聊天界面
- ✅ 侧边栏显示功能
- ✅ Session管理（UUID）
- ✅ 实时响应
- ✅ 完全解耦

### 界面布局

```
┌────────────────────────────────────────────────────┐
│ 📅 Cal.com Chatbot                          [设置] │
├──────────────┬─────────────────────────────────────┤
│              │                                     │
│ 💡 What I    │  Chat Messages:                     │
│    can do    │                                     │
│              │  👤 You:                            │
│ 📅 Book      │  show my events                     │
│    meetings  │                                     │
│              │  🤖 Bot:                            │
│ 📋 View      │  Here are your scheduled events:   │
│    events    │  1. Meeting with John...           │
│              │                                     │
│ ❌ Cancel    │  👤 You:                            │
│    meetings  │  cancel the first one               │
│              │                                     │
│ 🔄 Reschedule│  🤖 Bot:                            │
│    meetings  │  To cancel it, please provide...   │
│              │                                     │
│ 🔄 New       │                                     │
│    Session   ├─────────────────────────────────────┤
│              │  Type your message...        [Send] │
└──────────────┴─────────────────────────────────────┘
```

---

## 💡 代码对比

### Streamlit (~100行)

```python
import streamlit as st
import httpx
import uuid

# Initialize session
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Type your message..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Get bot response
    response = httpx.post(
        f"{BACKEND_URL}/chat",
        json={"message": prompt, "session_id": st.session_state.session_id}
    )
    bot_response = response.json()["response"]
    
    # Add bot message
    st.session_state.messages.append({"role": "assistant", "content": bot_response})
    st.rerun()
```

**优势**：
- ✅ 稳定（无兼容性问题）
- ✅ 简洁（核心代码~30行）
- ✅ 功能完整（聊天UI + session管理）

---

## 🧪 测试

### 1. 确保后端运行

```bash
# 新终端
python -m calcom_chatbot.main
```

### 2. 启动前端

```bash
# 新终端
./run_streamlit.sh
```

### 3. 打开浏览器

自动打开：http://localhost:8501

---

## 📊 Streamlit vs Chainlit

| 特性 | Streamlit | Chainlit |
|------|-----------|----------|
| **稳定性** | ⭐⭐⭐⭐⭐ | ⭐⭐（有bug） |
| **代码量** | ~100行 | ~70行 |
| **聊天UI** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **配置** | 简单 | 复杂（易出错） |
| **推荐** | ✅ 推荐 | ❌ 当前不推荐 |

---

## 🎯 特点

### Session管理

```python
# 自动生成UUID
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# 发送给后端
httpx.post("/chat", json={
    "message": prompt,
    "session_id": st.session_state.session_id
})
```

### 聊天历史

```python
# Streamlit自动管理
if "messages" not in st.session_state:
    st.session_state.messages = []

# 显示历史
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
```

### 新会话

侧边栏有"New Session"按钮：
- 清空历史
- 生成新session_id
- 重新开始对话

---

## ✅ 优势

1. **稳定** - 无版本兼容问题
2. **简洁** - 代码清晰易懂
3. **美观** - 内置聊天UI
4. **功能完整** - Session + 历史 + 重置

---

## 🚀 立即使用

```bash
# 一行命令
./run_streamlit.sh

# 访问
http://localhost:8501
```

**Streamlit更稳定，推荐使用！** 🎉

