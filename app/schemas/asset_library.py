"""资源库管理Pydantic模式"""
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from enum import Enum


# ==================== 素材类型枚举 ====================

class AssetTypeEnum(str, Enum):
    """素材类型枚举"""
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"


# ==================== 音效库模式 ====================

class SoundEffectCreate(BaseModel):
    """创建音效请求"""
    name: str = Field(..., description="音效名称")
    category: str = Field(..., description="音效分类")
    audio_file_url: str = Field(..., description="音频文件URL")
    duration_seconds: float = Field(..., gt=0, description="音频时长（秒）")
    tags: Optional[List[str]] = Field(default=None, description="标签列表")


class SoundEffectUpdate(BaseModel):
    """更新音效请求"""
    name: Optional[str] = Field(None, description="音效名称")
    category: Optional[str] = Field(None, description="音效分类")
    tags: Optional[List[str]] = Field(None, description="标签列表")


class SoundEffectResponse(BaseModel):
    """音效响应"""
    id: UUID
    name: str
    category: str
    audio_file_url: str
    duration_seconds: float
    tags: Optional[List[str]] = None
    
    class Config:
        from_attributes = True
    
    @classmethod
    def from_orm_with_tags(cls, sound_effect):
        """从ORM对象创建响应，处理标签字符串"""
        tags = None
        if sound_effect.tags:
            tags = [tag.strip() for tag in sound_effect.tags.split(",") if tag.strip()]
        
        return cls(
            id=sound_effect.id,
            name=sound_effect.name,
            category=sound_effect.category,
            audio_file_url=sound_effect.audio_file_url,
            duration_seconds=sound_effect.duration_seconds,
            tags=tags
        )


class SoundEffectListResponse(BaseModel):
    """音效列表响应"""
    items: List[SoundEffectResponse]
    total: int
    skip: int
    limit: int


class CategoryListResponse(BaseModel):
    """分类列表响应"""
    categories: List[str]


class TagListResponse(BaseModel):
    """标签列表响应"""
    tags: List[str]


class BulkSoundEffectCreate(BaseModel):
    """批量创建音效请求"""
    sound_effects: List[SoundEffectCreate]



# ==================== 搜索相关模式 ====================

class SearchRequest(BaseModel):
    """搜索请求"""
    query: str = Field(..., description="搜索关键词")
    category: Optional[str] = Field(None, description="分类过滤")
    tags: Optional[List[str]] = Field(None, description="标签过滤")
    skip: int = Field(0, ge=0, description="跳过数量")
    limit: int = Field(100, ge=1, le=1000, description="返回数量限制")


class SearchResponse(BaseModel):
    """搜索响应"""
    items: List[SoundEffectResponse]
    total: int
    skip: int
    limit: int
    elapsed_time: float = Field(..., description="搜索耗时（秒）")


class SimilaritySearchRequest(BaseModel):
    """相似度搜索请求"""
    reference_tags: List[str] = Field(..., description="参考标签列表")
    category: Optional[str] = Field(None, description="分类过滤")
    top_k: int = Field(10, ge=1, le=100, description="返回前k个结果")



# ==================== 素材管理模式 ====================

class AssetMetadata(BaseModel):
    """素材元数据"""
    width: Optional[int] = Field(None, description="宽度（像素）")
    height: Optional[int] = Field(None, description="高度（像素）")
    duration_seconds: Optional[float] = Field(None, description="时长（秒）")


class AssetUploadRequest(BaseModel):
    """素材上传请求（用于表单数据）"""
    asset_type: AssetTypeEnum = Field(..., description="素材类型")
    category: Optional[str] = Field(None, description="分类")
    tags: Optional[List[str]] = Field(default=None, description="标签列表")
    description: Optional[str] = Field(None, description="描述")
    metadata: Optional[AssetMetadata] = Field(None, description="元数据")


class AssetUpdate(BaseModel):
    """更新素材请求"""
    name: Optional[str] = Field(None, description="素材名称")
    category: Optional[str] = Field(None, description="分类")
    tags: Optional[List[str]] = Field(None, description="标签列表")
    description: Optional[str] = Field(None, description="描述")


class AssetResponse(BaseModel):
    """素材响应"""
    id: UUID
    name: str
    asset_type: AssetTypeEnum
    file_url: str
    file_size: int
    mime_type: str
    duration_seconds: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None
    thumbnail_url: Optional[str] = None
    preview_url: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    description: Optional[str] = None
    
    class Config:
        from_attributes = True
    
    @classmethod
    def from_orm_with_tags(cls, asset):
        """从ORM对象创建响应，处理标签字符串"""
        tags = None
        if asset.tags:
            tags = [tag.strip() for tag in asset.tags.split(",") if tag.strip()]
        
        return cls(
            id=asset.id,
            name=asset.name,
            asset_type=asset.asset_type,
            file_url=asset.file_url,
            file_size=asset.file_size,
            mime_type=asset.mime_type,
            duration_seconds=asset.duration_seconds,
            width=asset.width,
            height=asset.height,
            thumbnail_url=asset.thumbnail_url,
            preview_url=asset.preview_url,
            category=asset.category,
            tags=tags,
            description=asset.description
        )


class AssetListResponse(BaseModel):
    """素材列表响应"""
    items: List[AssetResponse]
    total: int
    skip: int
    limit: int


class AssetSearchRequest(BaseModel):
    """素材搜索请求"""
    query: str = Field(..., description="搜索关键词")
    asset_type: Optional[AssetTypeEnum] = Field(None, description="素材类型过滤")
    category: Optional[str] = Field(None, description="分类过滤")
    tags: Optional[List[str]] = Field(None, description="标签过滤")
    skip: int = Field(0, ge=0, description="跳过数量")
    limit: int = Field(100, ge=1, le=1000, description="返回数量限制")


class AssetSearchResponse(BaseModel):
    """素材搜索响应"""
    items: List[AssetResponse]
    total: int
    skip: int
    limit: int
    elapsed_time: float = Field(..., description="搜索耗时（秒）")
