from langchain_openai import ChatOpenAI
from calcom_chatbot.state import AgentState
from calcom_chatbot.prompts.templates import INTENT_CLASSIFICATION_PROMPT
from calcom_chatbot.utils.config import get_openai_api_key
import logging

logger = logging.getLogger(__name__)


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
    response_text = response.content.strip().lower()
    
    # Parse intent and confidence score
    # Expected format: "intent:confidence_score" (e.g., "book_meeting:0.95")
    intent = "general"
    confidence = 0.0
    
    try:
        if ":" in response_text:
            parts = response_text.split(":")
            predicted_intent = parts[0].strip()
            confidence = float(parts[1].strip())
            
            # Validate intent
            valid_intents = ["book_meeting", "list_events", "get_slots", "cancel_meeting", "reschedule_meeting", "multi_step", "general"]
            if predicted_intent in valid_intents:
                # Check confidence threshold
                if confidence >= 0.6:
                    intent = predicted_intent
                else:
                    # Low confidence - default to general
                    intent = "general"
            else:
                intent = "general"
        else:
            # Fallback: old format without confidence
            if response_text in ["book_meeting", "list_events", "get_slots", "cancel_meeting", "reschedule_meeting", "multi_step", "general"]:
                intent = response_text
            else:
                intent = "general"
    except (ValueError, IndexError):
        # Parsing error - default to general
        intent = "general"
    
    # Store both intent and confidence in state
    state["intent"] = intent
    state["confidence"] = confidence
    
    # Log classification result
    logger.info(f"🎯 Classification: intent={intent}, confidence={confidence:.2f}, query='{user_query[:50]}...'")
    
    return state

