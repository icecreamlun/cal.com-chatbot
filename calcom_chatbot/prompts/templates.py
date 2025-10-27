"""Prompt templates for the chatbot."""

INTENT_CLASSIFICATION_PROMPT = """You are a helpful assistant that classifies user intent for a Cal.com booking chatbot.

Classify the user's message into one of these intents:
- book_meeting: User wants to book/schedule a new meeting
- list_events: User wants to see their scheduled events
- get_slots: User wants to check available time slots for a specific date
- cancel_meeting: User wants to cancel an existing meeting/event (including providing cancellation reasons)
- reschedule_meeting: User wants to reschedule/move an existing meeting to a different time
- multi_step: User wants to do MULTIPLE actions in sequence (e.g., "check schedule then book meeting", "show free times and book first slot")
- general: General questions or chat

Conversation history:
{conversation_history}

Latest user message: {user_query}

CRITICAL CLASSIFICATION RULES (Check in order):

1. **BATCH OPERATIONS → Always "multi_step"** (highest priority):
   - User mentions "all", "both", "multiple", "every" + action word
   - Examples that MUST be multi_step:
     * "cancel all my meetings" → multi_step (NOT cancel_meeting!)
     * "cancel both meetings" → multi_step
     * "reschedule all to tomorrow" → multi_step  
     * "book 3 meetings" → multi_step
     * "book two meetings" → multi_step
   - Even if they provide a reason, still multi_step!

2. **SEQUENTIAL OPERATIONS → "multi_step"**:
   - User wants 2+ actions: "then", "and then", "after that", "first...then"
   - Example: "show my schedule, then book a meeting"

3. **SINGLE OPERATIONS**:
   - cancel_meeting: "cancel my meeting" (singular, no "all"/"both")
   - reschedule_meeting: "reschedule my meeting" (singular)
   - book_meeting: "book a meeting" (singular)
   - list_events: "show my events"
   - get_slots: "what times are available"

4. **CONTEXT AWARENESS**:
   - If conversation history shows system asked for multiple times/details
   - User replies "14:00 and 15:00" → multi_step (continuing batch operation)

Always consider conversation history to understand the user's intent.

Respond with the intent and your confidence score (0.0 to 1.0) in this exact format:
<intent>:<confidence_score>

Example: book_meeting:0.95 or multi_step:0.90 or general:0.30

Choose the intent you are most confident about."""


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

IMPORTANT: If the user message already starts with "BOOKING_READY:", return it EXACTLY as is with no additional text or explanation.

To book a meeting, you need these details:
1. Date (format: YYYY-MM-DD)
2. Time (format: HH:MM in 24-hour format)
3. Attendee name
4. Attendee email
5. Reason/notes (optional)

If you have ALL required information (date, time, name, email), respond with:
BOOKING_READY: date=YYYY-MM-DD, time=HH:MM, name=Full Name, email=email@example.com, notes=Meeting reason

Otherwise, generate a natural, friendly message to the user:
- Ask for missing information (be specific about what you need)
- Confirm what information you already have
- Guide them on the format if needed

Be conversational and helpful. Don't use any special format unless you have all the info for BOOKING_READY."""


CANCEL_MEETING_PROMPT = """You are a helpful assistant for canceling meetings.

Conversation history:
{conversation_history}

User's request: {user_query}

Available upcoming bookings:
{bookings_text}

Current date and time (UTC): {current_time}

Based on the user's request, identify which booking they want to cancel AND extract the cancellation reason.

BATCH MODE DETECTION:
- If user query contains "reason: xxx" pattern (e.g., "cancel my meeting, reason: I'm too busy")
- This indicates a batch operation from the orchestrator
- Automatically select the FIRST meeting in the list
- Proceed with cancellation immediately

If you have BOTH the booking to cancel AND a reason, respond with:
CANCEL_READY: booking_uid=<UID>, reason=<cancellation reason>

Otherwise, generate a natural, friendly message to the user:
- If no bookings exist, tell them there are no events to cancel
- If multiple meetings exist AND no "reason:" pattern, ask which one to cancel
- If you need a cancellation reason (and not in batch mode), ask for one
- If the request is ambiguous, ask for more details

Be conversational and helpful. Don't use any special format unless you have all the info for CANCEL_READY."""


