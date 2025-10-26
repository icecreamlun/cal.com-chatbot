# 🚀 启动Streamlit前端

## ✅ 切换到Streamlit

因为Chainlit有兼容性bug，改用**Streamlit**（更稳定）。

---

## 🚀 立即启动

### 最简单（一行命令）

```bash
./run_streamlit.sh
```

### 或手动启动

```bash
# 1. 进入frontend目录
cd frontend

# 2. 激活环境
source frontend_venv/bin/activate

# 3. 启动streamlit
streamlit run streamlit_app.py
```

**访问**: http://localhost:8501

---

## 📊 Streamlit界面

```
┌────────────────────────────────────────────────────┐
│ 📅 Cal.com Chatbot                          [⚙️]   │
│ Book, list, cancel, and reschedule meetings        │
├──────────────┬─────────────────────────────────────┤
│              │                                     │
│ 💡 What I    │  👤 You:                            │
│    can do    │  show my events                     │
│              │                                     │
│ 📅 Book      │  🤖 Assistant:                      │
│    meetings  │  Here are your scheduled events:   │
│              │  1. Meeting with John - 2025-12... │
│ 📋 View      │                                     │
│    events    │  👤 You:                            │
│              │  cancel the first one               │
│ ❌ Cancel    │                                     │
│    meetings  │  🤖 Assistant:                      │
│              │  To cancel it, please provide...   │
│ 🔄 Reschedule│                                     │
│    meetings  │                                     │
│              │                                     │
│ ─────────    │                                     │
│              ├─────────────────────────────────────┤
│ Session ID:  │  Type your message...        [Send] │
│ abc123...    │                                     │
│              │                                     │
│ 🔄 New       │                                     │
│    Session   │                                     │
└──────────────┴─────────────────────────────────────┘
```

---

## 💡 特点

### 1. 稳定
- ✅ 无版本冲突
- ✅ 成熟框架
- ✅ 久经考验

### 2. 简洁
- ✅ ~100行代码
- ✅ 清晰易懂
- ✅ 无过度工程化

### 3. 功能完整
- ✅ 聊天界面
- ✅ Session管理
- ✅ 新会话按钮
- ✅ 侧边栏信息

### 4. 美观
- ✅ 现代化设计
- ✅ 响应式布局
- ✅ 自定义样式

---

## 🎯 使用示例

### 启动后

1. 浏览器打开 http://localhost:8501
2. 看到欢迎界面和功能说明
3. 输入消息测试

### 测试对话

```
You: show my events
Bot: Here are your scheduled events: ...

You: cancel my meeting with John
Bot: To cancel it, please provide a reason

You: I have a conflict
Bot: ✅ Successfully canceled...
```

---

## 📁 文件

```
frontend/
├── streamlit_app.py    # Streamlit应用（新，推荐）✅
├── app.py             # Chainlit应用（有bug，弃用）
├── requirements.txt    # 已更新为streamlit
└── frontend_venv/      # 虚拟环境
```

---

## 🔧 启动脚本

**`run_streamlit.sh`** 会自动：
1. 检查后端
2. 进入frontend目录
3. 激活虚拟环境
4. 启动streamlit

---

## 📊 对比

| 框架 | 状态 | 代码量 | UI质量 |
|------|------|--------|--------|
| Chainlit | ❌ 有bug | ~70行 | ⭐⭐⭐⭐⭐ |
| **Streamlit** | ✅ 稳定 | ~100行 | ⭐⭐⭐⭐ |

**推荐使用Streamlit** ✅

---

## 🎉 立即测试

```bash
# 确保后端运行
python -m calcom_chatbot.main

# 启动streamlit前端（新终端）
./run_streamlit.sh
```

浏览器访问: **http://localhost:8501**

**稳定、简洁、美观！** 🚀

