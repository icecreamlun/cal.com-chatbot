from langchain_openai import ChatOpenAI
from calcom_chatbot.state import AgentState
from calcom_chatbot.tools.cal_api import list_bookings, reschedule_booking
from calcom_chatbot.utils.config import get_openai_api_key, get_calcom_user_email
from calcom_chatbot.prompts.templates import RESCHEDULE_MEETING_PROMPT
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
    
    try:
        # Get all upcoming bookings
        user_email = get_calcom_user_email()
        bookings = await list_bookings(user_email)
        
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
        
        bookings_text = "\n".join(bookings_info) if bookings else "No upcoming bookings"
        
        # Let LLM handle all user interaction
        prompt = RESCHEDULE_MEETING_PROMPT.format(
            conversation_history=conversation_history,
            user_query=user_query,
            bookings_text=bookings_text,
            current_time=datetime.now(timezone.utc).isoformat()
        )

        response = llm.invoke(prompt)
        response_text = response.content.strip()
        
        # Only check if ready to reschedule, otherwise return LLM's message
        if response_text.startswith("RESCHEDULE_READY:"):
            # Extract booking UID, new time, and reason
            uid_match = re.search(r'booking_uid=([a-zA-Z0-9]+)', response_text)
            time_match = re.search(r'new_time=([0-9T:\-Z]+)', response_text)
            reason_match = re.search(r'reason=(.+?)(?:,|$)', response_text, re.DOTALL)
            
            if uid_match and time_match:
                booking_uid = uid_match.group(1)
                new_start_time = time_match.group(1)
                reason = reason_match.group(1).strip() if reason_match else None
                
                # Execute rescheduling
                try:
                    result = await reschedule_booking(booking_uid, new_start_time, reason)
                    
                    # Get booking details for success message
                    booking_to_reschedule = next((b for b in bookings if b.get("uid") == booking_uid), None)
                    if booking_to_reschedule:
                        title = booking_to_reschedule.get("title", "Meeting")
                        old_start = booking_to_reschedule.get("start", "")
                        state["final_response"] = f"✅ Successfully rescheduled: {title}\nFrom: {old_start}\nTo: {new_start_time}"
                        if reason:
                            state["final_response"] += f"\nReason: {reason}"
                    else:
                        state["final_response"] = f"✅ Successfully rescheduled to {new_start_time}"
                    
                    state["api_response"] = result
                    
                except Exception as e:
                    state["final_response"] = f"❌ Failed to reschedule: {str(e)}"
            else:
                # Parsing failed, let LLM handle it
                state["final_response"] = response_text
        else:
            # LLM is handling user interaction (asking for info, clarifying, etc.)
            state["final_response"] = response_text
        
    except Exception as e:
        state["final_response"] = f"Error: {str(e)}"
    
    return state

