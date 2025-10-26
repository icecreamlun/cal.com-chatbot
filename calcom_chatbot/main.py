from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional, Tuple
from calcom_chatbot.graph import compiled_graph
from calcom_chatbot.state import AgentState
import uvicorn
import traceback
import logging
from datetime import datetime, timedelta
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI(
    title="Cal.com Chatbot API",
    description="A chatbot for interacting with Cal.com booking system",
    version="1.0.0"
)


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"


class ChatResponse(BaseModel):
    response: str
    intent: Optional[str] = None


# In-memory session storage with TTL (Time To Live)
# Format: session_id -> (messages, last_access_time)
sessions: Dict[str, Tuple[List[str], datetime]] = {}
SESSION_TTL = timedelta(hours=1)  # 会话1小时后过期


def get_session_messages(session_id: str) -> List[str]:
    """获取会话消息，如果过期则自动删除并返回空列表"""
    if session_id in sessions:
        messages, last_access = sessions[session_id]
        if datetime.now() - last_access > SESSION_TTL:
            # 会话过期，删除
            del sessions[session_id]
            logger.info(f"Session {session_id} expired and removed")
            return []
        return messages
    return []


def update_session_messages(session_id: str, messages: List[str]):
    """更新会话消息并刷新访问时间"""
    sessions[session_id] = (messages, datetime.now())


async def cleanup_expired_sessions():
    """后台任务：定期清理过期会话"""
    while True:
        await asyncio.sleep(600)  # 每10分钟检查一次
        now = datetime.now()
        expired_sessions = [
            sid for sid, (_, last_access) in sessions.items()
            if now - last_access > SESSION_TTL
        ]
        for sid in expired_sessions:
            del sessions[sid]
        if expired_sessions:
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")


@app.on_event("startup")
async def startup_event():
    """启动时启动后台清理任务"""
    asyncio.create_task(cleanup_expired_sessions())
    logger.info("Started background session cleanup task")


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Main chat endpoint.
    
    Accepts a user message and returns the chatbot's response.
    Sessions auto-expire after 1 hour of inactivity.
    """
    try:
        # Get existing messages (or empty list if new/expired)
        messages = get_session_messages(request.session_id)
        
        # Add user message
        messages.append(f"User: {request.message}")
        
        # Prepare initial state
        initial_state: AgentState = {
            "messages": messages.copy(),
            "user_query": request.message,
            "intent": None,
            "booking_details": None,
            "api_response": None,
            "final_response": ""
        }
        
        # Invoke the graph
        result = await compiled_graph.ainvoke(initial_state)
        
        # Add assistant response
        messages.append(f"Assistant: {result['final_response']}")
        
        # Save messages with updated timestamp
        update_session_messages(request.session_id, messages)
        
        return ChatResponse(
            response=result["final_response"],
            intent=result.get("intent")
        )
    
    except Exception as e:
        # Log the full traceback for debugging
        logger.error(f"Error processing chat request: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "message": "Cal.com Chatbot API is running"
    }


@app.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """Get conversation history for a session (if not expired)."""
    messages = get_session_messages(session_id)
    
    if not messages:
        raise HTTPException(status_code=404, detail="Session not found or expired")
    
    # Get last access time
    _, last_access = sessions.get(session_id, ([], datetime.now()))
    time_remaining = SESSION_TTL - (datetime.now() - last_access)
    
    return {
        "session_id": session_id,
        "messages": messages,
        "expires_in_seconds": int(time_remaining.total_seconds())
    }


@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Clear a session's conversation history."""
    if session_id in sessions:
        del sessions[session_id]
        return {"message": "Session cleared"}
    
    return {"message": "Session not found (may have already expired)"}


@app.get("/sessions")
async def list_sessions():
    """List all active sessions with their status."""
    now = datetime.now()
    session_list = []
    
    for session_id, (messages, last_access) in sessions.items():
        time_remaining = SESSION_TTL - (now - last_access)
        session_list.append({
            "session_id": session_id,
            "message_count": len(messages),
            "last_access": last_access.isoformat(),
            "expires_in_seconds": int(time_remaining.total_seconds())
        })
    
    return {
        "active_sessions": len(session_list),
        "sessions": session_list
    }


def main():
    """Run the FastAPI server."""
    uvicorn.run(app, host="0.0.0.0", port=8001)


if __name__ == "__main__":
    main()

