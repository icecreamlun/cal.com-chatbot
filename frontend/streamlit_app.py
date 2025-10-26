"""
Cal.com Chatbot Frontend using Streamlit
Simple, clean, and decoupled from backend
"""
import streamlit as st
import httpx
import uuid
from datetime import datetime

# Backend API configuration
BACKEND_URL = "http://localhost:8001"

# Page configuration
st.set_page_config(
    page_title="Cal.com Chatbot",
    page_icon="📅",
    layout="centered"
)

# Custom CSS for better chat UI
st.markdown("""
<style>
    .stTextInput > div > div > input {
        caret-color: #ff4b4b;
    }
    div[data-testid="stChatMessage"] {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 10px;
    }
    div[data-testid="stChatMessage"][data-testid*="user"] {
        background-color: #e3f2fd;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

# Title and description
st.title("📅 Cal.com Chatbot")
st.caption("Book, list, cancel, and reschedule your meetings with natural language")

# Sidebar with info
with st.sidebar:
    st.header("💡 What I can do")
    st.markdown("""
    **📅 Book meetings**
    - "Book a meeting tomorrow at 2pm with John, john@test.com"
    
    **📋 View events**
    - "Show me my scheduled events"
    
    **❌ Cancel meetings**
    - "Cancel my meeting with John"
    
    **🔄 Reschedule meetings**
    - "Reschedule my meeting to tomorrow at 3pm"
    """)
    
    st.divider()
    
    st.caption(f"Session ID: {st.session_state.session_id[:8]}...")
    
    if st.button("🔄 New Session"):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Type your message..."):
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get bot response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Call backend API
                response = httpx.post(
                    f"{BACKEND_URL}/chat",
                    json={
                        "message": prompt,
                        "session_id": st.session_state.session_id
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                
                bot_response = data.get("response", "Sorry, I couldn't process that.")
                
                # Display response
                st.markdown(bot_response)
                
                # Add to session state
                st.session_state.messages.append({"role": "assistant", "content": bot_response})
                
            except httpx.HTTPError as e:
                error_message = f"❌ Error connecting to backend: {str(e)}"
                st.error(error_message)
                st.session_state.messages.append({"role": "assistant", "content": error_message})
            except Exception as e:
                error_message = f"❌ An error occurred: {str(e)}"
                st.error(error_message)
                st.session_state.messages.append({"role": "assistant", "content": error_message})

# Footer
st.divider()
st.caption("Powered by FastAPI, LangGraph, OpenAI, and Cal.com")

