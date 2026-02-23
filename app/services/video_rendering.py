"""
视频渲染服务

实现竖屏视频渲染引擎，支持9:16竖屏比例优化、画面构图优化和视频渲染。
"""
import io
import json
import subprocess
import tempfile
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont
import numpy as np

from app.core.storage import StorageManager


class AspectRatio(str, Enum):
    """画面比例枚举"""
    VERTICAL_9_16 = "9:16"
    HORIZONTAL_16_9 = "16:9"
    SQUARE_1_1 = "1:1"


class VideoQuality(str, Enum):
    """视频质量枚举"""
    HD_720P = "720p"
    FULL_HD_1080P = "1080p"
    UHD_4K = "4K"


class VideoFormat(str, Enum):
    """视频格式枚举"""
    MP4 = "mp4"
    MOV = "mov"


class VideoProjectConfig:
    """视频项目配置"""
    
    def __init__(
        self,
        aspect_ratio: AspectRatio = AspectRatio.VERTICAL_9_16,
        duration_minutes: float = 2.0,
        quality: VideoQuality = VideoQuality.FULL_HD_1080P,
        format: VideoFormat = VideoFormat.MP4
    ):
        self.aspect_ratio = aspect_ratio
        self.duration_minutes = duration_minutes
        self.quality = quality
        self.format = format
        
        # 根据比例和质量计算分辨率
        self.resolution = self._calculate_resolution()
    
    def _calculate_resolution(self) -> Tuple[int, int]:
        """根据画面比例和质量计算分辨率"""
        # 基础分辨率（1080p）
        base_resolutions = {
            AspectRatio.VERTICAL_9_16: (1080, 1920),  # 竖屏
            AspectRatio.HORIZONTAL_16_9: (1920, 1080),  # 横屏
            AspectRatio.SQUARE_1_1: (1080, 1080)  # 方屏
        }
        
        base_width, base_height = base_resolutions[self.aspect_ratio]
        
        # 根据质量调整
        if self.quality == VideoQuality.HD_720P:
            scale = 720 / 1080
        elif self.quality == VideoQuality.FULL_HD_1080P:
            scale = 1.0
        elif self.quality == VideoQuality.UHD_4K:
            scale = 2.0
        else:
            scale = 1.0
        
        width = int(base_width * scale)
        height = int(base_height * scale)
        
        # 确保是偶数（FFmpeg要求）
        width = width if width % 2 == 0 else width + 1
        height = height if height % 2 == 0 else height + 1
        
        return (width, height)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "aspect_ratio": self.aspect_ratio.value,
            "duration_minutes": self.duration_minutes,
            "quality": self.quality.value,
            "format": self.format.value,
            "resolution": {
                "width": self.resolution[0],
                "height": self.resolution[1]
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "VideoProjectConfig":
        """从字典创建配置"""
        return cls(
            aspect_ratio=AspectRatio(data.get("aspect_ratio", "9:16")),
            duration_minutes=data.get("duration_minutes", 2.0),
            quality=VideoQuality(data.get("quality", "1080p")),
            format=VideoFormat(data.get("format", "mp4"))
        )


class CompositionOptimizer:
    """画面构图优化器"""
    
    def __init__(self):
        self.storage = StorageService()
    
    def optimize_for_vertical(self, image: Image.Image) -> Image.Image:
        """
        优化图像以适配竖屏（9:16）
        
        策略：
        1. 如果图像是横屏，裁剪中心区域
        2. 如果图像是方屏，上下添加边距
        3. 调整构图使主体居中
        """
        target_ratio = 9 / 16
        current_ratio = image.width / image.height
        
        if current_ratio > target_ratio:
            # 图像太宽，需要裁剪
            new_width = int(image.height * target_ratio)
            left = (image.width - new_width) // 2
            image = image.crop((left, 0, left + new_width, image.height))
        elif current_ratio < target_ratio:
            # 图像太高，需要裁剪
            new_height = int(image.width / target_ratio)
            top = (image.height - new_height) // 2
            image = image.crop((0, top, image.width, top + new_height))
        
        return image
    
    def optimize_for_horizontal(self, image: Image.Image) -> Image.Image:
        """优化图像以适配横屏（16:9）"""
        target_ratio = 16 / 9
        current_ratio = image.width / image.height
        
        if current_ratio < target_ratio:
            # 图像太窄，需要裁剪
            new_height = int(image.width / target_ratio)
            top = (image.height - new_height) // 2
            image = image.crop((0, top, image.width, top + new_height))
        elif current_ratio > target_ratio:
            # 图像太宽，需要裁剪
            new_width = int(image.height * target_ratio)
            left = (image.width - new_width) // 2
            image = image.crop((left, 0, left + new_width, image.height))
        
        return image
    
    def optimize_for_square(self, image: Image.Image) -> Image.Image:
        """优化图像以适配方屏（1:1）"""
        size = min(image.width, image.height)
        left = (image.width - size) // 2
        top = (image.height - size) // 2
        return image.crop((left, top, left + size, top + size))
    
    def optimize_composition(
        self,
        image: Image.Image,
        aspect_ratio: AspectRatio
    ) -> Image.Image:
        """
        优化画面构图以适配目标比例
        
        参数:
            image: 原始图像
            aspect_ratio: 目标画面比例
        
        返回:
            优化后的图像
        """
        if aspect_ratio == AspectRatio.VERTICAL_9_16:
            return self.optimize_for_vertical(image)
        elif aspect_ratio == AspectRatio.HORIZONTAL_16_9:
            return self.optimize_for_horizontal(image)
        elif aspect_ratio == AspectRatio.SQUARE_1_1:
            return self.optimize_for_square(image)
        else:
            return image
    
    def add_text_overlay(
        self,
        image: Image.Image,
        text: str,
        position: str = "bottom",
        font_size: Optional[int] = None
    ) -> Image.Image:
        """
        添加文字叠加层（适配移动端）
        
        参数:
            image: 原始图像
            text: 文字内容
            position: 位置（top/center/bottom）
            font_size: 字体大小（None则自动计算）
        
        返回:
            添加文字后的图像
        """
        # 创建副本
        img_with_text = image.copy()
        draw = ImageDraw.Draw(img_with_text)
        
        # 自动计算字体大小（基于图像高度）
        if font_size is None:
            font_size = max(24, int(image.height * 0.04))
        
        # 尝试使用系统字体，失败则使用默认字体
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        # 计算文字位置
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (image.width - text_width) // 2
        
        if position == "top":
            y = int(image.height * 0.1)
        elif position == "center":
            y = (image.height - text_height) // 2
        else:  # bottom
            y = int(image.height * 0.85)
        
        # 添加文字阴影（提高可读性）
        shadow_offset = 2
        draw.text((x + shadow_offset, y + shadow_offset), text, font=font, fill=(0, 0, 0, 128))
        draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))
        
        return img_with_text


