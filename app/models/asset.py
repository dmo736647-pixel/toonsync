"""素材模型"""
from sqlalchemy import Column, String, Text, Float, Integer, Enum as SQLEnum
import enum

from app.models.base import BaseModel


class AssetType(str, enum.Enum):
    """素材类型枚举"""
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"


class Asset(BaseModel):
    """素材模型"""
    
    __tablename__ = "assets"
    
    name = Column(String(255), nullable=False)
    asset_type = Column(SQLEnum(AssetType), nullable=False, index=True)
    file_url = Column(Text, nullable=False)
    file_size = Column(Integer, nullable=False)  # 文件大小（字节）
    mime_type = Column(String(100), nullable=False)
    
    # 元数据
    duration_seconds = Column(Float, nullable=True)  # 音频/视频时长
    width = Column(Integer, nullable=True)  # 图片/视频宽度
    height = Column(Integer, nullable=True)  # 图片/视频高度
    
    # 预览
    thumbnail_url = Column(Text, nullable=True)  # 缩略图URL
    preview_url = Column(Text, nullable=True)  # 预览URL（低分辨率）
    
    # 分类和标签
    category = Column(String(100), nullable=True, index=True)
    tags = Column(Text, nullable=True)  # 使用逗号分隔的字符串
    
    # 描述
    description = Column(Text, nullable=True)
