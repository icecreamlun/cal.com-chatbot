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

