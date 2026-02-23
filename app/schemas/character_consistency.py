"""角色一致性数据模式"""
from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class ConsistencyModelResponse(BaseModel):
    """一致性模型响应"""
    character_id: str = Field(..., description="角色ID")
    reference_image_path: str = Field(..., description="参考图像路径")
    facial_features: Dict = Field(..., description="面部特征")
    clothing_features: Dict = Field(..., description="服装特征")
    style: str = Field(..., description="渲染风格")
    created_at: str = Field(..., description="创建时间")


class ConsistencyScoreResponse(BaseModel):
    """一致性评分响应"""
    facial_similarity: float = Field(..., description="面部相似度（0-1）")
    clothing_consistency: float = Field(..., description="服装一致性（0-1）")
    overall_score: float = Field(..., description="整体评分（0-1）")
    meets_requirements: bool = Field(..., description="是否满足要求")
    details: Dict = Field(default_factory=dict, description="详细信息")


class ExtractFeaturesRequest(BaseModel):
    """提取特征请求"""
    character_id: str = Field(..., description="角色ID")
    style: str = Field("anime", description="渲染风格（anime或realistic）")


class GenerateFrameRequest(BaseModel):
    """生成分镜请求"""
    character_id: str = Field(..., description="角色ID")
    scene_description: str = Field(..., description="场景描述")
    pose_reference_url: Optional[str] = Field(None, description="姿态参考图URL")
    style: str = Field("anime", description="渲染风格")


class GenerateFrameResponse(BaseModel):
    """生成分镜响应"""
    frame_url: str = Field(..., description="生成的分镜图像URL")
    character_id: str = Field(..., description="角色ID")
    scene_description: str = Field(..., description="场景描述")
    style: str = Field(..., description="渲染风格")
    processing_time_seconds: float = Field(..., description="处理时间（秒）")


class ValidateConsistencyRequest(BaseModel):
    """验证一致性请求"""
    character_id: str = Field(..., description="角色ID")
    generated_frame_urls: List[str] = Field(..., description="生成的分镜图像URL列表")


class BatchGenerateRequest(BaseModel):
    """批量生成请求"""
    character_id: str = Field(..., description="角色ID")
    scene_descriptions: List[str] = Field(..., description="场景描述列表")
    style: str = Field("anime", description="渲染风格")


class BatchGenerateResponse(BaseModel):
    """批量生成响应"""
    frame_urls: List[str] = Field(..., description="生成的分镜图像URL列表")
    character_id: str = Field(..., description="角色ID")
    total_frames: int = Field(..., description="总帧数")
    consistency_score: ConsistencyScoreResponse = Field(..., description="一致性评分")
    processing_time_seconds: float = Field(..., description="总处理时间（秒）")
