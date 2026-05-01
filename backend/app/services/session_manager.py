"""
Session management service
Manages user sessions, context, and role switching
"""
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import logging

from ..models.session import Session, SessionStatus, SessionRole, SessionStage
from ..models.message import Message

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages user sessions and conversation state"""
    
    def __init__(self, db_session, redis_client, expire_hours: int = 24):
        self.db = db_session
        self.redis = redis_client
        self.expire_hours = expire_hours
    
    def create_session(self, user_id: str) -> Session:
        """Create a new session"""
        session_id = f"sess_{uuid.uuid4().hex[:16]}"
        
        session = Session(
            session_id=session_id,
            user_id=user_id,
            current_role=SessionRole.STRATEGIST,
            current_stage=SessionStage.INIT,
            context={},
            status=SessionStatus.ACTIVE
        )
        
        self.db.add(session)
        self.db.commit()
        
        # Cache in Redis
        self._cache_session(session)
        
        logger.info(f"Created session {session_id} for user {user_id}")
        return session
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """Get session by ID (checks cache first)"""
        # Try cache first
        cached = self._get_cached_session(session_id)
        if cached:
            return cached
        
        # Fallback to database
        session = self.db.query(Session).filter(
            Session.session_id == session_id
        ).first()
        
        if session:
            self._cache_session(session)
        
        return session
    
    def update_context(
        self,
        session_id: str,
        context_updates: Dict[str, Any]
    ) -> Session:
        """Update session context"""
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")
        
        # Merge context
        session.context.update(context_updates)
        session.updated_at = datetime.utcnow()
        
        self.db.commit()
        self._cache_session(session)
        
        logger.info(f"Updated context for session {session_id}")
        return session
    
    def switch_role(
        self,
        session_id: str,
        new_role: SessionRole,
        new_stage: Optional[SessionStage] = None
    ) -> Session:
        """Switch to a different role"""
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")
        
        old_role = session.current_role
        session.current_role = new_role
        
        if new_stage:
            session.current_stage = new_stage
        
        session.updated_at = datetime.utcnow()
        
        self.db.commit()
        self._cache_session(session)
        
        logger.info(
            f"Session {session_id} role switched: {old_role} -> {new_role}"
        )
        return session
    
    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Message:
        """Add a message to conversation history"""
        message_id = f"msg_{uuid.uuid4().hex[:16]}"
        
        message = Message(
            message_id=message_id,
            session_id=session_id,
            role=role,
            content=content,
            metadata=metadata or {}
        )
        
        self.db.add(message)
        self.db.commit()
        
        # Update session timestamp
        session = self.get_session(session_id)
        if session:
            session.updated_at = datetime.utcnow()
            self.db.commit()
            self._cache_session(session)
        
        return message
    
    def get_conversation_history(
        self,
        session_id: str,
        limit: Optional[int] = None
    ) -> List[Message]:
        """Get conversation history for a session"""
        query = self.db.query(Message).filter(
            Message.session_id == session_id
        ).order_by(Message.created_at)
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    def update_status(
        self,
        session_id: str,
        status: SessionStatus
    ) -> Session:
        """Update session status"""
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")
        
        session.status = status
        session.updated_at = datetime.utcnow()
        
        self.db.commit()
        self._cache_session(session)
        
        return session
    
    def link_project(self, session_id: str, project_id: str) -> Session:
        """Link a project to the session"""
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")
        
        session.project_id = project_id
        session.updated_at = datetime.utcnow()
        
        self.db.commit()
        self._cache_session(session)
        
        logger.info(f"Linked project {project_id} to session {session_id}")
        return session
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions"""
        cutoff = datetime.utcnow() - timedelta(hours=self.expire_hours)
        
        expired = self.db.query(Session).filter(
            Session.updated_at < cutoff,
            Session.status != SessionStatus.COMPLETED
        ).all()
        
        count = len(expired)
        
        for session in expired:
            session.status = SessionStatus.ERROR
            self._remove_cached_session(session.session_id)
        
        self.db.commit()
        
        logger.info(f"Cleaned up {count} expired sessions")
        return count
    
    # ========== Redis Cache Methods ==========
    
    def _cache_session(self, session: Session):
        """Cache session in Redis"""
        if not self.redis:
            return
        
        key = f"session:{session.session_id}"
        data = session.to_dict()
        
        try:
            self.redis.setex(
                key,
                timedelta(hours=self.expire_hours),
                str(data)
            )
        except Exception as e:
            logger.warning(f"Failed to cache session: {e}")
    
    def _get_cached_session(self, session_id: str) -> Optional[Session]:
        """Get session from Redis cache"""
        if not self.redis:
            return None
        
        key = f"session:{session_id}"
        
        try:
            data = self.redis.get(key)
            if data:
                # Note: In production, use proper serialization (JSON/pickle)
                # This is simplified for the example
                return self.db.query(Session).filter(
                    Session.session_id == session_id
                ).first()
        except Exception as e:
            logger.warning(f"Failed to get cached session: {e}")
        
        return None
    
    def _remove_cached_session(self, session_id: str):
        """Remove session from Redis cache"""
        if not self.redis:
            return
        
        key = f"session:{session_id}"
        
        try:
            self.redis.delete(key)
        except Exception as e:
            logger.warning(f"Failed to remove cached session: {e}")
