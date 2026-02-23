"""
音效匹配数据模式
"""
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class ScriptParseRequest(BaseModel):
    """剧本解析请求"""
    script: str = Field(..., min_length=1, description="剧本文本")


class SceneSegmentResponse(BaseModel):
    """场景片段响应"""
    scene_id: str
    text: str
    scene_type: str
    actions: List[str]
    emotions: List[str]
    characters: List[str]
    start_time: float
    duration: float
    keywords: List[str]


class ScriptParseResponse(BaseModel):
    """剧本解析响应"""
    segments: List[SceneSegmentResponse]
    total_duration: float
    segment_count: int


class SoundEffectResponse(BaseModel):
    """音效响应"""
    effect_id: str
    name: str
    description: str
    category: str
    tags: List[str]
    duration: float
    file_url: str


class RecommendRequest(BaseModel):
    """音效推荐请求"""
    scene_id: str = Field(..., description="场景ID")
    scene_text: str = Field(..., description="场景文本")
    scene_type: str = Field(..., description="场景类型")
    top_k: int = Field(default=3, ge=1, le=10, description="返回推荐数量")


class RecommendationResponse(BaseModel):
    """推荐响应"""
    effect: SoundEffectResponse
    score: float = Field(..., ge=0.0, le=1.0, description="相似度分数")


class RecommendResponse(BaseModel):
    """音效推荐响应"""
    scene_id: str
    recommendations: List[RecommendationResponse]


class PlacementRequest(BaseModel):
    """音效放置请求"""
    scene_id: str
    effect_id: str


class AutoPlaceRequest(BaseModel):
    """自动放置请求"""
    script: str = Field(..., description="剧本文本")
    placements: List[PlacementRequest] = Field(..., description="放置列表")


class PlacementResponse(BaseModel):
    """放置响应"""
    scene_id: str
    effect_id: str
    effect_name: str
    start_time: float
    duration: float
    file_url: str
    volume: float


class AutoPlaceResponse(BaseModel):
    """自动放置响应"""
    placements: List[PlacementResponse]
    total_effects: int


class UploadEffectRequest(BaseModel):
    """上传音效请求"""
    name: str = Field(..., min_length=1, description="音效名称")
    description: str = Field(..., description="描述")
    category: str = Field(..., description="类别")
    tags: List[str] = Field(..., min_items=1, description="标签列表")
    duration: float = Field(..., gt=0, description="时长（秒）")
    file_url: str = Field(..., description="文件URL")


class SearchEffectsRequest(BaseModel):
    """搜索音效请求"""
    category: Optional[str] = Field(None, description="类别")
    tags: Optional[List[str]] = Field(None, description="标签列表")


class SearchEffectsResponse(BaseModel):
    """搜索音效响应"""
    effects: List[SoundEffectResponse]
    total_count: int
