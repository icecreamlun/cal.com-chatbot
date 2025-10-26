# Cal.com Chatbot Frontend

Beautiful, simple web UI for the Cal.com Chatbot using Chainlit.

## ✨ Features

- 🎨 Beautiful chat interface (Chainlit)
- 💬 Real-time messaging
- 🔄 Session management (automatic)
- 📱 Responsive design
- 🚀 Zero backend coupling

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd frontend
pip install -r requirements.txt
```

### 2. Configure Backend URL (Optional)

```bash
# Create .env file
echo "BACKEND_URL=http://localhost:8001" > .env
```

If you don't create `.env`, it defaults to `http://localhost:8001`.

### 3. Start Backend (if not running)

In another terminal:
```bash
cd ..
python -m calcom_chatbot.main
```

### 4. Start Frontend

```bash
chainlit run app.py -w
```

The `-w` flag enables auto-reload during development.

### 5. Open Browser

Navigate to: http://localhost:8000

## 📁 Project Structure

```
frontend/
├── app.py              # Main Chainlit application
├── .chainlit           # Chainlit configuration
├── chainlit.md         # Welcome page content
├── requirements.txt    # Frontend dependencies
└── README.md          # This file
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file:

```env
# Backend API URL (default: http://localhost:8001)
BACKEND_URL=http://localhost:8001

# Show intent in responses for debugging (default: false)
SHOW_INTENT=false
```

### Chainlit Settings

Edit `.chainlit` file to customize:
- App name and description
- Session timeout (default: 3600 seconds)
- UI features

## 💡 How It Works

### Session Management

1. **Frontend**: Generates unique `session_id` using UUID when chat starts
2. **Backend**: Uses `session_id` to maintain conversation context
3. **Persistent**: Session data stored in backend (1 hour TTL)

```python
# Frontend generates session_id
session_id = str(uuid.uuid4())

# Sends to backend with every message
{
  "message": "Book a meeting...",
  "session_id": session_id
}
```

### API Communication

```
Frontend (Chainlit) → HTTP POST → Backend (FastAPI)
                    ← JSON Response ←
```

**Request**:
```json
{
  "message": "Show me my events",
  "session_id": "abc-123-..."
}
```

**Response**:
```json
{
  "response": "Here are your scheduled events...",
  "intent": "list_events"
}
```

## 🎨 Customization

### Change Welcome Message

Edit `app.py`:

```python
@cl.on_chat_start
async def start():
    await cl.Message(
        content="Your custom welcome message"
    ).send()
```

### Modify UI Appearance

Edit `.chainlit`:

```toml
[UI]
name = "Your App Name"
description = "Your description"
```

### Add Custom Styling

Create `public/style.css` (Chainlit will automatically load it).

## 🧪 Testing

### Test with Backend

```bash
# Terminal 1: Start backend
python -m calcom_chatbot.main

# Terminal 2: Start frontend
cd frontend
chainlit run app.py
```

### Test Messages

Try these in the chat:
- "Show me my events"
- "Book a meeting tomorrow at 2pm with John, john@test.com"
- "Cancel my meeting with John"
- "Reschedule my meeting to next Monday"

## 🐛 Troubleshooting

### Frontend can't connect to backend

**Error**: `Error connecting to backend: Connection refused`

**Solution**: 
1. Check backend is running: `curl http://localhost:8001/`
2. Verify BACKEND_URL in `.env`
3. Check firewall settings

### Session not maintained

**Issue**: Bot doesn't remember previous messages

**Solution**: 
- Check browser console for errors
- Verify session_id is being sent
- Backend session might have expired (check backend logs)

### Port already in use

**Error**: `Address already in use`

**Solution**:
```bash
# Use different port
chainlit run app.py -p 8080
```

## 📊 Production Deployment

### Option 1: Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV BACKEND_URL=http://backend:8001

CMD ["chainlit", "run", "app.py", "-h", "0.0.0.0"]
```

### Option 2: Direct Deployment

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment
export BACKEND_URL=https://your-backend-url.com

# Run (production)
chainlit run app.py -h 0.0.0.0 -p 8000
```

## 🔒 Security Notes

- Frontend communicates with backend via HTTP API
- No sensitive data stored in frontend
- Session IDs are random UUIDs
- All authentication handled by backend

## 📝 Code Structure

### app.py (50 lines)

Simple and clean:
1. **Imports**: Standard libraries + Chainlit + httpx
2. **Config**: Backend URL from environment
3. **on_chat_start**: Initialize session, show welcome
4. **on_message**: Send to backend, display response
5. **on_chat_end**: Cleanup (optional)

No complex state management, no unnecessary abstractions.

## 🎉 That's It!

This frontend is intentionally minimal:
- ✅ Single file (`app.py`)
- ✅ ~70 lines of code
- ✅ Zero backend coupling
- ✅ Beautiful UI out of the box
- ✅ Session management automatic

Just install, configure, and run!

