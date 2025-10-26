from calcom_chatbot.state import AgentState
from calcom_chatbot.tools.cal_api import list_bookings
from calcom_chatbot.utils.config import get_calcom_user_email


async def list_events_node(state: AgentState) -> AgentState:
    """Handle listing events."""
    # Note: user_email is not actually used in list_bookings anymore
    # We query all bookings for the authenticated user (host)
    user_email = get_calcom_user_email()
    
    try:
        # Get bookings asynchronously (queries all bookings where you are the host)
        bookings = await list_bookings(user_email)
        
        state["api_response"] = {"bookings": bookings}
        
        if not bookings:
            state["final_response"] = "You don't have any upcoming scheduled events."
        else:
            # Format bookings into a readable list
            events_list = []
            for idx, booking in enumerate(bookings, 1):
                start = booking.get("start", "N/A")
                title = booking.get("title", "Meeting")
                events_list.append(f"{idx}. {title} - {start}")
            
            state["final_response"] = "Here are your scheduled events:\n" + "\n".join(events_list)
    except Exception as e:
        state["final_response"] = f"I encountered an error while fetching your events: {str(e)}"
    
    return state

