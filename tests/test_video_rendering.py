"""
视频渲染服务单元测试
"""
import io
import json
import pytest
from PIL import Image
from datetime import datetime

from app.services.video_rendering import (
    VideoRenderingEngine,
    VideoProjectConfig,
    AspectRatio,
    VideoQuality,
    VideoFormat,
    CompositionOptimizer
)


class TestVideoProjectConfig:
    """测试视频项目配置"""
    
    def test_create_default_config(self):
        """测试创建默认配置（9:16竖屏）"""
        config = VideoProjectConfig()
        
        assert config.aspect_ratio == AspectRatio.VERTICAL_9_16
        assert config.duration_minutes == 2.0
        assert config.quality == VideoQuality.FULL_HD_1080P
        assert config.format == VideoFormat.MP4
        assert config.resolution == (1080, 1920)
    
    def test_create_horizontal_config(self):
        """测试创建横屏配置（16:9）"""
        config = VideoProjectConfig(
            aspect_ratio=AspectRatio.HORIZONTAL_16_9
        )
        
        assert config.aspect_ratio == AspectRatio.HORIZONTAL_16_9
        assert config.resolution == (1920, 1080)
    
    def test_create_square_config(self):
        """测试创建方屏配置（1:1）"""
        config = VideoProjectConfig(
            aspect_ratio=AspectRatio.SQUARE_1_1
        )
        
        assert config.aspect_ratio == AspectRatio.SQUARE_1_1
        assert config.resolution == (1080, 1080)
    
    def test_720p_resolution(self):
        """测试720p分辨率"""
        config = VideoProjectConfig(
            aspect_ratio=AspectRatio.VERTICAL_9_16,
            quality=VideoQuality.HD_720P
        )
        
        assert config.resolution == (720, 1280)
    
    def test_4k_resolution(self):
        """测试4K分辨率"""
        config = VideoProjectConfig(
            aspect_ratio=AspectRatio.VERTICAL_9_16,
            quality=VideoQuality.UHD_4K
        )
        
        assert config.resolution == (2160, 3840)
    
    def test_duration_validation(self):
        """测试时长范围"""
        # 有效时长
        config = VideoProjectConfig(duration_minutes=1.5)
        assert config.duration_minutes == 1.5
        
        # 边界值
        config = VideoProjectConfig(duration_minutes=0.5)
        assert config.duration_minutes == 0.5
        
        config = VideoProjectConfig(duration_minutes=10.0)
        assert config.duration_minutes == 10.0
    
    def test_config_to_dict(self):
        """测试配置转换为字典"""
        config = VideoProjectConfig(
            aspect_ratio=AspectRatio.VERTICAL_9_16,
            duration_minutes=2.5,
            quality=VideoQuality.FULL_HD_1080P,
            format=VideoFormat.MP4
        )
        
        data = config.to_dict()
        
        assert data["aspect_ratio"] == "9:16"
        assert data["duration_minutes"] == 2.5
        assert data["quality"] == "1080p"
        assert data["format"] == "mp4"
        assert data["resolution"]["width"] == 1080
        assert data["resolution"]["height"] == 1920
    
    def test_config_from_dict(self):
        """测试从字典创建配置"""
        data = {
            "aspect_ratio": "16:9",
            "duration_minutes": 3.0,
            "quality": "720p",
            "format": "mov"
        }
        
        config = VideoProjectConfig.from_dict(data)
        
        assert config.aspect_ratio == AspectRatio.HORIZONTAL_16_9
        assert config.duration_minutes == 3.0
        assert config.quality == VideoQuality.HD_720P
        assert config.format == VideoFormat.MOV


