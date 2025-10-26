import os
from dotenv import load_dotenv

load_dotenv()


def get_openai_api_key() -> str:
    """Get OpenAI API key from environment."""
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    return key


def get_calcom_api_key() -> str:
    """Get Cal.com API key from environment."""
    key = os.getenv("CALCOM_API_KEY")
    if not key:
        raise ValueError("CALCOM_API_KEY not found in environment variables")
    return key


def get_calcom_user_email() -> str:
    """Get Cal.com user email from environment."""
    email = os.getenv("CALCOM_USER_EMAIL")
    if not email:
        raise ValueError("CALCOM_USER_EMAIL not found in environment variables")
    return email


def get_calcom_event_type_id() -> int:
    """Get Cal.com event type ID from environment."""
    event_type_id = os.getenv("CALCOM_EVENT_TYPE_ID")
    if not event_type_id:
        raise ValueError("CALCOM_EVENT_TYPE_ID not found in environment variables")
    return int(event_type_id)


def get_calcom_base_url() -> str:
    """Get Cal.com API base URL from environment."""
    return os.getenv("CALCOM_API_BASE_URL", "https://api.cal.com/v2")


def setup_langsmith():
    """Setup LangSmith tracing if enabled."""
    if os.getenv("LANGSMITH_TRACING", "false").lower() == "true":
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_ENDPOINT"] = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
        os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGSMITH_API_KEY", "")
        os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGSMITH_PROJECT", "cal.com-chatbot")
        print(f"LangSmith tracing enabled for project: {os.environ['LANGCHAIN_PROJECT']}")
    else:
        print("LangSmith tracing disabled")

