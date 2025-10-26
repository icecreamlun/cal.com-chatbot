"""
Cal.com Chatbot Frontend using Chainlit
Simple, clean, and decoupled from backend
"""
import chainlit as cl
import httpx
import os
from datetime import datetime
import uuid

# Backend API configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8001")


@cl.on_chat_start
async def start():
    """Initialize chat session."""
    # Generate a unique session ID for this chat
    session_id = str(uuid.uuid4())
    cl.user_session.set("session_id", session_id)
    
    # Welcome message
    await cl.Message(
        content="""👋 Welcome to Cal.com Chatbot!

I can help you with:
- 📅 **Book meetings** - "Book a meeting tomorrow at 2pm with John Doe, john@example.com"
- 📋 **View events** - "Show me my scheduled events"
- ❌ **Cancel meetings** - "Cancel my meeting with John"
- 🔄 **Reschedule meetings** - "Reschedule my meeting to tomorrow at 3pm"

How can I help you today?"""
    ).send()


@cl.on_message
async def main(message: cl.Message):
    """Handle user messages."""
    # Get session ID
    session_id = cl.user_session.get("session_id")
    
    # Show loading indicator
    msg = cl.Message(content="")
    await msg.send()
    
    try:
        # Call backend API
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{BACKEND_URL}/chat",
                json={
                    "message": message.content,
                    "session_id": session_id
                }
            )
            response.raise_for_status()
            data = response.json()
            
            # Get response and intent
            bot_response = data.get("response", "Sorry, I couldn't process that.")
            intent = data.get("intent", "general")
            
            # Add intent badge for debugging (optional)
            if os.getenv("SHOW_INTENT") == "true":
                bot_response = f"[Intent: {intent}]\n\n{bot_response}"
            
            # Update message with response
            msg.content = bot_response
            await msg.update()
            
    except httpx.HTTPError as e:
        error_message = f"❌ Error connecting to backend: {str(e)}"
        msg.content = error_message
        await msg.update()
    except Exception as e:
        error_message = f"❌ An error occurred: {str(e)}"
        msg.content = error_message
        await msg.update()


@cl.on_chat_end
def end():
    """Clean up when chat ends."""
    print(f"Chat session ended at {datetime.now()}")

