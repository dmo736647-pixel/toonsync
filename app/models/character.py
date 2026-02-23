"""角色模型"""
from sqlalchemy import Column, String, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from app.models.base import BaseModel, GUID


class RenderStyle(str, enum.Enum):
    """渲染风格"""
    ANIME = "anime"
    REALISTIC = "realistic"


class Character(BaseModel):
    """角色模型"""
    
    __tablename__ = "characters"
    
    project_id = Column(GUID(), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    reference_image_url = Column(Text, nullable=False)
    consistency_model_url = Column(Text, nullable=True)
    style = Column(SQLEnum(RenderStyle), nullable=False)
    
    # 关系
    project = relationship("Project", back_populates="characters")
    storyboard_frames = relationship("StoryboardFrame", back_populates="character")
