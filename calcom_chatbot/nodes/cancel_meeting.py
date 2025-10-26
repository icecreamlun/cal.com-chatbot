from langchain_openai import ChatOpenAI
from calcom_chatbot.state import AgentState
from calcom_chatbot.tools.cal_api import list_bookings, cancel_booking
from calcom_chatbot.utils.config import get_openai_api_key, get_calcom_user_email
from calcom_chatbot.prompts.templates import CANCEL_MEETING_PROMPT
from datetime import datetime, timezone
import re


async def cancel_meeting_node(state: AgentState) -> AgentState:
    """Handle canceling meeting flow."""
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
        prompt = CANCEL_MEETING_PROMPT.format(
            conversation_history=conversation_history,
            user_query=user_query,
            bookings_text=bookings_text,
            current_time=datetime.now(timezone.utc).isoformat()
        )

        response = llm.invoke(prompt)
        response_text = response.content.strip()
        
        # Only check if ready to cancel, otherwise return LLM's message
        if response_text.startswith("CANCEL_READY:"):
            # Extract booking UID and reason
            uid_match = re.search(r'booking_uid=([a-zA-Z0-9]+)', response_text)
            reason_match = re.search(r'reason=(.+?)(?:,|$)', response_text, re.DOTALL)
            
            if uid_match and reason_match:
                booking_uid = uid_match.group(1)
                reason = reason_match.group(1).strip()
                
                # Execute cancellation
                try:
                    result = await cancel_booking(booking_uid, reason)
                    
                    # Get booking details for success message
                    booking_to_cancel = next((b for b in bookings if b.get("uid") == booking_uid), None)
                    if booking_to_cancel:
                        title = booking_to_cancel.get("title", "Meeting")
                        start = booking_to_cancel.get("start", "")
                        state["final_response"] = f"✅ Successfully canceled: {title} scheduled for {start}\nReason: {reason}"
                    else:
                        state["final_response"] = f"✅ Successfully canceled the booking.\nReason: {reason}"
                    
                    state["api_response"] = result
                    
                except Exception as e:
                    state["final_response"] = f"❌ Failed to cancel: {str(e)}"
            else:
                # Parsing failed, let LLM handle it
                state["final_response"] = response_text
        else:
            # LLM is handling user interaction (asking for info, clarifying, etc.)
            state["final_response"] = response_text
        
    except Exception as e:
        state["final_response"] = f"Error: {str(e)}"
    
    return state

