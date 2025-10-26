from langgraph.graph import StateGraph
from langgraph.constants import START, END
from calcom_chatbot.state import AgentState
from calcom_chatbot.nodes.classifier import classifier_node
from calcom_chatbot.nodes.book_meeting import book_meeting_node
from calcom_chatbot.nodes.list_events import list_events_node
from calcom_chatbot.nodes.cancel_meeting import cancel_meeting_node
from calcom_chatbot.nodes.response import response_node


def route_by_intent(state: AgentState) -> str:
    """Route to appropriate node based on intent."""
    intent = state.get("intent", "general")
    
    if intent == "book_meeting":
        return "book_meeting"
    elif intent == "list_events":
        return "list_events"
    elif intent == "cancel_meeting":
        return "cancel_meeting"
    else:
        return "response"


graph = StateGraph(AgentState)

graph.add_node("classifier", classifier_node)
graph.add_node("book_meeting", book_meeting_node)
graph.add_node("list_events", list_events_node)
graph.add_node("cancel_meeting", cancel_meeting_node)
graph.add_node("response", response_node)

graph.add_edge(START, "classifier")
graph.add_conditional_edges("classifier", route_by_intent, {
    "book_meeting": "book_meeting",
    "list_events": "list_events",
    "cancel_meeting": "cancel_meeting",
    "response": "response"
})
graph.add_edge("book_meeting", "response")
graph.add_edge("list_events", "response")
graph.add_edge("cancel_meeting", "response")
graph.add_edge("response", END)

compiled_graph = graph.compile()

