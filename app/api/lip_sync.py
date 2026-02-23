"""口型同步API端点"""
import time
import tempfile
import os
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.schemas.lip_sync import (
    LipSyncRequest,
    LipSyncResponse,
    AudioAnalysisResponse,
    LipKeyframeResponse,
    SyncAccuracyResponse,
    PhonemeInfo
)
from app.services.lip_sync import (
    get_lip_sync_engine,
    AudioAnalysis,
    LipKeyframe
)

router = APIRouter(prefix="/lip-sync", tags=["lip-sync"])


@router.post("/analyze", response_model=AudioAnalysisResponse)
async def analyze_audio(
    audio_file: UploadFile = File(..., description="音频文件"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    分析音频文件，提取音素和时序信息
    
    参数:
        audio_file: 上传的音频文件
        current_user: 当前用户
        db: 数据库会话
    
    返回:
        AudioAnalysisResponse: 音频分析结果
    """
    # 验证文件类型
    if not audio_file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="文件必须是音频格式")
    
    # 保存临时文件
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
        content = await audio_file.read()
        temp_file.write(content)
        temp_file_path = temp_file.name
    
    try:
        # 获取口型同步引擎
        engine = get_lip_sync_engine()
        
        # 分析音频
        analysis = engine.analyze_audio(temp_file_path)
        
        # 转换为响应格式
        return AudioAnalysisResponse(
            phonemes=[PhonemeInfo(**p) for p in analysis.phonemes],
            duration=analysis.duration,
            sample_rate=analysis.sample_rate,
            transcript=analysis.transcript,
            created_at=analysis.created_at.isoformat()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"音频分析失败: {str(e)}")
    
    finally:
        # 清理临时文件
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)


@router.post("/generate", response_model=LipSyncResponse)
async def generate_lip_sync(
    audio_file: UploadFile = File(..., description="音频文件"),
    style: str = "anime",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    生成完整的口型同步动画
    
    参数:
        audio_file: 上传的音频文件
        style: 口型风格（anime或realistic）
        current_user: 当前用户
        db: 数据库会话
    
    返回:
        LipSyncResponse: 完整的口型同步结果
    """
    start_time = time.time()
    
    # 验证文件类型
    if not audio_file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="文件必须是音频格式")
    
    # 验证风格参数
    if style not in ["anime", "realistic"]:
        raise HTTPException(status_code=400, detail="风格必须是anime或realistic")
    
    # 保存临时文件
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
        content = await audio_file.read()
        temp_file.write(content)
        temp_file_path = temp_file.name
    
    try:
        # 获取口型同步引擎
        engine = get_lip_sync_engine()
        
        # 1. 分析音频
        analysis = engine.analyze_audio(temp_file_path)
        
        # 2. 生成口型关键帧
        keyframes = engine.generate_lip_keyframes(analysis, style=style)
        
        # 3. 验证同步精度
        accuracy = engine.validate_sync_accuracy(keyframes, analysis)
        
        # 计算处理时间
        processing_time = time.time() - start_time
        
        # 转换为响应格式
        return LipSyncResponse(
            audio_analysis=AudioAnalysisResponse(
                phonemes=[PhonemeInfo(**p) for p in analysis.phonemes],
                duration=analysis.duration,
                sample_rate=analysis.sample_rate,
                transcript=analysis.transcript,
                created_at=analysis.created_at.isoformat()
            ),
            keyframes=[
                LipKeyframeResponse(
                    timestamp=kf.timestamp,
                    phoneme=kf.phoneme,
                    mouth_shape=kf.mouth_shape,
                    intensity=kf.intensity
                )
                for kf in keyframes
            ],
            sync_accuracy=SyncAccuracyResponse(
                average_error_ms=accuracy.average_error_ms,
                max_error_ms=accuracy.max_error_ms,
                accuracy_rate=accuracy.accuracy_rate,
                total_keyframes=accuracy.total_keyframes,
                error_distribution=accuracy.error_distribution,
                quality_score=accuracy.quality_score,
                quality_level=accuracy.get_quality_level()
            ),
            processing_time_seconds=processing_time
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"口型同步生成失败: {str(e)}")
    
    finally:
        # 清理临时文件
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)


@router.get("/health")
async def health_check():
    """
    健康检查端点
    
    返回:
        dict: 服务状态
    """
    try:
        engine = get_lip_sync_engine()
        return {
            "status": "healthy",
            "whisper_model": engine.whisper_model_name,
            "service": "lip-sync"
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"服务不可用: {str(e)}")



@router.post("/generate-report")
async def generate_sync_report(
    audio_file: UploadFile = File(..., description="音频文件"),
    style: str = "anime",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    生成详细的口型同步报告
    
    参数:
        audio_file: 上传的音频文件
        style: 口型风格（anime或realistic）
        current_user: 当前用户
        db: 数据库会话
    
    返回:
        dict: 详细的同步报告
    """
    # 验证文件类型
    if not audio_file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="文件必须是音频格式")
    
    # 验证风格参数
    if style not in ["anime", "realistic"]:
        raise HTTPException(status_code=400, detail="风格必须是anime或realistic")
    
    # 保存临时文件
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
        content = await audio_file.read()
        temp_file.write(content)
        temp_file_path = temp_file.name
    
    try:
        # 获取口型同步引擎
        engine = get_lip_sync_engine()
        
        # 1. 分析音频
        analysis = engine.analyze_audio(temp_file_path)
        
        # 2. 生成口型关键帧
        keyframes = engine.generate_lip_keyframes(analysis, style=style)
        
        # 3. 生成详细报告
        report = engine.generate_sync_report(keyframes, analysis, style)
        
        return report
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"报告生成失败: {str(e)}")
    
    finally:
        # 清理临时文件
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)


@router.post("/export-wav2lip")
async def export_for_wav2lip(
    audio_file: UploadFile = File(..., description="音频文件"),
    style: str = "anime",
    fps: int = 25,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    导出Wav2Lip兼容格式的口型数据
    
    参数:
        audio_file: 上传的音频文件
        style: 口型风格（anime或realistic）
        fps: 视频帧率
        current_user: 当前用户
        db: 数据库会话
    
    返回:
        dict: Wav2Lip格式的帧数据
    """
    # 验证文件类型
    if not audio_file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="文件必须是音频格式")
    
    # 验证参数
    if style not in ["anime", "realistic"]:
        raise HTTPException(status_code=400, detail="风格必须是anime或realistic")
    
    if not 15 <= fps <= 60:
        raise HTTPException(status_code=400, detail="帧率必须在15-60之间")
    
    # 保存临时文件
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
        content = await audio_file.read()
        temp_file.write(content)
        temp_file_path = temp_file.name
    
    try:
        # 获取口型同步引擎
        engine = get_lip_sync_engine()
        
        # 1. 分析音频
        analysis = engine.analyze_audio(temp_file_path)
        
        # 2. 生成口型关键帧
        keyframes = engine.generate_lip_keyframes(analysis, style=style)
        
        # 3. 导出Wav2Lip格式
        wav2lip_frames = engine.export_keyframes_for_wav2lip(keyframes, fps=fps)
        
        return {
            "total_frames": len(wav2lip_frames),
            "fps": fps,
            "duration": analysis.duration,
            "style": style,
            "frames": wav2lip_frames
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")
    
    finally:
        # 清理临时文件
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
