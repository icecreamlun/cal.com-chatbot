from typing import TypedDict, Optional, List, Dict, Any


class AgentState(TypedDict):
    """State for the Cal.com chatbot agent."""
    messages: List[str]
    user_query: str
    intent: Optional[str]
    booking_details: Optional[Dict[str, Any]]
    api_response: Optional[Dict[str, Any]]
    final_response: str