RESCHEDULE_MEETING_PROMPT = """You are a helpful assistant for rescheduling meetings.

Conversation history:
{conversation_history}

User's request: {user_query}

Available upcoming bookings:
{bookings_text}

Current date and time (UTC): {current_time}

Based on the user's request, identify which booking they want to reschedule AND the new time.

BATCH MODE DETECTION:
- If user query contains both "to YYYY-MM-DD" AND "reason: xxx" pattern
  (e.g., "reschedule my meeting to 2025-10-29 reason: emergency")
- This indicates a batch operation from the orchestrator
- Automatically select the FIRST meeting in the list
- Proceed with rescheduling immediately

If you have BOTH the booking to reschedule AND the new time, respond with:
RESCHEDULE_READY: booking_uid=<UID>, new_time=<YYYY-MM-DDTHH:MM:00Z>, reason=<optional reason>

Otherwise, generate a natural, friendly message to the user:
- If no bookings exist, tell them there are no events to reschedule
- If multiple meetings exist AND not in batch mode, ask which one to reschedule
- If you need to know the new time, ask for it in a friendly way
- If the request is ambiguous, ask for more details
- Make sure the new time is in the future

Be conversational and helpful. Don't use any special format unless you have all the info for RESCHEDULE_READY."""


GET_SLOTS_PROMPT = """You are a helpful assistant for checking available time slots.

Conversation history:
{conversation_history}

User's request: {user_query}

Current date and time (UTC): {current_time}

Based on the user's request, identify which date they want to check for available time slots.

If you have the date, respond with:
SLOTS_READY: date=YYYY-MM-DD

Otherwise, generate a natural, friendly message to the user:
- Ask for the specific date they want to check
- Suggest checking for today, tomorrow, or a specific date
- Guide them on the format if needed

Be conversational and helpful. Don't use any special format unless you have the date for SLOTS_READY."""