class TestCompositionOptimizer:
    """测试画面构图优化器"""
    
    def create_test_image(self, width: int, height: int) -> Image.Image:
        """创建测试图像"""
        return Image.new('RGB', (width, height), color='blue')
    
    def test_optimize_for_vertical_from_horizontal(self):
        """测试从横屏优化为竖屏"""
        optimizer = CompositionOptimizer()
        
        # 创建横屏图像（1920x1080）
        image = self.create_test_image(1920, 1080)
        
        # 优化为竖屏
        optimized = optimizer.optimize_for_vertical(image)
        
        # 验证比例
        ratio = optimized.width / optimized.height
        expected_ratio = 9 / 16
        assert abs(ratio - expected_ratio) < 0.01
        
        # 验证尺寸
        assert optimized.width < image.width
        assert optimized.height == image.height
    
    def test_optimize_for_vertical_from_square(self):
        """测试从方屏优化为竖屏"""
        optimizer = CompositionOptimizer()
        
        # 创建方屏图像（1080x1080）
        image = self.create_test_image(1080, 1080)
        
        # 优化为竖屏
        optimized = optimizer.optimize_for_vertical(image)
        
        # 验证比例
        ratio = optimized.width / optimized.height
        expected_ratio = 9 / 16
        assert abs(ratio - expected_ratio) < 0.01
    
    def test_optimize_for_horizontal_from_vertical(self):
        """测试从竖屏优化为横屏"""
        optimizer = CompositionOptimizer()
        
        # 创建竖屏图像（1080x1920）
        image = self.create_test_image(1080, 1920)
        
        # 优化为横屏
        optimized = optimizer.optimize_for_horizontal(image)
        
        # 验证比例
        ratio = optimized.width / optimized.height
        expected_ratio = 16 / 9
        assert abs(ratio - expected_ratio) < 0.01
        
        # 验证尺寸
        assert optimized.width == image.width
        assert optimized.height < image.height
    
    def test_optimize_for_square(self):
        """测试优化为方屏"""
        optimizer = CompositionOptimizer()
        
        # 创建横屏图像
        image = self.create_test_image(1920, 1080)
        
        # 优化为方屏
        optimized = optimizer.optimize_for_square(image)
        
        # 验证是正方形
        assert optimized.width == optimized.height
        assert optimized.width == 1080  # 取较小的边
    
    def test_optimize_composition_vertical(self):
        """测试构图优化（竖屏）"""
        optimizer = CompositionOptimizer()
        
        image = self.create_test_image(1920, 1080)
        optimized = optimizer.optimize_composition(image, AspectRatio.VERTICAL_9_16)
        
        ratio = optimized.width / optimized.height
        expected_ratio = 9 / 16
        assert abs(ratio - expected_ratio) < 0.01
    
    def test_optimize_composition_horizontal(self):
        """测试构图优化（横屏）"""
        optimizer = CompositionOptimizer()
        
        image = self.create_test_image(1080, 1920)
        optimized = optimizer.optimize_composition(image, AspectRatio.HORIZONTAL_16_9)
        
        ratio = optimized.width / optimized.height
        expected_ratio = 16 / 9
        assert abs(ratio - expected_ratio) < 0.01
    
    def test_add_text_overlay(self):
        """测试添加文字叠加"""
        optimizer = CompositionOptimizer()
        
        image = self.create_test_image(1080, 1920)
        text = "测试文字"
        
        # 添加文字（底部）
        image_with_text = optimizer.add_text_overlay(image, text, position="bottom")
        
        # 验证图像尺寸未改变
        assert image_with_text.size == image.size
        
        # 验证图像已修改（像素不完全相同）
        assert image_with_text.tobytes() != image.tobytes()
    
    def test_add_text_overlay_positions(self):
        """测试不同位置的文字叠加"""
        optimizer = CompositionOptimizer()
        
        image = self.create_test_image(1080, 1920)
        text = "测试"
        
        # 测试三个位置
        for position in ["top", "center", "bottom"]:
            image_with_text = optimizer.add_text_overlay(image, text, position=position)
            assert image_with_text.size == image.size


