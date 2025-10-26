"""
Simple test client for the Cal.com Chatbot API.

Usage:
    python test_client.py
"""

import requests
import json
from typing import Dict, Any


class ChatbotClient:
    """Simple client for testing the chatbot API."""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.session_id = "test_session"
    
    def send_message(self, message: str) -> Dict[str, Any]:
        """Send a message to the chatbot."""
        url = f"{self.base_url}/chat"
        payload = {
            "message": message,
            "session_id": self.session_id
        }
        
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    
    def get_session_history(self) -> Dict[str, Any]:
        """Get the session conversation history."""
        url = f"{self.base_url}/sessions/{self.session_id}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    
    def clear_session(self) -> Dict[str, Any]:
        """Clear the session history."""
        url = f"{self.base_url}/sessions/{self.session_id}"
        response = requests.delete(url)
        response.raise_for_status()
        return response.json()


def print_response(response: Dict[str, Any]):
    """Pretty print the chatbot response."""
    print("\n" + "="*50)
    print(f"Intent: {response.get('intent', 'N/A')}")
    print("-"*50)
    print(f"Response: {response.get('response')}")
    print("="*50 + "\n")


def main():
    """Run interactive tests."""
    client = ChatbotClient()
    
    print("\n🤖 Cal.com Chatbot Test Client")
    print("="*50)
    
    # Test 1: General question
    print("\n📝 Test 1: General Question")
    response = client.send_message("What can you help me with?")
    print_response(response)
    
    # Test 2: List events
    print("\n📝 Test 2: List Events")
    response = client.send_message("Show me my scheduled events")
    print_response(response)
    
    # Test 3: Book a meeting (conversational)
    print("\n📝 Test 3: Book a Meeting (Conversational)")
    response = client.send_message("I need to book a meeting")
    print_response(response)
    
    # Test 4: Book a meeting (with details)
    print("\n📝 Test 4: Book a Meeting (With Full Details)")
    response = client.send_message(
        "Book a meeting for 2024-12-15 at 14:00. "
        "My name is John Doe and email is john@example.com. "
        "Reason: Discuss Q4 planning"
    )
    print_response(response)
    
    # Show session history
    print("\n📝 Session History")
    history = client.get_session_history()
    print(json.dumps(history, indent=2))
    
    # Clear session
    print("\n🗑️  Clearing session...")
    client.clear_session()
    print("Session cleared!")


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Cannot connect to the server.")
        print("Please make sure the server is running:")
        print("  python -m calcom_chatbot.main")
    except Exception as e:
        print(f"\n❌ Error: {e}")

