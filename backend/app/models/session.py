"""
Session model for managing user conversations
"""
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, String, DateTime, JSON, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()


class SessionStatus(str, enum.Enum):
    """Session status enumeration"""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ERROR = "error"


class SessionRole(str, enum.Enum):
    """Current role in the workflow"""
    STRATEGIST = "strategist"
    IMAGE_GENERATOR = "image_generator"
    EXECUTOR = "executor"


class SessionStage(str, enum.Enum):
    """Current stage in the workflow"""
    INIT = "init"
    STRATEGY = "strategy"
    IMAGE_GEN = "image_gen"
    EXECUTION = "execution"
    POST_PROCESS = "post_process"
    COMPLETED = "completed"


class Session(Base):
    """Session model"""
    __tablename__ = "sessions"
    
    session_id = Column(String(64), primary_key=True, index=True)
    user_id = Column(String(64), nullable=False, index=True)
    project_id = Column(String(64), nullable=True, index=True)
    
    current_role = Column(SQLEnum(SessionRole), default=SessionRole.STRATEGIST)
    current_stage = Column(SQLEnum(SessionStage), default=SessionStage.INIT)
    
    context = Column(JSON, default=dict)  # Stores workflow context
    status = Column(SQLEnum(SessionStatus), default=SessionStatus.ACTIVE)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "project_id": self.project_id,
            "current_role": self.current_role.value if self.current_role else None,
            "current_stage": self.current_stage.value if self.current_stage else None,
            "context": self.context,
            "status": self.status.value if self.status else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