class TestVideoRenderingEngine:
    """测试视频渲染引擎"""
    
    def test_singleton_pattern(self):
        """测试单例模式"""
        engine1 = VideoRenderingEngine()
        engine2 = VideoRenderingEngine()
        
        assert engine1 is engine2
    
    def test_create_project_config(self):
        """测试创建项目配置"""
        engine = VideoRenderingEngine()
        
        config = engine.create_project_config(
            aspect_ratio=AspectRatio.VERTICAL_9_16,
            duration_minutes=2.0,
            quality=VideoQuality.FULL_HD_1080P,
            format=VideoFormat.MP4
        )
        
        assert config.aspect_ratio == AspectRatio.VERTICAL_9_16
        assert config.duration_minutes == 2.0
        assert config.quality == VideoQuality.FULL_HD_1080P
        assert config.format == VideoFormat.MP4
    
    def test_create_project_config_invalid_duration(self):
        """测试创建配置时验证时长"""
        engine = VideoRenderingEngine()
        
        # 时长太短
        with pytest.raises(ValueError, match="视频时长应在"):
            engine.create_project_config(duration_minutes=0.1)
        
        # 时长太长
        with pytest.raises(ValueError, match="视频时长应在"):
            engine.create_project_config(duration_minutes=15.0)
    
    def test_optimize_composition(self):
        """测试优化构图"""
        engine = VideoRenderingEngine()
        
        # 创建测试图像
        image = Image.new('RGB', (1920, 1080), color='red')
        image_bytes = io.BytesIO()
        image.save(image_bytes, format='PNG')
        image_data = image_bytes.getvalue()
        
        # 优化为竖屏
        optimized_data = engine.optimize_composition(
            image_data,
            AspectRatio.VERTICAL_9_16
        )
        
        # 验证输出
        assert isinstance(optimized_data, bytes)
        assert len(optimized_data) > 0
        
        # 验证是有效图像
        optimized_image = Image.open(io.BytesIO(optimized_data))
        ratio = optimized_image.width / optimized_image.height
        expected_ratio = 9 / 16
        assert abs(ratio - expected_ratio) < 0.01
    
    def test_estimate_render_time(self):
        """测试估算渲染时间"""
        engine = VideoRenderingEngine()
        
        config = VideoProjectConfig(
            aspect_ratio=AspectRatio.VERTICAL_9_16,
            duration_minutes=2.0,
            quality=VideoQuality.FULL_HD_1080P
        )
        
        # 估算10帧的渲染时间
        estimated_time = engine.estimate_render_time(10, config)
        
        # 验证返回值
        assert isinstance(estimated_time, float)
        assert estimated_time > 0
        
        # 1-3分钟视频应在5分钟内完成
        assert estimated_time < 5.0
    
    def test_estimate_render_time_quality_impact(self):
        """测试不同质量对渲染时间的影响"""
        engine = VideoRenderingEngine()
        
        frame_count = 20
        
        # 720p
        config_720p = VideoProjectConfig(quality=VideoQuality.HD_720P)
        time_720p = engine.estimate_render_time(frame_count, config_720p)
        
        # 1080p
        config_1080p = VideoProjectConfig(quality=VideoQuality.FULL_HD_1080P)
        time_1080p = engine.estimate_render_time(frame_count, config_1080p)
        
        # 4K
        config_4k = VideoProjectConfig(quality=VideoQuality.UHD_4K)
        time_4k = engine.estimate_render_time(frame_count, config_4k)
        
        # 验证质量越高，时间越长
        assert time_720p < time_1080p < time_4k
    
    def test_generate_preview(self):
        """测试生成预览视频"""
        engine = VideoRenderingEngine()
        
        # 创建测试帧
        frames = []
        for i in range(3):
            image = Image.new('RGB', (1080, 1920), color=(i*80, 0, 0))
            image_bytes = io.BytesIO()
            image.save(image_bytes, format='PNG')
            frames.append(image_bytes.getvalue())
        
        config = VideoProjectConfig(
            aspect_ratio=AspectRatio.VERTICAL_9_16,
            duration_minutes=1.0
        )
        
        # 生成预览
        preview_data = engine.generate_preview(frames, config)
        
        # 验证输出
        assert isinstance(preview_data, bytes)
        assert len(preview_data) > 0
    
    def test_render_video_mock(self):
        """测试渲染视频（模拟模式）"""
        engine = VideoRenderingEngine()
        
        # 创建测试帧
        frames = []
        for i in range(5):
            image = Image.new('RGB', (1080, 1920), color=(0, i*50, 0))
            image_bytes = io.BytesIO()
            image.save(image_bytes, format='PNG')
            frames.append(image_bytes.getvalue())
        
        config = VideoProjectConfig(
            aspect_ratio=AspectRatio.VERTICAL_9_16,
            duration_minutes=1.0,
            quality=VideoQuality.HD_720P
        )
        
        # 渲染视频（会使用模拟模式，因为FFmpeg可能未安装）
        video_path = engine.render_video(frames, config)
        
        # 验证输出
        assert isinstance(video_path, str)
        assert len(video_path) > 0
    
    def test_render_video_empty_frames(self):
        """测试渲染空帧列表"""
        engine = VideoRenderingEngine()
        
        config = VideoProjectConfig()
        
        with pytest.raises(ValueError, match="至少需要一个分镜图像"):
            engine.render_video([], config)
    
    def test_create_mock_video(self):
        """测试创建模拟视频"""
        engine = VideoRenderingEngine()
        
        frames = [b"frame1", b"frame2"]
        config = VideoProjectConfig()
        
        mock_data = engine._create_mock_video(frames, config)
        
        # 验证是有效的JSON
        data = json.loads(mock_data.decode('utf-8'))
        assert data["type"] == "mock_video"
        assert data["frame_count"] == 2
        assert "config" in data
        assert "created_at" in data


