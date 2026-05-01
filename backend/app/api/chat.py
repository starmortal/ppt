"""
Chat/conversation API endpoints
"""
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
import json
from datetime import datetime
import uuid

from ..core.llm import get_llm_client
from ..services.script_executor import ScriptExecutor
from ..agents.strategist_agent import StrategistAgent

# Import shared session store
from .session import _sessions_store

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/test")
async def test_endpoint():
    """Test endpoint to verify API is working"""
    try:
        from ..core.llm import get_llm_client
        llm = get_llm_client()
        return {
            "status": "ok",
            "llm_type": type(llm).__name__,
            "message": "Chat API is working"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


# Temporary in-memory storage for messages
_messages_store: Dict[str, List[Any]] = {}


class SimpleSessionManager:
    """Simplified session manager for development (no DB/Redis)"""
    
    def get_session(self, session_id: str):
        """Get session from memory"""
        return _sessions_store.get(session_id)
    
    def add_message(self, session_id: str, role: str, content: str, message_id: str = None, metadata: Dict = None):
        """Add message to memory"""
        if session_id not in _messages_store:
            _messages_store[session_id] = []
        
        msg = {
            "id": message_id or f"msg_{uuid.uuid4().hex[:16]}",
            "role": role,
            "content": content,
            "metadata": metadata or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        _messages_store[session_id].append(msg)
        return msg
    
    def get_conversation_history(self, session_id: str, limit: int = 50):
        """Get conversation history from memory"""
        messages = _messages_store.get(session_id, [])
        return messages[-limit:] if limit else messages
    
    def update_context(self, session_id: str, updates: Dict):
        """Update session context"""
        session = _sessions_store.get(session_id)
        if session:
            if "context" not in session:
                session["context"] = {}
            session["context"].update(updates)
    
    def update_session(self, session_id: str, current_role=None, current_stage=None):
        """Update session role/stage"""
        session = _sessions_store.get(session_id)
        if session:
            if current_role:
                session["current_role"] = current_role
            if current_stage:
                session["current_stage"] = current_stage


def get_session_manager() -> SimpleSessionManager:
    """Get session manager instance"""
    return SimpleSessionManager()


def get_script_executor() -> ScriptExecutor:
    """Get script executor instance"""
    from ..core.config import settings
    return ScriptExecutor(
        scripts_base_path=settings.SCRIPTS_BASE_PATH,
        projects_base_path=settings.PROJECTS_BASE_PATH
    )


def get_agent(
    session_manager: SimpleSessionManager = Depends(get_session_manager),
    script_executor: ScriptExecutor = Depends(get_script_executor)
):
    """Get agent based on session role"""
    llm_client = get_llm_client()
    
    # For now, always return Strategist
    # In production, determine based on session.current_role
    return StrategistAgent(llm_client, session_manager, script_executor)


# Request/Response models
class SendMessageRequest(BaseModel):
    session_id: str
    message: str


class MessageResponse(BaseModel):
    message_id: str
    role: str
    content: str
    actions: List[Dict[str, Any]] = []
    metadata: Dict[str, Any] = {}
    timestamp: str


class ConversationHistoryResponse(BaseModel):
    messages: List[MessageResponse]
    total: int


@router.post("/message", response_model=MessageResponse)
async def send_message(
    request: SendMessageRequest,
    agent: StrategistAgent = Depends(get_agent),
    session_manager: SimpleSessionManager = Depends(get_session_manager)
):
    """
    Send a message in the conversation
    
    The message is processed by the current active agent
    (Strategist, Image_Generator, or Executor) based on
    the session's current role.
    
    Returns the AI's response along with any actions taken.
    """
    try:
        # Get session
        session = session_manager.get_session(request.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Save user message
        user_msg_id = f"msg_{uuid.uuid4().hex[:16]}"
        session_manager.add_message(
            session_id=request.session_id,
            role="user",
            content=request.message,
            message_id=user_msg_id
        )
        
        # Process with agent
        try:
            result = agent.process_message(
                session_id=request.session_id,
                user_message=request.message
            )
        except Exception as agent_error:
            logger.error(f"Agent processing failed: {agent_error}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Agent error: {str(agent_error)}")
        
        # Save AI response
        ai_msg_id = f"msg_{uuid.uuid4().hex[:16]}"
        session_manager.add_message(
            session_id=request.session_id,
            role="assistant",
            content=result["content"],
            message_id=ai_msg_id,
            metadata={
                "actions": result.get("actions", []),
                "role": session.get("current_role", "strategist")
            }
        )
        
        # Update session context
        if result.get("context_updates"):
            session_manager.update_context(
                session_id=request.session_id,
                updates=result["context_updates"]
            )
        
        # Handle role/stage switch
        if result.get("role_switch"):
            session_manager.update_session(
                session_id=request.session_id,
                current_role=result["role_switch"],
                current_stage=result.get("stage_switch")
            )
        
        return MessageResponse(
            message_id=ai_msg_id,
            role=session.get("current_role", "strategist"),
            content=result["content"],
            actions=result.get("actions", []),
            metadata={
                "role_switch": result.get("role_switch"),
                "stage_switch": result.get("stage_switch")
            },
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Failed to send message: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{session_id}", response_model=ConversationHistoryResponse)
async def get_conversation_history(
    session_id: str,
    limit: Optional[int] = 50,
    offset: Optional[int] = 0
):
    """
    Get conversation history for a session
    
    Returns all messages in the conversation, ordered by timestamp.
    """
    try:
        # TODO: Implement with session_manager
        return ConversationHistoryResponse(
            messages=[],
            total=0
        )
    except Exception as e:
        logger.error(f"Failed to get conversation history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/stream")
async def websocket_chat(websocket: WebSocket):
    """
    WebSocket endpoint for streaming chat responses
    
    Provides real-time streaming of AI responses and progress updates.
    
    Client sends:
    {
        "session_id": "sess_xxx",
        "message": "user message"
    }
    
    Server sends:
    {
        "type": "token",  // or "done", "error", "progress"
        "content": "...",
        "metadata": {}
    }
    """
    await websocket.accept()
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            session_id = message_data.get("session_id")
            user_message = message_data.get("message")
            
            if not session_id or not user_message:
                await websocket.send_json({
                    "type": "error",
                    "content": "Missing session_id or message"
                })
                continue
            
            # TODO: Process message with agent and stream response
            # For now, send mock streaming response
            response_text = "This is a streaming response. "
            
            for word in response_text.split():
                await websocket.send_json({
                    "type": "token",
                    "content": word + " "
                })
            
            await websocket.send_json({
                "type": "done",
                "message_id": "msg_123"
            })
            
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.send_json({
            "type": "error",
            "content": str(e)
        })
