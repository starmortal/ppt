"""
Project model for managing PPT projects
"""
from datetime import datetime
from typing import Dict, Any
from sqlalchemy import Column, String, DateTime, JSON, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()


class ProjectStatus(str, enum.Enum):
    """Project status enumeration"""
    INIT = "init"
    STRATEGY = "strategy"
    IMAGE_GEN = "image_gen"
    EXECUTION = "execution"
    POST_PROCESS = "post_process"
    COMPLETED = "completed"
    ERROR = "error"


class Project(Base):
    """Project model"""
    __tablename__ = "projects"
    
    project_id = Column(String(64), primary_key=True, index=True)
    user_id = Column(String(64), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    format = Column(String(32), nullable=False)  # ppt169, ppt43, etc.
    
    status = Column(SQLEnum(ProjectStatus), default=ProjectStatus.INIT)
    file_path = Column(String(512), nullable=True)  # Storage path
    
    project_metadata = Column(JSON, default=dict)  # Additional metadata
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "project_id": self.project_id,
            "user_id": self.user_id,
            "name": self.name,
            "format": self.format,
            "status": self.status.value if self.status else None,
            "file_path": self.file_path,
            "metadata": self.project_metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
