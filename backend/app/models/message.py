"""
Message model for storing conversation history
"""
from datetime import datetime
from typing import Dict, Any
from sqlalchemy import Column, String, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Message(Base):
    """Message model"""
    __tablename__ = "messages"
    
    message_id = Column(String(64), primary_key=True, index=True)
    session_id = Column(String(64), nullable=False, index=True)
    
    role = Column(String(32), nullable=False)  # user, strategist, image_generator, executor
    content = Column(Text, nullable=False)
    
    message_metadata = Column(JSON, default=dict)  # Additional data (actions, files, etc.)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "message_id": self.message_id,
            "session_id": self.session_id,
            "role": self.role,
            "content": self.content,
            "metadata": self.message_metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