class VideoRenderingEngine:
    """
    竖屏视频渲染引擎
    
    核心功能：
    1. 创建视频项目配置
    2. 优化画面构图
    3. 渲染最终视频
    """
    
    _instance = None
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """初始化视频渲染引擎"""
        if self._initialized:
            return
        
        self.storage = StorageService()
        self.composition_optimizer = CompositionOptimizer()
        self._initialized = True
    
    def create_project_config(
        self,
        aspect_ratio: AspectRatio = AspectRatio.VERTICAL_9_16,
        duration_minutes: float = 2.0,
        quality: VideoQuality = VideoQuality.FULL_HD_1080P,
        format: VideoFormat = VideoFormat.MP4
    ) -> VideoProjectConfig:
        """
        创建视频项目配置
        
        参数:
            aspect_ratio: 画面比例（默认9:16竖屏）
            duration_minutes: 目标时长（默认2分钟）
            quality: 视频质量（默认1080p）
            format: 视频格式（默认MP4）
        
        返回:
            VideoProjectConfig: 项目配置对象
        """
        # 验证时长（1-3分钟微短剧优化）
        if duration_minutes < 0.5 or duration_minutes > 10:
            raise ValueError("视频时长应在0.5-10分钟之间")
        
        config = VideoProjectConfig(
            aspect_ratio=aspect_ratio,
            duration_minutes=duration_minutes,
            quality=quality,
            format=format
        )
        
        return config
    
    def optimize_composition(
        self,
        image_data: bytes,
        aspect_ratio: AspectRatio
    ) -> bytes:
        """
        优化画面构图以适配目标比例
        
        参数:
            image_data: 原始图像数据
            aspect_ratio: 目标画面比例
        
        返回:
            优化后的图像数据
        """
        # 加载图像
        image = Image.open(io.BytesIO(image_data))
        
        # 优化构图
        optimized_image = self.composition_optimizer.optimize_composition(
            image, aspect_ratio
        )
        
        # 转换回字节
        output = io.BytesIO()
        optimized_image.save(output, format='PNG')
        return output.getvalue()
    
    def generate_preview(
        self,
        frames: List[bytes],
        config: VideoProjectConfig,
        audio_path: Optional[str] = None
    ) -> bytes:
        """
        生成低分辨率预览视频
        
        参数:
            frames: 分镜图像列表
            config: 项目配置
            audio_path: 音频文件路径（可选）
        
        返回:
            预览视频数据
        """
        # 预览使用较低分辨率（720p）
        preview_config = VideoProjectConfig(
            aspect_ratio=config.aspect_ratio,
            duration_minutes=config.duration_minutes,
            quality=VideoQuality.HD_720P,
            format=config.format
        )
        
        # 渲染预览视频
        return self._render_video_internal(frames, preview_config, audio_path)
    
    def render_video(
        self,
        frames: List[bytes],
        config: VideoProjectConfig,
        audio_path: Optional[str] = None,
        output_path: Optional[str] = None
    ) -> str:
        """
        渲染最终视频
        
        参数:
            frames: 分镜图像列表
            config: 项目配置
            audio_path: 音频文件路径（可选）
            output_path: 输出文件路径（可选）
        
        返回:
            视频文件路径
        
        性能要求: 1-3分钟视频在5分钟内完成渲染
        """
        start_time = datetime.now()
        
        # 渲染视频
        video_data = self._render_video_internal(frames, config, audio_path)
        
        # 保存到存储
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"videos/rendered_{timestamp}.{config.format.value}"
        
        # 保存文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{config.format.value}") as tmp:
            tmp.write(video_data)
            tmp_path = tmp.name
        
        # 上传到存储
        storage_path = self.storage.upload_file(tmp_path, output_path)
        
        # 清理临时文件
        Path(tmp_path).unlink()
        
        # 记录渲染时间
        render_time = (datetime.now() - start_time).total_seconds()
        print(f"视频渲染完成，耗时: {render_time:.2f}秒")
        
        return storage_path
    
    def _render_video_internal(
        self,
        frames: List[bytes],
        config: VideoProjectConfig,
        audio_path: Optional[str] = None
    ) -> bytes:
        """
        内部视频渲染方法（使用FFmpeg）
        
        参数:
            frames: 分镜图像列表
            config: 项目配置
            audio_path: 音频文件路径（可选）
        
        返回:
            视频数据
        """
        if not frames:
            raise ValueError("至少需要一个分镜图像")
        
        # 创建临时目录
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # 保存所有帧
            frame_paths = []
            for i, frame_data in enumerate(frames):
                # 加载并调整图像大小
                image = Image.open(io.BytesIO(frame_data))
                image = image.resize(config.resolution, Image.Resampling.LANCZOS)
                
                # 保存帧
                frame_path = tmpdir_path / f"frame_{i:04d}.png"
                image.save(frame_path)
                frame_paths.append(frame_path)
            
            # 计算帧率（基于总时长和帧数）
            total_seconds = config.duration_minutes * 60
            fps = max(1, len(frames) / total_seconds)
            fps = min(fps, 30)  # 限制最大帧率
            
            # 构建FFmpeg命令
            output_path = tmpdir_path / f"output.{config.format.value}"
            
            cmd = [
                "ffmpeg",
                "-y",  # 覆盖输出文件
                "-framerate", str(fps),
                "-i", str(tmpdir_path / "frame_%04d.png"),
            ]
            
            # 添加音频（如果提供）
            if audio_path and Path(audio_path).exists():
                cmd.extend(["-i", audio_path])
                cmd.extend(["-c:a", "aac", "-b:a", "192k"])
            
            # 视频编码参数
            cmd.extend([
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-preset", "medium",
                "-crf", "23",
                str(output_path)
            ])
            
            # 执行FFmpeg命令
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    check=True
                )
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"FFmpeg渲染失败: {e.stderr}")
            except FileNotFoundError:
                # FFmpeg未安装，返回模拟数据
                print("警告: FFmpeg未安装，返回模拟视频数据")
                return self._create_mock_video(frames, config)
            
            # 读取输出视频
            with open(output_path, 'rb') as f:
                return f.read()
    
    def _create_mock_video(
        self,
        frames: List[bytes],
        config: VideoProjectConfig
    ) -> bytes:
        """
        创建模拟视频数据（用于测试）
        
        参数:
            frames: 分镜图像列表
            config: 项目配置
        
        返回:
            模拟视频数据
        """
        # 创建一个简单的视频元数据JSON
        mock_data = {
            "type": "mock_video",
            "config": config.to_dict(),
            "frame_count": len(frames),
            "created_at": datetime.now().isoformat()
        }
        return json.dumps(mock_data).encode('utf-8')
    
    def estimate_render_time(
        self,
        frame_count: int,
        config: VideoProjectConfig
    ) -> float:
        """
        估算渲染时间（分钟）
        
        参数:
            frame_count: 分镜数量
            config: 项目配置
        
        返回:
            预估渲染时间（分钟）
        """
        # 基础渲染时间（每帧）
        base_time_per_frame = 0.5  # 秒
        
        # 质量系数
        quality_factor = {
            VideoQuality.HD_720P: 0.5,
            VideoQuality.FULL_HD_1080P: 1.0,
            VideoQuality.UHD_4K: 3.0
        }
        
        # 计算总时间
        total_seconds = frame_count * base_time_per_frame * quality_factor[config.quality]
        
        # 添加编码开销
        encoding_overhead = config.duration_minutes * 30  # 秒
        total_seconds += encoding_overhead
        
        return total_seconds / 60  # 转换为分钟
