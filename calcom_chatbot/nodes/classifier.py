from langchain_openai import ChatOpenAI
from calcom_chatbot.state import AgentState
from calcom_chatbot.prompts.templates import INTENT_CLASSIFICATION_PROMPT
from calcom_chatbot.utils.config import get_openai_api_key


def classifier_node(state: AgentState) -> AgentState:
    """Classify user intent."""
    user_query = state["user_query"]
    
    llm = ChatOpenAI(
        api_key=get_openai_api_key(),
        model="gpt-4",
        temperature=0
    )
    
    prompt = INTENT_CLASSIFICATION_PROMPT.format(user_query=user_query)
    response = llm.invoke(prompt)
    intent = response.content.strip().lower()
    
    # Validate intent
    if intent not in ["book_meeting", "list_events", "general"]:
        intent = "general"
    
    state["intent"] = intent
    return state

