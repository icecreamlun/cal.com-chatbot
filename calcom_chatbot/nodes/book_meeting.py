from langchain_openai import ChatOpenAI
from calcom_chatbot.state import AgentState
from calcom_chatbot.tools.cal_api import create_booking
from calcom_chatbot.utils.config import get_openai_api_key
import re


async def book_meeting_node(state: AgentState) -> AgentState:
    """Handle booking meeting flow."""
    user_query = state["user_query"]
    messages = state.get("messages", [])
    
    llm = ChatOpenAI(
        api_key=get_openai_api_key(),
        model="gpt-4",
        temperature=0
    )
    
    # Build conversation history
    conversation_history = "\n".join(messages[-5:]) if messages else ""
    
    # Improved prompt for extracting booking details
    prompt = f"""You are a helpful booking assistant. 

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

    try:
        response = llm.invoke(prompt)
        response_text = response.content
        
        # Check if we have all information
        if response_text.startswith("BOOKING_READY:"):
            # Parse the booking details
            booking_info = response_text.replace("BOOKING_READY:", "").strip()
            
            # Extract details using regex
            date_match = re.search(r'date=(\d{4}-\d{2}-\d{2})', booking_info)
            time_match = re.search(r'time=(\d{2}:\d{2})', booking_info)
            name_match = re.search(r'name=([^,]+)', booking_info)
            email_match = re.search(r'email=([^\s,]+)', booking_info)
            notes_match = re.search(r'notes=(.+?)(?:,|$)', booking_info)
            
            if all([date_match, time_match, name_match, email_match]):
                date = date_match.group(1)
                time = time_match.group(1)
                name = name_match.group(1).strip()
                email = email_match.group(1).strip()
                notes = notes_match.group(1).strip() if notes_match else ""
                
                # Validate date is in the future
                from datetime import datetime, timezone
                try:
                    booking_datetime = datetime.fromisoformat(f"{date}T{time}:00")
                    current_time = datetime.now(timezone.utc).replace(tzinfo=None)
                    
                    if booking_datetime <= current_time:
                        state["final_response"] = f"❌ The date {date} at {time} is in the past. Please choose a future date and time."
                        return state
                except ValueError:
                    state["final_response"] = f"❌ Invalid date or time format. Please use YYYY-MM-DD for date and HH:MM for time."
                    return state
                
                # Create booking
                try:
                    start_time = f"{date}T{time}:00Z"
                    result = await create_booking(
                        start_time=start_time,
                        attendee_email=email,
                        attendee_name=name,
                        notes=notes
                    )
                    
                    state["api_response"] = result
                    state["final_response"] = f"✅ Great! I've successfully booked your meeting for {date} at {time}. A confirmation has been sent to {email}."
                except Exception as e:
                    error_msg = str(e)
                    
                    # 特殊处理各种错误类型
                    if "past" in error_msg.lower():
                        state["final_response"] = f"❌ Cannot book a meeting in the past. The date {date} at {time} has already passed. Please choose a future date and time."
                    elif "already has booking" in error_msg.lower() or "not available" in error_msg.lower():
                        state["final_response"] = f"❌ This time slot ({date} at {time}) is not available. Either you already have a booking at this time, or the host is not available.\n\n💡 Suggestions:\n- Try a different time on the same day\n- Choose another date\n- Use 'Show me my scheduled events' to see existing bookings"
                    else:
                        state["final_response"] = f"❌ I encountered an error while booking: {error_msg}\n\nPlease check:\n- The time slot is available\n- Your Cal.com configuration is correct"
            else:
                state["final_response"] = "I couldn't parse all the booking details. Please provide the date, time, your name, and email clearly."
        else:
            # LLM is asking for more information
            state["final_response"] = response_text
        
    except Exception as e:
        state["final_response"] = f"I encountered an error: {str(e)}. Please try again."
    
    return state

