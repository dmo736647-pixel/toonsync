"""
视频渲染API端点
"""
import io
import tempfile
from pathlib import Path
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.core.storage import StorageManager
from app.models.user import User
from app.schemas.video_rendering import (
    VideoProjectConfigCreate,
    VideoProjectConfigResponse,
    CompositionOptimizeRequest,
    CompositionOptimizeResponse,
    VideoRenderRequest,
    VideoRenderResponse,
    VideoPreviewRequest,
    VideoPreviewResponse,
    RenderTimeEstimateRequest,
    RenderTimeEstimateResponse
)
from app.services.video_rendering import (
    VideoRenderingEngine,
    AspectRatio,
    VideoQuality,
    VideoFormat
)
from PIL import Image
from datetime import datetime


router = APIRouter(prefix="/video-rendering", tags=["video-rendering"])


@router.post("/config", response_model=VideoProjectConfigResponse)
async def create_project_config(
    config_data: VideoProjectConfigCreate,
    current_user: User = Depends(get_current_user)
):
    """
    创建视频项目配置
    
    支持：
    - 9:16竖屏（默认）
    - 16:9横屏
    - 1:1方屏
    - 多种质量和格式选项
    """
    try:
        engine = VideoRenderingEngine()
        
        # 创建配置
        config = engine.create_project_config(
            aspect_ratio=AspectRatio(config_data.aspect_ratio),
            duration_minutes=config_data.duration_minutes,
            quality=VideoQuality(config_data.quality),
            format=VideoFormat(config_data.format)
        )
        
        return VideoProjectConfigResponse(**config.to_dict())
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建配置失败: {str(e)}")


@router.post("/optimize-composition", response_model=CompositionOptimizeResponse)
async def optimize_composition(
    request: CompositionOptimizeRequest,
    current_user: User = Depends(get_current_user)
):
    """
    优化画面构图以适配目标比例
    
    自动裁剪和调整图像以适配竖屏、横屏或方屏格式
    """
    try:
        engine = VideoRenderingEngine()
        storage = StorageService()
        
        # 下载原始图像
        image_data = storage.download_file(request.image_url)
        original_image = Image.open(io.BytesIO(image_data))
        original_size = {"width": original_image.width, "height": original_image.height}
        
        # 优化构图
        optimized_data = engine.optimize_composition(
            image_data,
            AspectRatio(request.aspect_ratio)
        )
        
        # 获取优化后的尺寸
        optimized_image = Image.open(io.BytesIO(optimized_data))
        optimized_size = {"width": optimized_image.width, "height": optimized_image.height}
        
        # 保存优化后的图像
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"optimized/composition_{timestamp}.png"
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            tmp.write(optimized_data)
            tmp_path = tmp.name
        
        optimized_url = storage.upload_file(tmp_path, output_path)
        Path(tmp_path).unlink()
        
        return CompositionOptimizeResponse(
            optimized_image_url=optimized_url,
            original_size=original_size,
            optimized_size=optimized_size
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"构图优化失败: {str(e)}")


@router.post("/render", response_model=VideoRenderResponse)
async def render_video(
    request: VideoRenderRequest,
    current_user: User = Depends(get_current_user)
):
    """
    渲染最终视频
    
    性能要求：1-3分钟视频在5分钟内完成渲染
    """
    try:
        engine = VideoRenderingEngine()
        storage = StorageService()
        
        start_time = datetime.now()
        
        # 下载所有分镜图像
        frames = []
        for frame_url in request.frame_urls:
            frame_data = storage.download_file(frame_url)
            frames.append(frame_data)
        
        # 下载音频（如果提供）
        audio_path = None
        if request.audio_url:
            audio_data = storage.download_file(request.audio_url)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                tmp.write(audio_data)
                audio_path = tmp.name
        
        # 创建配置
        config = engine.create_project_config(
            aspect_ratio=AspectRatio(request.config.aspect_ratio),
            duration_minutes=request.config.duration_minutes,
            quality=VideoQuality(request.config.quality),
            format=VideoFormat(request.config.format)
        )
        
        # 渲染视频
        video_url = engine.render_video(
            frames=frames,
            config=config,
            audio_path=audio_path
        )
        
        # 清理临时音频文件
        if audio_path:
            Path(audio_path).unlink()
        
        # 计算渲染时间
        render_time = (datetime.now() - start_time).total_seconds()
        
        # 获取文件大小
        try:
            video_data = storage.download_file(video_url)
            file_size_mb = len(video_data) / (1024 * 1024)
        except:
            file_size_mb = 0.0
        
        return VideoRenderResponse(
            video_url=video_url,
            render_time_seconds=render_time,
            file_size_mb=file_size_mb,
            config=VideoProjectConfigResponse(**config.to_dict())
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"视频渲染失败: {str(e)}")


