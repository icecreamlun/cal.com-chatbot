from langchain_openai import ChatOpenAI
from calcom_chatbot.state import AgentState
from calcom_chatbot.tools.cal_api import create_booking
from calcom_chatbot.utils.config import get_openai_api_key
from calcom_chatbot.prompts.templates import BOOK_MEETING_PROMPT
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
    
    # Let LLM handle all user interaction
    prompt = BOOK_MEETING_PROMPT.format(
        conversation_history=conversation_history,
        user_query=user_query
    )

    try:
        response = llm.invoke(prompt)
        response_text = response.content.strip()
        
        # Only check if ready to book, otherwise return LLM's message
        if response_text.startswith("BOOKING_READY:"):
            # Extract booking details
            date_match = re.search(r'date=(\d{4}-\d{2}-\d{2})', response_text)
            time_match = re.search(r'time=(\d{2}:\d{2})', response_text)
            name_match = re.search(r'name=([^,]+)', response_text)
            email_match = re.search(r'email=([^\s,]+)', response_text)
            notes_match = re.search(r'notes=(.+?)(?:,|$)', response_text, re.DOTALL)
            
            if all([date_match, time_match, name_match, email_match]):
                date = date_match.group(1)
                time = time_match.group(1)
                name = name_match.group(1).strip()
                email = email_match.group(1).strip()
                notes = notes_match.group(1).strip() if notes_match else ""
                
                # Execute booking
                start_time = f"{date}T{time}:00Z"
                result = await create_booking(
                    start_time=start_time,
                    attendee_email=email,
                    attendee_name=name,
                    notes=notes
                )
                
                state["api_response"] = result
                state["final_response"] = f"✅ Successfully booked your meeting for {date} at {time}. Confirmation sent to {email}."
            else:
                # Parsing failed, let LLM handle it
                state["final_response"] = response_text
        else:
            # LLM is handling user interaction (asking for info, clarifying, etc.)
            state["final_response"] = response_text
        
    except Exception as e:
        error_msg = str(e)
        if "past" in error_msg.lower():
            state["final_response"] = f"❌ Cannot book in the past. Please choose a future date and time."
        elif "already has booking" in error_msg.lower() or "not available" in error_msg.lower():
            state["final_response"] = f"❌ Time slot not available. Try a different time or date."
        else:
            state["final_response"] = f"❌ Booking failed: {error_msg}"
    
    return state

