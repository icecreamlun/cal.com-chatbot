# Quick Setup Guide

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Configure Environment

1. Copy the example environment file:
```bash
cp env.example .env
```

2. Edit `.env` and add your credentials:
   - `OPENAI_API_KEY`: Use the key from requirements.md
   - `CALCOM_API_KEY`: Get from https://app.cal.com/settings/developer/api-keys
   - `CALCOM_USER_EMAIL`: Your Cal.com account email
   - `CALCOM_EVENT_TYPE_ID`: Get from your event types page
   - `CALCOM_API_BASE_URL`: Keep as https://api.cal.com/v2

## Step 3: Run the Server

```bash
python -m calcom_chatbot.main
```

The server will start at `http://localhost:8001`

## Step 4: Test the API

### Test 1: Health Check
```bash
curl http://localhost:8001/
```

Expected response:
```json
{
  "status": "ok",
  "message": "Cal.com Chatbot API is running"
}
```

### Test 2: Book a Meeting
```bash
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I want to book a meeting for 2024-12-01 at 14:00. My name is John Doe and email is john@example.com",
    "session_id": "test123"
  }'
```

### Test 3: List Events
```bash
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Show me my scheduled events",
    "session_id": "test123"
  }'
```

### Test 4: General Question
```bash
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What can you help me with?",
    "session_id": "test123"
  }'
```

## Troubleshooting

### Issue: Module not found
Make sure you're running from the project root directory and using `python -m calcom_chatbot.main`

### Issue: API key errors
Verify all environment variables are set correctly in `.env` file

### Issue: Cal.com API errors
- Ensure your Cal.com API key has proper permissions
- Verify the event type ID exists in your account
- Check that the API base URL is correct

## Project Structure

```
calcom_chatbot/
├── main.py              # FastAPI server (run with: python -m calcom_chatbot.main)
├── state.py             # Agent state definition
├── graph.py             # LangGraph flow (minimal, clean)
├── nodes/               # Individual processing nodes
│   ├── classifier.py    # Intent classification
│   ├── book_meeting.py  # Booking logic
│   ├── list_events.py   # List events logic
│   └── response.py      # Response formatting
├── tools/               # External integrations
│   ├── cal_api.py       # Cal.com API wrapper
│   └── openai_tools.py  # OpenAI function schemas
├── prompts/             # LLM prompts
│   └── templates.py     # Prompt templates
└── utils/               # Utilities
    └── config.py        # Environment config
```

## Flow Diagram

```
User Message → Classifier Node → Route by Intent
                                      ↓
                ┌─────────────────────┼─────────────────────┐
                ↓                     ↓                     ↓
        Book Meeting Node      List Events Node      Response Node
                ↓                     ↓                     
        Response Node          Response Node              
                ↓                     ↓                     ↓
                └─────────────────────┴─────────────────────┘
                                      ↓
                              Final Response
```

