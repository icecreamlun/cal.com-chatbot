"""Prompt templates for the chatbot."""

INTENT_CLASSIFICATION_PROMPT = """You are a helpful assistant that classifies user intent for a Cal.com booking chatbot.

Classify the user's message into one of these intents:
- book_meeting: User wants to book/schedule a new meeting
- list_events: User wants to see their scheduled events
- general: General questions or chat

User message: {user_query}

Respond with only one word: book_meeting, list_events, or general"""


EXTRACT_BOOKING_DETAILS_PROMPT = """You are a helpful assistant helping users book meetings.

Based on the conversation history and the user's latest message, extract the booking details.

Conversation history:
{conversation_history}

Latest message: {user_query}

If you have all the required information (date, time, attendee name, attendee email), extract them.
If information is missing, ask the user for the missing details in a friendly way.
"""


RESPONSE_FORMATTING_PROMPT = """You are a helpful Cal.com booking assistant.

Generate a natural, friendly response based on the following information:

Intent: {intent}
API Response: {api_response}
User Query: {user_query}

Provide a clear, concise response to the user."""


MISSING_INFO_PROMPT = """You are a helpful assistant helping users book meetings.

The user wants to book a meeting but hasn't provided all the required information.

Current booking details:
{booking_details}

Required information:
- Date (YYYY-MM-DD)
- Time (HH:MM)
- Attendee name
- Attendee email
- Reason (optional)

Generate a friendly message asking for the missing information."""

