"""
视频渲染数据模式
"""
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, validator


class VideoProjectConfigCreate(BaseModel):
    """创建视频项目配置请求"""
    aspect_ratio: str = Field(default="9:16", description="画面比例")
    duration_minutes: float = Field(default=2.0, ge=0.5, le=10.0, description="目标时长（分钟）")
    quality: str = Field(default="1080p", description="视频质量")
    format: str = Field(default="mp4", description="视频格式")
    
    @validator('aspect_ratio')
    def validate_aspect_ratio(cls, v):
        valid_ratios = ["9:16", "16:9", "1:1"]
        if v not in valid_ratios:
            raise ValueError(f"画面比例必须是以下之一: {', '.join(valid_ratios)}")
        return v
    
    @validator('quality')
    def validate_quality(cls, v):
        valid_qualities = ["720p", "1080p", "4K"]
        if v not in valid_qualities:
            raise ValueError(f"视频质量必须是以下之一: {', '.join(valid_qualities)}")
        return v
    
    @validator('format')
    def validate_format(cls, v):
        valid_formats = ["mp4", "mov"]
        if v not in valid_formats:
            raise ValueError(f"视频格式必须是以下之一: {', '.join(valid_formats)}")
        return v


class VideoProjectConfigResponse(BaseModel):
    """视频项目配置响应"""
    aspect_ratio: str
    duration_minutes: float
    quality: str
    format: str
    resolution: Dict[str, int]
    
    class Config:
        from_attributes = True


class CompositionOptimizeRequest(BaseModel):
    """画面构图优化请求"""
    image_url: str = Field(..., description="原始图像URL")
    aspect_ratio: str = Field(..., description="目标画面比例")
    
    @validator('aspect_ratio')
    def validate_aspect_ratio(cls, v):
        valid_ratios = ["9:16", "16:9", "1:1"]
        if v not in valid_ratios:
            raise ValueError(f"画面比例必须是以下之一: {', '.join(valid_ratios)}")
        return v


class CompositionOptimizeResponse(BaseModel):
    """画面构图优化响应"""
    optimized_image_url: str = Field(..., description="优化后的图像URL")
    original_size: Dict[str, int] = Field(..., description="原始尺寸")
    optimized_size: Dict[str, int] = Field(..., description="优化后尺寸")


class VideoRenderRequest(BaseModel):
    """视频渲染请求"""
    project_id: str = Field(..., description="项目ID")
    frame_urls: List[str] = Field(..., min_items=1, description="分镜图像URL列表")
    config: VideoProjectConfigCreate = Field(..., description="项目配置")
    audio_url: Optional[str] = Field(None, description="音频文件URL（可选）")
    
    @validator('frame_urls')
    def validate_frame_urls(cls, v):
        if not v:
            raise ValueError("至少需要一个分镜图像")
        return v


class VideoRenderResponse(BaseModel):
    """视频渲染响应"""
    video_url: str = Field(..., description="渲染完成的视频URL")
    render_time_seconds: float = Field(..., description="渲染耗时（秒）")
    file_size_mb: float = Field(..., description="文件大小（MB）")
    config: VideoProjectConfigResponse = Field(..., description="项目配置")


class VideoPreviewRequest(BaseModel):
    """视频预览请求"""
    frame_urls: List[str] = Field(..., min_items=1, description="分镜图像URL列表")
    config: VideoProjectConfigCreate = Field(..., description="项目配置")
    audio_url: Optional[str] = Field(None, description="音频文件URL（可选）")


class VideoPreviewResponse(BaseModel):
    """视频预览响应"""
    preview_url: str = Field(..., description="预览视频URL")
    duration_seconds: float = Field(..., description="视频时长（秒）")


class RenderTimeEstimateRequest(BaseModel):
    """渲染时间估算请求"""
    frame_count: int = Field(..., ge=1, description="分镜数量")
    config: VideoProjectConfigCreate = Field(..., description="项目配置")


class RenderTimeEstimateResponse(BaseModel):
    """渲染时间估算响应"""
    estimated_time_minutes: float = Field(..., description="预估渲染时间（分钟）")
    frame_count: int = Field(..., description="分镜数量")
    quality: str = Field(..., description="视频质量")
