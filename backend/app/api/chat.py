"""
Chat/conversation API endpoints
"""
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
import json

logger = logging.getLogger(__name__)

router = APIRouter()


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
async def send_message(request: SendMessageRequest):
    """
    Send a message in the conversation
    
    The message is processed by the current active agent
    (Strategist, Image_Generator, or Executor) based on
    the session's current role.
    
    Returns the AI's response along with any actions taken.
    """
    try:
        # TODO: Implement with agent system
        # 1. Get session
        # 2. Determine current agent
        # 3. Process message with agent
        # 4. Save message to history
        # 5. Return response
        
        import uuid
        from datetime import datetime
        
        return MessageResponse(
            message_id=f"msg_{uuid.uuid4().hex[:16]}",
            role="strategist",
            content="Thank you for your message. Let's start with the first confirmation: What canvas format would you like? (16:9 or 4:3)",
            actions=[],
            metadata={},
            timestamp=datetime.utcnow().isoformat()
        )
    except Exception as e:
        logger.error(f"Failed to send message: {e}")
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
