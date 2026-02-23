"""音效模型"""
from sqlalchemy import Column, String, Text, Float

from app.models.base import BaseModel


class SoundEffect(BaseModel):
    """音效模型"""
    
    __tablename__ = "sound_effects"
    
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False, index=True)
    audio_file_url = Column(Text, nullable=False)
    duration_seconds = Column(Float, nullable=False)
    tags = Column(Text, nullable=True)  # 使用逗号分隔的字符串代替ARRAY
    # 向量嵌入用于语义检索（需要pgvector扩展）
    # embedding_vector = Column(VECTOR(768), nullable=True)
