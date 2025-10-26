# 🚀 开始使用 Cal.com Chatbot

## ⚡ 5秒快速启动

### 1. 启动后端

```bash
python -m calcom_chatbot.main
```

### 2. 启动前端（新终端）

```bash
./start_frontend.sh
```

### 3. 打开浏览器

```
http://localhost:8000
```

**就这么简单！** 🎉

---

## 📊 系统架构

```
浏览器 (http://localhost:8000)
    ↓
前端 Chainlit (美观Web UI)
    ↓
后端 FastAPI (智能处理)
    ↓
Cal.com API (会议管理)
```

---

## 💬 可以说什么？

### 查看会议
```
show my events
what meetings do I have?
```

### 预订会议
```
book a meeting tomorrow at 2pm with John Doe, john@example.com
schedule an appointment for Dec 20 at 3pm, Jane Smith, jane@test.com, reason: project discussion
```

### 取消会议（多轮对话）
```
You: cancel my meeting with John
Bot: To cancel it, please provide a reason
You: I have a conflict
Bot: ✅ Successfully canceled
```

### 重新安排
```
reschedule my meeting with John to tomorrow at 3pm
move my 3pm meeting to next Monday
```

---

## 🎯 特点

- ✅ **美观界面** - 专业聊天UI
- ✅ **自然语言** - 随意表达
- ✅ **多轮对话** - 保持上下文
- ✅ **完整功能** - 预订/查看/取消/重新安排
- ✅ **实时响应** - 即时反馈

---

## 📁 端口说明

| 服务 | 端口 | 访问方式 |
|------|------|----------|
| 前端 (Chainlit) | 8000 | 浏览器访问 |
| 后端 (FastAPI) | 8001 | API（前端调用） |

---

## 🔧 故障排查

### 后端没有运行

**错误**: "Error connecting to backend"

**解决**:
```bash
# 检查后端状态
curl http://localhost:8001/

# 如果没有响应，启动后端
python -m calcom_chatbot.main
```

### 端口被占用

**错误**: "Address already in use"

**解决**:
```bash
# 使用不同端口
cd frontend
source frontend_venv/bin/activate
chainlit run app.py -p 8080
```

### 依赖问题

**错误**: "ModuleNotFoundError: No module named 'chainlit'"

**解决**:
```bash
cd frontend
pip install -r requirements.txt
```

---

## 📚 更多信息

- **前端文档**: `frontend/README.md`
- **完整指南**: `FRONTEND_GUIDE.md`
- **项目文档**: `README.md`

---

## 🎉 That's It!

只需两个命令：
```bash
python -m calcom_chatbot.main    # 后端
./start_frontend.sh               # 前端
```

享受使用吧！ 🚀

