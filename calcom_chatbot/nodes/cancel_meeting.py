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
    
    # First, get all upcoming bookings
    try:
        user_email = get_calcom_user_email()
        bookings = await list_bookings(user_email)
        
        if not bookings:
            state["final_response"] = "You don't have any upcoming events to cancel."
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
        
        # Use prompt template
        prompt = CANCEL_MEETING_PROMPT.format(
            conversation_history=conversation_history,
            user_query=user_query,
            bookings_text=bookings_text,
            current_time=datetime.now(timezone.utc).isoformat()
        )

        response = llm.invoke(prompt)
        response_text = response.content
        
        # Check if we need a reason
        if response_text.startswith("NEED_REASON:"):
            # Parse to get the UID
            cancel_info = response_text.replace("NEED_REASON:", "").strip()
            uid_match = re.search(r'booking_uid=([a-zA-Z0-9]+)', cancel_info)
            
            if uid_match:
                booking_uid = uid_match.group(1)
                booking_to_cancel = next((b for b in bookings if b.get("uid") == booking_uid), None)
                
                if booking_to_cancel:
                    title = booking_to_cancel.get("title", "Meeting")
                    start = booking_to_cancel.get("start", "")
                    state["final_response"] = f"I found your meeting: {title} scheduled for {start}.\n\nTo cancel it, please provide a reason for the cancellation (e.g., 'I'm busy', 'something came up', etc.)"
                else:
                    state["final_response"] = "I couldn't find that booking. Please try again."
            else:
                state["final_response"] = "Please provide a reason for canceling the meeting."
        
        # Check if we have identified the booking to cancel with reason
        elif response_text.startswith("CANCEL_READY:"):
            # Parse the cancellation details
            cancel_info = response_text.replace("CANCEL_READY:", "").strip()
            
            # Extract booking UID and reason
            uid_match = re.search(r'booking_uid=([a-zA-Z0-9]+)', cancel_info)
            reason_match = re.search(r'reason=(.+?)$', cancel_info)
            
            if uid_match and reason_match:
                booking_uid = uid_match.group(1)
                reason = reason_match.group(1).strip()
                
                # Find the booking to get details for confirmation
                booking_to_cancel = next((b for b in bookings if b.get("uid") == booking_uid), None)
                
                if not booking_to_cancel:
                    state["final_response"] = f"❌ Could not find booking with UID {booking_uid}."
                    return state
                
                # Cancel the booking with reason
                try:
                    result = await cancel_booking(booking_uid, reason)
                    
                    # Get booking details for user-friendly message
                    title = booking_to_cancel.get("title", "Meeting")
                    start = booking_to_cancel.get("start", "")
                    
                    state["api_response"] = result
                    state["final_response"] = f"✅ Successfully canceled: {title} scheduled for {start}\nReason: {reason}"
                    
                except Exception as e:
                    error_msg = str(e)
                    # Check if it's a "reason required" error
                    if "reason is required" in error_msg.lower():
                        state["final_response"] = f"To cancel this meeting, please provide a reason for the cancellation."
                    else:
                        state["final_response"] = f"❌ Failed to cancel the booking: {error_msg}"
            else:
                # Missing reason
                if uid_match:
                    booking_uid = uid_match.group(1)
                    booking_to_cancel = next((b for b in bookings if b.get("uid") == booking_uid), None)
                    if booking_to_cancel:
                        title = booking_to_cancel.get("title", "Meeting")
                        state["final_response"] = f"To cancel '{title}', please provide a reason for the cancellation."
                    else:
                        state["final_response"] = "Please provide a reason for canceling the meeting."
                else:
                    state["final_response"] = "I couldn't identify which booking to cancel. Please be more specific."
        else:
            # LLM is asking for clarification
            state["final_response"] = response_text
        
    except Exception as e:
        state["final_response"] = f"I encountered an error: {str(e)}. Please try again."
    
    return state

