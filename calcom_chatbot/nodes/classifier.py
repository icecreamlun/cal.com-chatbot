from langchain_openai import ChatOpenAI
from calcom_chatbot.state import AgentState
from calcom_chatbot.prompts.templates import INTENT_CLASSIFICATION_PROMPT
from calcom_chatbot.utils.config import get_openai_api_key


def classifier_node(state: AgentState) -> AgentState:
    """Classify user intent."""
    user_query = state["user_query"]
    messages = state.get("messages", [])
    
    llm = ChatOpenAI(
        api_key=get_openai_api_key(),
        model="gpt-4",
        temperature=0
    )
    
    # Build conversation history for context
    conversation_history = "\n".join(messages[-3:]) if messages else "No previous conversation"
    
    # Use conversation history to better classify intent
    prompt = INTENT_CLASSIFICATION_PROMPT.format(
        user_query=user_query,
        conversation_history=conversation_history
    )
    response = llm.invoke(prompt)
    intent = response.content.strip().lower()
    
    # Validate intent
    if intent not in ["book_meeting", "list_events", "cancel_meeting", "general"]:
        intent = "general"
    
    state["intent"] = intent
    return state

