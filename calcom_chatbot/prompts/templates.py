"""Prompt templates for the chatbot."""

INTENT_CLASSIFICATION_PROMPT = """You are a helpful assistant that classifies user intent for a Cal.com booking chatbot.

Classify the user's message into one of these intents:
- book_meeting: User wants to book/schedule a new meeting
- list_events: User wants to see their scheduled events
- cancel_meeting: User wants to cancel an existing meeting/event (including providing cancellation reasons)
- reschedule_meeting: User wants to reschedule/move an existing meeting to a different time
- general: General questions or chat

Conversation history:
{conversation_history}

Latest user message: {user_query}

IMPORTANT: 
- If the conversation is about canceling and the user is providing info, classify as "cancel_meeting"
- If the conversation is about rescheduling and the user is providing info, classify as "reschedule_meeting"
- Consider the context from conversation history to understand the user's intent
- Keywords for reschedule: "reschedule", "move", "change time", "postpone", "earlier", "later"

Respond with only one word: book_meeting, list_events, cancel_meeting, reschedule_meeting, or general"""


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


BOOK_MEETING_PROMPT = """You are a helpful booking assistant. 

Conversation history:
{conversation_history}

Latest user message: {user_query}

To book a meeting, you need these details:
1. Date (format: YYYY-MM-DD)
2. Time (format: HH:MM in 24-hour format)
3. Attendee name
4. Attendee email
5. Reason/notes (optional)

Analyze the conversation and user's latest message. If you have ALL required information (date, time, name, email), respond with:
BOOKING_READY: date=YYYY-MM-DD, time=HH:MM, name=Full Name, email=email@example.com, notes=Meeting reason

If any required information is missing, ask for it in a friendly way. List what specific information you still need."""


CANCEL_MEETING_PROMPT = """You are a helpful assistant for canceling meetings.

Conversation history:
{conversation_history}

User's request: {user_query}

Available upcoming bookings:
{bookings_text}

Current date and time (UTC): {current_time}

Based on the user's request, identify which booking they want to cancel AND extract the cancellation reason.

Consider:
- Time references like "3pm today", "tomorrow at 2pm", "next Monday"
- Partial matches like "cancel my meeting with John"
- Cancellation reasons like "I'm busy", "something came up", "need to reschedule"
- If the user doesn't provide a reason, ask for one (required for cancellation)
- If ambiguous which meeting, ask for clarification

If you have BOTH the booking to cancel AND a reason, respond with:
CANCEL_READY: booking_uid=<UID>, reason=<cancellation reason>

If you know which booking but need a reason, respond with:
NEED_REASON: booking_uid=<UID>

If you need clarification about which booking, ask the user."""


RESCHEDULE_MEETING_PROMPT = """You are a helpful assistant for rescheduling meetings.

Conversation history:
{conversation_history}

User's request: {user_query}

Available upcoming bookings:
{bookings_text}

Current date and time (UTC): {current_time}

Based on the user's request, identify which booking they want to reschedule AND the new time.

Consider:
- Original meeting references: "my meeting with John", "my 3pm meeting", "tomorrow's meeting"
- New time references: "to tomorrow", "to next Monday at 2pm", "move it to 10am"
- Relative times: "same time tomorrow", "one day later", "next week"

If you have BOTH the booking to reschedule AND the new time, respond with:
RESCHEDULE_READY: booking_uid=<UID>, new_time=<YYYY-MM-DDTHH:MM:00Z>, reason=<optional reason>

If you need more information, ask the user."""