class TestVideoRenderingIntegration:
    """集成测试"""
    
    def test_full_workflow(self):
        """测试完整工作流"""
        engine = VideoRenderingEngine()
        
        # 1. 创建配置
        config = engine.create_project_config(
            aspect_ratio=AspectRatio.VERTICAL_9_16,
            duration_minutes=1.5,
            quality=VideoQuality.HD_720P
        )
        
        assert config.aspect_ratio == AspectRatio.VERTICAL_9_16
        
        # 2. 创建并优化帧
        frames = []
        for i in range(3):
            # 创建横屏图像
            image = Image.new('RGB', (1920, 1080), color=(i*80, i*80, i*80))
            image_bytes = io.BytesIO()
            image.save(image_bytes, format='PNG')
            
            # 优化为竖屏
            optimized_data = engine.optimize_composition(
                image_bytes.getvalue(),
                AspectRatio.VERTICAL_9_16
            )
            frames.append(optimized_data)
        
        # 3. 估算渲染时间
        estimated_time = engine.estimate_render_time(len(frames), config)
        assert estimated_time > 0
        assert estimated_time < 5.0  # 应在5分钟内
        
        # 4. 生成预览
        preview_data = engine.generate_preview(frames, config)
        assert len(preview_data) > 0
        
        # 5. 渲染最终视频
        video_path = engine.render_video(frames, config)
        assert len(video_path) > 0
    
    def test_different_aspect_ratios(self):
        """测试不同画面比例"""
        engine = VideoRenderingEngine()
        
        # 创建测试图像
        image = Image.new('RGB', (1920, 1080), color='green')
        image_bytes = io.BytesIO()
        image.save(image_bytes, format='PNG')
        image_data = image_bytes.getvalue()
        
        # 测试三种比例
        for aspect_ratio in [AspectRatio.VERTICAL_9_16, AspectRatio.HORIZONTAL_16_9, AspectRatio.SQUARE_1_1]:
            optimized_data = engine.optimize_composition(image_data, aspect_ratio)
            optimized_image = Image.open(io.BytesIO(optimized_data))
            
            # 验证比例
            if aspect_ratio == AspectRatio.VERTICAL_9_16:
                expected_ratio = 9 / 16
            elif aspect_ratio == AspectRatio.HORIZONTAL_16_9:
                expected_ratio = 16 / 9
            else:  # SQUARE_1_1
                expected_ratio = 1.0
            
            actual_ratio = optimized_image.width / optimized_image.height
            assert abs(actual_ratio - expected_ratio) < 0.01