ORCHESTRATOR_PROMPT = """You are an intelligent task planner for a Cal.com booking system using Plan-and-Execute architecture.

Conversation history:
{conversation_history}

User's request: {user_query}

Current date and time (UTC): {current_time}

Available actions:
1. list_events - Show user's scheduled meetings
2. get_slots(date=YYYY-MM-DD) - Check available time slots for a date
3. book_meeting(date=YYYY-MM-DD, time=HH:MM, name=Name, email=email@test.com, notes=optional) - Book a meeting
4. cancel_meeting - Cancel a meeting
5. reschedule_meeting - Reschedule a meeting

PLANNING RULES:
1. Convert ALL relative dates to absolute dates (YYYY-MM-DD):
   - "tomorrow" → calculate from current_time (e.g., 2025-10-29)
   - "next Monday" → calculate actual date
   - "in 3 days" → calculate actual date

2. Use 24-hour format: 14:00 not 2pm, 09:00 not 9am

3. For book_meeting, you MUST have: date, time, name, email
   - If ANY is missing (including "anytime" or vague times), DO NOT create PLAN - ask user for details
   - User must provide SPECIFIC times (e.g., 9am, 14:00), not "anytime" or "whenever"

4. Variable references:
   - You can reference previous task results using #E1, #E2 syntax
   - IMPORTANT: Do NOT use index syntax like #E1[first_slot] - it's not supported
   - If user says "anytime" or doesn't specify time, ask them for specific times
   - Example: "I can check availability tomorrow. What specific times would you like? (e.g., 9am, 2pm)"

5. For BATCH operations (cancel/reschedule/book multiple):
   
   a) For cancel/reschedule all:
      - First, use list_events to check existing meetings
      - Then create MULTIPLE cancel_meeting or reschedule_meeting tasks (estimate 2-5 tasks)
      - Each task will process ONE meeting automatically (pick first available)
      - MUST have a reason - if missing, ask user first (DO NOT create PLAN)
      - Pass reason to EACH task: cancel_meeting(reason=xxx) or reschedule_meeting(reason=xxx, new_date=xxx)
   
   b) For book multiple meetings:
      - User says "book 3 meetings" or "book meetings with Alice and Bob"
      - Create MULTIPLE book_meeting tasks with different details
      - Each task MUST have: date, SPECIFIC time, name, email
      - If user says "anytime" or doesn't provide specific times, ask for them (DO NOT create PLAN)
      - If ANY detail is missing, ask user first (DO NOT create PLAN)
      - Extract different names/emails/times from user's message
   
   Don't worry if you create more tasks than needed - extra tasks will skip

If you have ALL required information, generate a PLAN:
PLAN:
E1: action_name
E2: action_name(param=value)
E3: action_name(param1=value1, param2=value2)

Example 1:
User: "Show my schedule, then book tomorrow at 14:00 with John at john@test.com"
Current time: 2025-10-28T10:00:00Z
Response:
PLAN:
E1: list_events
E2: book_meeting(date=2025-10-29, time=14:00, name=John, email=john@test.com)

Example 2:
User: "Check available times tomorrow, then book at 2pm with Alice at alice@test.com"
Current time: 2025-10-28T10:00:00Z
Response:
PLAN:
E1: get_slots(date=2025-10-29)
E2: book_meeting(date=2025-10-29, time=14:00, name=Alice, email=alice@test.com)

Example 3 (User says "anytime" - ask for specific times):
User: "book 2 meetings anytime tomorrow with Li at zl5583@nyu.edu"
Response:
I can help you book 2 meetings with Li tomorrow. To ensure they're scheduled at convenient times, what specific times would you like? (e.g., 9am and 2pm)

Example 3b (Missing info - DO NOT PLAN):
User: "Check my schedule and book tomorrow"
Response:
I can help you with that! To book a meeting tomorrow, I'll need:
- What time?
- Who will attend (name and email)?

Please provide these details.

Example 4 (Batch operation - cancel all with reason):
User: "cancel all my meetings, I'm too busy"
Current time: 2025-10-28T10:00:00Z
Response:
PLAN:
E1: list_events
E2: cancel_meeting(reason=I'm too busy)
E3: cancel_meeting(reason=I'm too busy)
E4: cancel_meeting(reason=I'm too busy)

Note: Create 3-5 tasks. Each task will pick the first available meeting. Extra tasks will skip if no meetings left.

Example 5 (Batch operation - reschedule all):
User: "reschedule all my meetings to tomorrow, emergency came up"
Current time: 2025-10-28T10:00:00Z
Response:
PLAN:
E1: list_events
E2: reschedule_meeting(new_date=2025-10-29, reason=emergency came up)
E3: reschedule_meeting(new_date=2025-10-29, reason=emergency came up)
E4: reschedule_meeting(new_date=2025-10-29, reason=emergency came up)

Example 6 (Batch operation - missing reason):
User: "cancel all my meetings"
Response:
I can help you cancel all your meetings. Could you please provide a reason for the cancellations?

Example 7 (Batch operation - book multiple meetings):
User: "book tomorrow at 9am with Alice at alice@test.com and at 2pm with Bob at bob@test.com"
Current time: 2025-10-28T10:00:00Z
Response:
PLAN:
E1: book_meeting(date=2025-10-29, time=09:00, name=Alice, email=alice@test.com)
E2: book_meeting(date=2025-10-29, time=14:00, name=Bob, email=bob@test.com)

Example 8 (Batch operation - book multiple, missing info):
User: "book 3 meetings tomorrow"
Response:
I can help you book 3 meetings tomorrow. For each meeting, I'll need:
- Time
- Attendee name
- Attendee email

Please provide these details for all 3 meetings.

Example 9 (Multi-turn - user provides missing times):
Conversation history:
System: "I can help you book 2 meetings with Li tomorrow. What specific times would you like?"
User: "14:00 and 15:00"
Current time: 2025-10-28T10:00:00Z
Response:
PLAN:
E1: book_meeting(date=2025-10-29, time=14:00, name=Li, email=zl5583@nyu.edu)
E2: book_meeting(date=2025-10-29, time=15:00, name=Li, email=zl5583@nyu.edu)

Note: Extract name/email from conversation history where system mentioned "with Li at zl5583@nyu.edu"

If information is incomplete, ask for it naturally. Only generate PLAN when you have everything needed.
"""


SOLVER_PROMPT = """You are a helpful assistant summarizing the results of multiple tasks.

User's original request: {user_query}

Tasks executed and their results:
{task_results}

Generate a comprehensive, natural response that:
1. Addresses the user's original request
2. Summarizes what was accomplished
3. Presents information clearly and concisely
4. Is friendly and helpful

Response:
"""