@router.post("/preview", response_model=VideoPreviewResponse)
async def generate_preview(
    request: VideoPreviewRequest,
    current_user: User = Depends(get_current_user)
):
    """
    生成低分辨率预览视频
    
    用于快速预览效果，无需等待完整渲染
    """
    try:
        engine = VideoRenderingEngine()
        storage = StorageService()
        
        # 下载所有分镜图像
        frames = []
        for frame_url in request.frame_urls:
            frame_data = storage.download_file(frame_url)
            frames.append(frame_data)
        
        # 下载音频（如果提供）
        audio_path = None
        if request.audio_url:
            audio_data = storage.download_file(request.audio_url)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                tmp.write(audio_data)
                audio_path = tmp.name
        
        # 创建配置
        config = engine.create_project_config(
            aspect_ratio=AspectRatio(request.config.aspect_ratio),
            duration_minutes=request.config.duration_minutes,
            quality=VideoQuality(request.config.quality),
            format=VideoFormat(request.config.format)
        )
        
        # 生成预览
        preview_data = engine.generate_preview(
            frames=frames,
            config=config,
            audio_path=audio_path
        )
        
        # 清理临时音频文件
        if audio_path:
            Path(audio_path).unlink()
        
        # 保存预览视频
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        preview_path = f"previews/preview_{timestamp}.{config.format.value}"
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{config.format.value}") as tmp:
            tmp.write(preview_data)
            tmp_path = tmp.name
        
        preview_url = storage.upload_file(tmp_path, preview_path)
        Path(tmp_path).unlink()
        
        return VideoPreviewResponse(
            preview_url=preview_url,
            duration_seconds=config.duration_minutes * 60
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"预览生成失败: {str(e)}")


@router.post("/estimate-render-time", response_model=RenderTimeEstimateResponse)
async def estimate_render_time(
    request: RenderTimeEstimateRequest,
    current_user: User = Depends(get_current_user)
):
    """
    估算视频渲染时间
    
    帮助用户了解渲染所需时间
    """
    try:
        engine = VideoRenderingEngine()
        
        # 创建配置
        config = engine.create_project_config(
            aspect_ratio=AspectRatio(request.config.aspect_ratio),
            duration_minutes=request.config.duration_minutes,
            quality=VideoQuality(request.config.quality),
            format=VideoFormat(request.config.format)
        )
        
        # 估算渲染时间
        estimated_time = engine.estimate_render_time(
            frame_count=request.frame_count,
            config=config
        )
        
        return RenderTimeEstimateResponse(
            estimated_time_minutes=estimated_time,
            frame_count=request.frame_count,
            quality=request.config.quality
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"时间估算失败: {str(e)}")


@router.post("/upload-frame")
async def upload_frame(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    上传分镜图像
    
    返回图像URL供后续渲染使用
    """
    try:
        storage = StorageService()
        
        # 读取文件
        content = await file.read()
        
        # 验证是图像文件
        try:
            Image.open(io.BytesIO(content))
        except:
            raise HTTPException(status_code=400, detail="无效的图像文件")
        
        # 保存文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"frames/frame_{timestamp}_{file.filename}"
        
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        
        file_url = storage.upload_file(tmp_path, filename)
        Path(tmp_path).unlink()
        
        return {"frame_url": file_url}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")
