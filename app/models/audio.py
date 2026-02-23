"""音频模型"""
from sqlalchemy import Column, Text, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.models.base import BaseModel, GUID


class AudioTrack(BaseModel):
    """音频轨道模型"""
    
    __tablename__ = "audio_tracks"
    
    project_id = Column(GUID(), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    audio_file_url = Column(Text, nullable=False)
    duration_seconds = Column(Float, nullable=False)
    transcript = Column(Text, nullable=True)
    audio_analysis = Column(JSON, nullable=True)
    
    # 关系
    project = relationship("Project", back_populates="audio_tracks")
