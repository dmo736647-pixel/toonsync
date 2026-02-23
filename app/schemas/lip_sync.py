"""口型同步数据模式"""
from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class PhonemeInfo(BaseModel):
    """音素信息"""
    phoneme: str = Field(..., description="音素")
    start_time: float = Field(..., description="开始时间（秒）")
    end_time: float = Field(..., description="结束时间（秒）")
    tone: int = Field(0, description="声调（0-5）")
    word: Optional[str] = Field(None, description="所属词语")


class AudioAnalysisResponse(BaseModel):
    """音频分析响应"""
    phonemes: List[PhonemeInfo] = Field(..., description="音素序列")
    duration: float = Field(..., description="音频时长（秒）")
    sample_rate: int = Field(..., description="采样率")
    transcript: str = Field("", description="转录文本")
    created_at: str = Field(..., description="创建时间")


class LipKeyframeResponse(BaseModel):
    """口型关键帧响应"""
    timestamp: float = Field(..., description="时间戳（秒）")
    phoneme: str = Field(..., description="音素")
    mouth_shape: str = Field(..., description="口型形状")
    intensity: float = Field(..., description="口型强度（0-1）")


class SyncAccuracyResponse(BaseModel):
    """同步精度报告响应"""
    average_error_ms: float = Field(..., description="平均误差（毫秒）")
    max_error_ms: float = Field(..., description="最大误差（毫秒）")
    accuracy_rate: float = Field(..., description="准确率（0-1）")
    total_keyframes: int = Field(..., description="总关键帧数")
    error_distribution: Dict[str, int] = Field(default_factory=dict, description="误差分布")
    quality_score: float = Field(..., description="质量评分（0-100）")
    quality_level: str = Field(..., description="质量等级")


class LipSyncRequest(BaseModel):
    """口型同步请求"""
    audio_file_url: str = Field(..., description="音频文件URL")
    style: str = Field("anime", description="口型风格（anime或realistic）")
    character_image_url: Optional[str] = Field(None, description="角色图像URL")


class LipSyncResponse(BaseModel):
    """口型同步响应"""
    audio_analysis: AudioAnalysisResponse = Field(..., description="音频分析结果")
    keyframes: List[LipKeyframeResponse] = Field(..., description="口型关键帧")
    sync_accuracy: SyncAccuracyResponse = Field(..., description="同步精度报告")
    processing_time_seconds: float = Field(..., description="处理时间（秒）")
