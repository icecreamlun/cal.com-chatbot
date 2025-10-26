from langchain_openai import ChatOpenAI
from calcom_chatbot.state import AgentState
from calcom_chatbot.prompts.templates import RESPONSE_FORMATTING_PROMPT
from calcom_chatbot.utils.config import get_openai_api_key


def response_node(state: AgentState) -> AgentState:
    """Format final response."""
    # If final_response is already set, return as is
    if state.get("final_response"):
        return state
    
    intent = state.get("intent", "general")
    api_response = state.get("api_response", {})
    user_query = state["user_query"]
    
    llm = ChatOpenAI(
        api_key=get_openai_api_key(),
        model="gpt-4",
        temperature=0.7
    )
    
    prompt = RESPONSE_FORMATTING_PROMPT.format(
        intent=intent,
        api_response=api_response,
        user_query=user_query
    )
    
    response = llm.invoke(prompt)
    state["final_response"] = response.content
    
    return state

