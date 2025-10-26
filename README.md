# Cal.com Chatbot Backend

A FastAPI-based chatbot backend using LangGraph and OpenAI function calling to interact with Cal.com API for booking meetings and listing events.

## Features

- **Book Meetings**: Interactive conversation to collect meeting details and book appointments
- **List Events**: Retrieve and display scheduled events
- **Cancel Meetings**: Cancel existing meetings using natural language (e.g., "cancel my event at 3pm today")
- **Reschedule Meetings**: Move meetings to different times (e.g., "reschedule my meeting to tomorrow at 2pm")
- **Session Management**: Maintain conversation context across multiple messages

## Project Structure

```
calcom_chatbot/
├── main.py              # FastAPI server entry point
├── state.py             # AgentState definition
├── graph.py             # LangGraph definition
├── nodes/               # LangGraph nodes
│   ├── classifier.py    # Intent classification
│   ├── book_meeting.py  # Booking flow handler
│   ├── list_events.py   # List events handler
│   ├── cancel_meeting.py # Cancel meeting handler
│   ├── reschedule_meeting.py # Reschedule meeting handler
│   └── response.py      # Response formatter
├── tools/               # External API integrations
│   ├── cal_api.py       # Cal.com API wrapper
│   └── openai_tools.py  # OpenAI function definitions
├── prompts/             # Prompt templates
│   └── templates.py
└── utils/               # Utilities
    └── config.py        # Environment config
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Required environment variables:

- `OPENAI_API_KEY`: Your OpenAI API key (provided in requirements document)
- `CALCOM_API_KEY`: Your Cal.com API key (get from https://app.cal.com/settings/developer/api-keys)
- `CALCOM_USER_EMAIL`: Your Cal.com account email
- `CALCOM_EVENT_TYPE_ID`: Your Cal.com event type ID
- `CALCOM_API_BASE_URL`: Cal.com API base URL (default: https://api.cal.com/v2)

### 3. Getting Cal.com Credentials

1. Create an account at https://cal.com
2. Go to Settings → Developer → API Keys
3. Create a new API key
4. Find your Event Type ID:
   - Go to Event Types
   - Click on an event type
   - The ID is in the URL: `/event-types/{EVENT_TYPE_ID}`

## Running the Server

Run the server using Python's module syntax:

```bash
python -m calcom_chatbot.main
```

The server will start on `http://localhost:8001`

## API Endpoints

### POST /chat

Send a message to the chatbot. Sessions auto-expire after 1 hour of inactivity.

**Request:**
```json
{
  "message": "Help me book a meeting",
  "session_id": "user123"
}
```

**Response:**
```json
{
  "response": "I'd be happy to help you book a meeting. Please provide the following details: date, time, your name, and your email.",
  "intent": "book_meeting"
}
```

### GET /

Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "message": "Cal.com Chatbot API is running"
}
```

### GET /sessions

List all active sessions with their status.

**Response:**
```json
{
  "active_sessions": 2,
  "sessions": [
    {
      "session_id": "user123",
      "message_count": 6,
      "last_access": "2024-10-26T10:30:00",
      "expires_in_seconds": 2400
    }
  ]
}
```

### GET /sessions/{session_id}

Get conversation history for a session (returns 404 if expired).

**Response:**
```json
{
  "session_id": "user123",
  "messages": [
    "User: Hello",
    "Assistant: Hi! How can I help you today?"
  ],
  "expires_in_seconds": 3600
}
```

### DELETE /sessions/{session_id}

Clear a session's conversation history.

**Response:**
```json
{
  "message": "Session cleared"
}
```

## Usage Examples

### 1. Book a Meeting

```bash
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I want to book a meeting for tomorrow at 2pm. My name is John Doe and email is john@example.com",
    "session_id": "user123"
  }'
```

### 2. List Events

```bash
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Show me my scheduled events",
    "session_id": "user123"
  }'
```

### 3. Cancel a Meeting

```bash
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "cancel my event at 3pm today",
    "session_id": "user123"
  }'
```

### 4. Reschedule a Meeting

```bash
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "reschedule my meeting with John to tomorrow at 2pm",
    "session_id": "user123"
  }'
```

### 5. General Questions

```bash
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What can you help me with?",
    "session_id": "user123"
  }'
```

## Architecture

The chatbot uses LangGraph to orchestrate a multi-node conversation flow:

1. **Classifier Node**: Determines user intent (book_meeting/list_events/cancel_meeting/reschedule_meeting/general)
2. **Routing**: Routes to appropriate handler based on intent
3. **Handler Nodes**:
   - Book Meeting: Extracts details using LLM, validates date/time, creates booking
   - List Events: Fetches user's scheduled events from Cal.com
   - Cancel Meeting: Finds matching booking using natural language, cancels it
   - Reschedule Meeting: Finds booking and updates to new time
4. **Response Node**: Formats the final response

## Development

### Code Style

- Simple, readable code
- Modular design with clear separation of concerns
- No self references (using `python -m` module execution)
- Minimal dependencies

### Future Enhancements

- Reschedule event functionality
- Query available time slots
- Web UI using Chainlit or Streamlit
- Persistent session storage (Redis/Database)
- Support for multiple event types
- Advanced timezone handling
- Batch operations (cancel multiple meetings)

## Troubleshooting

### Common Issues

1. **API Key Issues**: Ensure all environment variables are set correctly in `.env`
2. **Cal.com API Errors**: Verify your Cal.com API key has the required permissions
3. **Event Type ID**: Make sure the event type ID exists in your Cal.com account

### Logs

The application logs errors to stdout. Run with verbose logging if needed.

## License

MIT

