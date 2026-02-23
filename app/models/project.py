"""项目模型"""
from sqlalchemy import Column, String, Float, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from app.models.base import BaseModel, GUID


class AspectRatio(str, enum.Enum):
    """画面比例"""
    VERTICAL_9_16 = "9:16"
    HORIZONTAL_16_9 = "16:9"
    SQUARE_1_1 = "1:1"


class Project(BaseModel):
    """项目模型"""
    
    __tablename__ = "projects"
    
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    aspect_ratio = Column(SQLEnum(AspectRatio), default=AspectRatio.VERTICAL_9_16, nullable=False)
    duration_minutes = Column(Float, nullable=True)
    script = Column(Text, nullable=True)
    
    # 关系
    user = relationship("User", back_populates="projects")
    characters = relationship("Character", back_populates="project", cascade="all, delete-orphan")
    storyboard_frames = relationship("StoryboardFrame", back_populates="project", cascade="all, delete-orphan")
    audio_tracks = relationship("AudioTrack", back_populates="project", cascade="all, delete-orphan")
