from langchain_openai import ChatOpenAI
from calcom_chatbot.state import AgentState
from calcom_chatbot.tools.cal_api import get_available_slots
from calcom_chatbot.utils.config import get_openai_api_key
from calcom_chatbot.prompts.templates import GET_SLOTS_PROMPT
from datetime import datetime, timezone
import re


async def get_slots_node(state: AgentState) -> AgentState:
    """Handle getting available time slots."""
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
    prompt = GET_SLOTS_PROMPT.format(
        conversation_history=conversation_history,
        user_query=user_query,
        current_time=datetime.now(timezone.utc).isoformat()
    )
    
    try:
        response = llm.invoke(prompt)
        response_text = response.content.strip()
        
        # Only check if ready to get slots, otherwise return LLM's message
        if response_text.startswith("SLOTS_READY:"):
            # Extract date
            date_match = re.search(r'date=(\d{4}-\d{2}-\d{2})', response_text)
            
            if date_match:
                date = date_match.group(1)
                
                # Execute API call
                try:
                    result = await get_available_slots(date)
                    
                    # Parse the slots response
                    # API returns: {"data": {"2024-08-13": [{"start": "...", "end": "..."}]}}
                    slots = result.get("data", {})
                    
                    if not slots or not any(slots.values()):
                        state["final_response"] = f"No available time slots found for {date}."
                    else:
                        # Format slots by date
                        slots_list = []
                        for date_key, time_slots in slots.items():
                            if time_slots:
                                slots_list.append(f"\n📅 {date_key}:")
                                for slot in time_slots:
                                    # With format=range, each slot has start and end
                                    start = slot.get("start", "N/A")
                                    end = slot.get("end", "N/A")
                                    # Format time nicely (show only HH:MM)
                                    if start != "N/A":
                                        start_time = start.split("T")[1][:5] if "T" in start else start
                                        end_time = end.split("T")[1][:5] if "T" in end else end
                                        slots_list.append(f"  • {start_time} - {end_time}")
                                    else:
                                        slots_list.append(f"  • {start}")
                        
                        if slots_list:
                            state["final_response"] = f"✅ Available time slots for {date}:" + "".join(slots_list)
                        else:
                            state["final_response"] = f"No available time slots found for {date}."
                    
                    state["api_response"] = result
                    
                except Exception as e:
                    state["final_response"] = f"❌ Failed to get slots: {str(e)}"
            else:
                # Parsing failed, let LLM handle it
                state["final_response"] = response_text
        else:
            # LLM is handling user interaction (asking for info, clarifying, etc.)
            state["final_response"] = response_text
        
    except Exception as e:
        state["final_response"] = f"Error: {str(e)}"
    
    return state

