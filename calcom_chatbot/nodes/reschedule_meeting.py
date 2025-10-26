from langchain_openai import ChatOpenAI
from calcom_chatbot.state import AgentState
from calcom_chatbot.tools.cal_api import list_bookings, reschedule_booking
from calcom_chatbot.utils.config import get_openai_api_key, get_calcom_user_email
from datetime import datetime, timezone, timedelta
import re


async def reschedule_meeting_node(state: AgentState) -> AgentState:
    """Handle rescheduling meeting flow."""
    user_query = state["user_query"]
    messages = state.get("messages", [])
    
    llm = ChatOpenAI(
        api_key=get_openai_api_key(),
        model="gpt-4",
        temperature=0
    )
    
    # Build conversation history
    conversation_history = "\n".join(messages[-5:]) if messages else ""
    
    # Get all upcoming bookings
    try:
        user_email = get_calcom_user_email()
        bookings = await list_bookings(user_email)
        
        if not bookings:
            state["final_response"] = "You don't have any upcoming events to reschedule."
            return state
        
        # Format bookings for LLM
        bookings_info = []
        for booking in bookings:
            booking_uid = booking.get("uid")
            title = booking.get("title", "Meeting")
            start = booking.get("start", "")
            attendees = booking.get("attendees", [])
            attendee_names = ", ".join([a.get("name", "Unknown") for a in attendees])
            
            bookings_info.append(
                f"UID: {booking_uid}, Title: {title}, Start: {start}, Attendees: {attendee_names}"
            )
        
        bookings_text = "\n".join(bookings_info)
        
        # Ask LLM to identify which booking to reschedule and extract new time
        prompt = f"""You are a helpful assistant for rescheduling meetings.

Conversation history:
{conversation_history}

User's request: {user_query}

Available upcoming bookings:
{bookings_text}

Current date and time (UTC): {datetime.now(timezone.utc).isoformat()}

Based on the user's request, identify which booking they want to reschedule AND the new time.

Consider:
- Original meeting references: "my meeting with John", "my 3pm meeting", "tomorrow's meeting"
- New time references: "to tomorrow", "to next Monday at 2pm", "move it to 10am"
- Relative times: "same time tomorrow", "one day later", "next week"

If you have BOTH the booking to reschedule AND the new time, respond with:
RESCHEDULE_READY: booking_uid=<UID>, new_time=<YYYY-MM-DDTHH:MM:00Z>, reason=<optional reason>

If you need more information, ask the user."""

        response = llm.invoke(prompt)
        response_text = response.content
        
        # Check if we have all info to reschedule
        if response_text.startswith("RESCHEDULE_READY:"):
            # Parse the rescheduling details
            reschedule_info = response_text.replace("RESCHEDULE_READY:", "").strip()
            
            # Extract booking UID, new time, and reason
            uid_match = re.search(r'booking_uid=([a-zA-Z0-9]+)', reschedule_info)
            time_match = re.search(r'new_time=([0-9T:\-Z]+)', reschedule_info)
            reason_match = re.search(r'reason=(.+?)$', reschedule_info)
            
            if uid_match and time_match:
                booking_uid = uid_match.group(1)
                new_start_time = time_match.group(1)
                reason = reason_match.group(1).strip() if reason_match else None
                
                # Find the booking
                booking_to_reschedule = next((b for b in bookings if b.get("uid") == booking_uid), None)
                
                if not booking_to_reschedule:
                    state["final_response"] = f"❌ Could not find booking with UID {booking_uid}."
                    return state
                
                # Validate new time is in the future
                try:
                    new_datetime = datetime.fromisoformat(new_start_time.replace('Z', '+00:00'))
                    current_time = datetime.now(timezone.utc)
                    
                    if new_datetime <= current_time:
                        state["final_response"] = "❌ The new time must be in the future. Please choose a future date and time."
                        return state
                except ValueError:
                    state["final_response"] = "❌ Invalid date or time format for the new time."
                    return state
                
                # Reschedule the booking
                try:
                    result = await reschedule_booking(booking_uid, new_start_time, reason)
                    
                    # Get booking details for confirmation
                    title = booking_to_reschedule.get("title", "Meeting")
                    old_start = booking_to_reschedule.get("start", "")
                    
                    state["api_response"] = result
                    state["final_response"] = f"✅ Successfully rescheduled: {title}\n\nFrom: {old_start}\nTo: {new_start_time}"
                    if reason:
                        state["final_response"] += f"\nReason: {reason}"
                    
                except Exception as e:
                    error_msg = str(e)
                    state["final_response"] = f"❌ Failed to reschedule the booking: {error_msg}"
            else:
                state["final_response"] = "I need both the meeting to reschedule and the new time. Please provide both."
        else:
            # LLM is asking for more information
            state["final_response"] = response_text
        
    except Exception as e:
        state["final_response"] = f"I encountered an error: {str(e)}. Please try again."
    
    return state

