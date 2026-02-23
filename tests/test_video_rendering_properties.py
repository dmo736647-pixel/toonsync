"""
视频渲染服务属性测试

使用Hypothesis进行基于属性的测试，验证视频渲染引擎的正确性属性。
"""
import io
import json
from hypothesis import given, strategies as st, settings, assume
from PIL import Image

from app.services.video_rendering import (
    VideoRenderingEngine,
    VideoProjectConfig,
    AspectRatio,
    VideoQuality,
    VideoFormat,
    CompositionOptimizer
)


# 自定义策略
aspect_ratios = st.sampled_from([
    AspectRatio.VERTICAL_9_16,
    AspectRatio.HORIZONTAL_16_9,
    AspectRatio.SQUARE_1_1
])

video_qualities = st.sampled_from([
    VideoQuality.HD_720P,
    VideoQuality.FULL_HD_1080P,
    VideoQuality.UHD_4K
])

video_formats = st.sampled_from([
    VideoFormat.MP4,
    VideoFormat.MOV
])

durations = st.floats(min_value=0.5, max_value=10.0)

image_dimensions = st.tuples(
    st.integers(min_value=100, max_value=4000),
    st.integers(min_value=100, max_value=4000)
)


class TestVideoProjectConfigProperties:
    """测试视频项目配置的属性"""
    
    @given(
        aspect_ratio=aspect_ratios,
        duration=durations,
        quality=video_qualities,
        format=video_formats
    )
    @settings(max_examples=50)
    def test_config_creation_always_succeeds(
        self,
        aspect_ratio,
        duration,
        quality,
        format
    ):
        """
        属性：对于任意有效的参数组合，配置创建应总是成功
        """
        config = VideoProjectConfig(
            aspect_ratio=aspect_ratio,
            duration_minutes=duration,
            quality=quality,
            format=format
        )
        
        assert config.aspect_ratio == aspect_ratio
        assert config.duration_minutes == duration
        assert config.quality == quality
        assert config.format == format
        assert config.resolution is not None
        assert len(config.resolution) == 2
        assert config.resolution[0] > 0
        assert config.resolution[1] > 0
    
    @given(
        aspect_ratio=aspect_ratios,
        quality=video_qualities
    )
    @settings(max_examples=50)
    def test_resolution_matches_aspect_ratio(self, aspect_ratio, quality):
        """
        属性：分辨率应始终匹配指定的画面比例
        """
        config = VideoProjectConfig(
            aspect_ratio=aspect_ratio,
            quality=quality
        )
        
        width, height = config.resolution
        actual_ratio = width / height
        
        if aspect_ratio == AspectRatio.VERTICAL_9_16:
            expected_ratio = 9 / 16
        elif aspect_ratio == AspectRatio.HORIZONTAL_16_9:
            expected_ratio = 16 / 9
        else:  # SQUARE_1_1
            expected_ratio = 1.0
        
        # 允许小误差（由于整数舍入）
        assert abs(actual_ratio - expected_ratio) < 0.02
    
    @given(
        aspect_ratio=aspect_ratios,
        duration=durations,
        quality=video_qualities,
        format=video_formats
    )
    @settings(max_examples=50)
    def test_config_serialization_roundtrip(
        self,
        aspect_ratio,
        duration,
        quality,
        format
    ):
        """
        属性：配置序列化和反序列化应保持一致
        """
        original_config = VideoProjectConfig(
            aspect_ratio=aspect_ratio,
            duration_minutes=duration,
            quality=quality,
            format=format
        )
        
        # 序列化
        data = original_config.to_dict()
        
        # 反序列化
        restored_config = VideoProjectConfig.from_dict(data)
        
        # 验证一致性
        assert restored_config.aspect_ratio == original_config.aspect_ratio
        assert restored_config.duration_minutes == original_config.duration_minutes
        assert restored_config.quality == original_config.quality
        assert restored_config.format == original_config.format
        assert restored_config.resolution == original_config.resolution
    
    @given(quality=video_qualities)
    @settings(max_examples=30)
    def test_resolution_increases_with_quality(self, quality):
        """
        属性：更高的质量应产生更高的分辨率
        """
        config = VideoProjectConfig(
            aspect_ratio=AspectRatio.VERTICAL_9_16,
            quality=quality
        )
        
        width, height = config.resolution
        total_pixels = width * height
        
        if quality == VideoQuality.HD_720P:
            assert total_pixels < 2_000_000  # 小于2M像素
        elif quality == VideoQuality.FULL_HD_1080P:
            assert 2_000_000 <= total_pixels < 8_000_000  # 2M-8M像素
        else:  # UHD_4K
            assert total_pixels >= 8_000_000  # 大于8M像素


class TestCompositionOptimizerProperties:
    """测试画面构图优化器的属性"""
    
    def create_test_image(self, width: int, height: int) -> Image.Image:
        """创建测试图像"""
        return Image.new('RGB', (width, height), color='blue')
    
    @given(
        width=st.integers(min_value=200, max_value=3000),
        height=st.integers(min_value=200, max_value=3000)
    )
    @settings(max_examples=50)
    def test_vertical_optimization_preserves_ratio(self, width, height):
        """
        **属性12：竖屏画面构图优化**
        对于任意分镜图像，当导出为9:16竖屏格式时，系统应优化画面构图和文字布局以适配竖屏观看
        
        **验证：需求3.5**
        """
        optimizer = CompositionOptimizer()
        
        # 创建任意尺寸的图像
        image = self.create_test_image(width, height)
        
        # 优化为竖屏
        optimized = optimizer.optimize_for_vertical(image)
        
        # 验证比例
        actual_ratio = optimized.width / optimized.height
        expected_ratio = 9 / 16
        
        # 比例应匹配（允许1%误差）
        assert abs(actual_ratio - expected_ratio) < 0.01
        
        # 优化后的图像应不大于原图
        assert optimized.width <= width
        assert optimized.height <= height
    
    @given(
        width=st.integers(min_value=200, max_value=3000),
        height=st.integers(min_value=200, max_value=3000)
    )
    @settings(max_examples=50)
    def test_horizontal_optimization_preserves_ratio(self, width, height):
        """
        属性：对于任意图像，横屏优化应保持16:9比例
        """
        optimizer = CompositionOptimizer()
        
        image = self.create_test_image(width, height)
        optimized = optimizer.optimize_for_horizontal(image)
        
        actual_ratio = optimized.width / optimized.height
        expected_ratio = 16 / 9
        
        assert abs(actual_ratio - expected_ratio) < 0.01
        assert optimized.width <= width
        assert optimized.height <= height
    
    @given(
        width=st.integers(min_value=200, max_value=3000),
        height=st.integers(min_value=200, max_value=3000)
    )
    @settings(max_examples=50)
    def test_square_optimization_creates_square(self, width, height):
        """
        属性：对于任意图像，方屏优化应创建正方形
        """
        optimizer = CompositionOptimizer()
        
        image = self.create_test_image(width, height)
        optimized = optimizer.optimize_for_square(image)
        
        # 应该是正方形
        assert optimized.width == optimized.height
        
        # 边长应该是原图较小的边
        expected_size = min(width, height)
        assert optimized.width == expected_size
    
    @given(
        width=st.integers(min_value=200, max_value=3000),
        height=st.integers(min_value=200, max_value=3000),
        aspect_ratio=aspect_ratios
    )
    @settings(max_examples=100)
    def test_composition_optimization_always_succeeds(
        self,
        width,
        height,
        aspect_ratio
    ):
        """
        属性：对于任意图像和目标比例，构图优化应总是成功
        """
        optimizer = CompositionOptimizer()
        
        image = self.create_test_image(width, height)
        
        # 优化应不抛出异常
        optimized = optimizer.optimize_composition(image, aspect_ratio)
        
        # 验证输出
        assert isinstance(optimized, Image.Image)
        assert optimized.width > 0
        assert optimized.height > 0
        
        # 验证比例
        actual_ratio = optimized.width / optimized.height
        
        if aspect_ratio == AspectRatio.VERTICAL_9_16:
            expected_ratio = 9 / 16
        elif aspect_ratio == AspectRatio.HORIZONTAL_16_9:
            expected_ratio = 16 / 9
        else:  # SQUARE_1_1
            expected_ratio = 1.0
        
        assert abs(actual_ratio - expected_ratio) < 0.01
    
    @given(
        width=st.integers(min_value=500, max_value=2000),
        height=st.integers(min_value=500, max_value=2000),
        text=st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
        position=st.sampled_from(["top", "center", "bottom"])
    )
    @settings(max_examples=50)
    def test_text_overlay_preserves_dimensions(
        self,
        width,
        height,
        text,
        position
    ):
        """
        属性：添加文字叠加不应改变图像尺寸
        """
        optimizer = CompositionOptimizer()
        
        image = self.create_test_image(width, height)
        image_with_text = optimizer.add_text_overlay(image, text, position=position)
        
        # 尺寸应保持不变
        assert image_with_text.width == width
        assert image_with_text.height == height


class TestVideoRenderingEngineProperties:
    """测试视频渲染引擎的属性"""
    
    @given(
        aspect_ratio=aspect_ratios,
        duration=durations,
        quality=video_qualities,
        format=video_formats
    )
    @settings(max_examples=50)
    def test_project_config_creation_always_valid(
        self,
        aspect_ratio,
        duration,
        quality,
        format
    ):
        """
        属性：对于任意有效参数，项目配置创建应总是成功
        """
        engine = VideoRenderingEngine()
        
        config = engine.create_project_config(
            aspect_ratio=aspect_ratio,
            duration_minutes=duration,
            quality=quality,
            format=format
        )
        
        assert config is not None
        assert config.aspect_ratio == aspect_ratio
        assert config.duration_minutes == duration
        assert config.quality == quality
        assert config.format == format
    
    @given(
        width=st.integers(min_value=200, max_value=2000),
        height=st.integers(min_value=200, max_value=2000),
        aspect_ratio=aspect_ratios
    )
    @settings(max_examples=100)
    def test_composition_optimization_maintains_ratio(
        self,
        width,
        height,
        aspect_ratio
    ):
        """
        属性：构图优化应始终保持目标画面比例
        """
        engine = VideoRenderingEngine()
        
        # 创建测试图像
        image = Image.new('RGB', (width, height), color='red')
        image_bytes = io.BytesIO()
        image.save(image_bytes, format='PNG')
        image_data = image_bytes.getvalue()
        
        # 优化构图
        optimized_data = engine.optimize_composition(image_data, aspect_ratio)
        
        # 验证输出
        assert isinstance(optimized_data, bytes)
        assert len(optimized_data) > 0
        
        # 验证比例
        optimized_image = Image.open(io.BytesIO(optimized_data))
        actual_ratio = optimized_image.width / optimized_image.height
        
        if aspect_ratio == AspectRatio.VERTICAL_9_16:
            expected_ratio = 9 / 16
        elif aspect_ratio == AspectRatio.HORIZONTAL_16_9:
            expected_ratio = 16 / 9
        else:  # SQUARE_1_1
            expected_ratio = 1.0
        
        assert abs(actual_ratio - expected_ratio) < 0.01
    
    @given(
        frame_count=st.integers(min_value=1, max_value=100),
        quality=video_qualities,
        duration=st.floats(min_value=0.5, max_value=3.0)
    )
    @settings(max_examples=50)
    def test_render_time_estimation_is_positive(
        self,
        frame_count,
        quality,
        duration
    ):
        """
        属性：渲染时间估算应始终返回正数
        """
        engine = VideoRenderingEngine()
        
        config = VideoProjectConfig(
            duration_minutes=duration,
            quality=quality
        )
        
        estimated_time = engine.estimate_render_time(frame_count, config)
        
        # 估算时间应为正数
        assert estimated_time > 0
        
        # 对于1-3分钟的视频，估算时间应在合理范围内（<10分钟）
        if duration <= 3.0:
            assert estimated_time < 10.0
    
    @given(
        frame_count=st.integers(min_value=5, max_value=50),
        quality=video_qualities
    )
    @settings(max_examples=30)
    def test_higher_quality_takes_longer(self, frame_count, quality):
        """
        属性：更高的质量应需要更长的渲染时间
        """
        engine = VideoRenderingEngine()
        
        config = VideoProjectConfig(
            duration_minutes=2.0,
            quality=quality
        )
        
        estimated_time = engine.estimate_render_time(frame_count, config)
        
        # 根据质量验证时间范围
        if quality == VideoQuality.HD_720P:
            # 720p应该最快
            assert estimated_time > 0
        elif quality == VideoQuality.FULL_HD_1080P:
            # 1080p应该中等
            config_720p = VideoProjectConfig(
                duration_minutes=2.0,
                quality=VideoQuality.HD_720P
            )
            time_720p = engine.estimate_render_time(frame_count, config_720p)
            assert estimated_time >= time_720p
        else:  # UHD_4K
            # 4K应该最慢
            config_1080p = VideoProjectConfig(
                duration_minutes=2.0,
                quality=VideoQuality.FULL_HD_1080P
            )
            time_1080p = engine.estimate_render_time(frame_count, config_1080p)
            assert estimated_time >= time_1080p
    
    @given(
        frame_count=st.integers(min_value=1, max_value=20)
    )
    @settings(max_examples=30)
    def test_preview_generation_succeeds(self, frame_count):
        """
        属性：对于任意数量的帧，预览生成应总是成功
        """
        engine = VideoRenderingEngine()
        
        # 创建测试帧
        frames = []
        for i in range(frame_count):
            image = Image.new('RGB', (1080, 1920), color=(i*10, 0, 0))
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
    
    @given(
        frame_count=st.integers(min_value=1, max_value=10),
        aspect_ratio=aspect_ratios,
        quality=video_qualities
    )
    @settings(max_examples=50)
    def test_video_rendering_produces_output(
        self,
        frame_count,
        aspect_ratio,
        quality
    ):
        """
        属性：对于任意有效输入，视频渲染应产生输出
        """
        engine = VideoRenderingEngine()
        
        # 创建测试帧
        frames = []
        for i in range(frame_count):
            image = Image.new('RGB', (1080, 1920), color=(0, i*20, 0))
            image_bytes = io.BytesIO()
            image.save(image_bytes, format='PNG')
            frames.append(image_bytes.getvalue())
        
        config = VideoProjectConfig(
            aspect_ratio=aspect_ratio,
            duration_minutes=1.0,
            quality=quality
        )
        
        # 渲染视频
        video_path = engine.render_video(frames, config)
        
        # 验证输出
        assert isinstance(video_path, str)
        assert len(video_path) > 0


class TestVideoRenderingPerformanceProperties:
    """测试视频渲染性能属性"""
    
    @given(
        duration=st.floats(min_value=1.0, max_value=3.0),
        frame_count=st.integers(min_value=10, max_value=50)
    )
    @settings(max_examples=30)
    def test_short_video_render_time_under_5_minutes(self, duration, frame_count):
        """
        **属性11：竖屏视频渲染性能**
        对于任意1-3分钟的微短剧项目，视频渲染时间应不超过5分钟
        
        **验证：需求9.6**
        """
        engine = VideoRenderingEngine()
        
        config = VideoProjectConfig(
            aspect_ratio=AspectRatio.VERTICAL_9_16,
            duration_minutes=duration,
            quality=VideoQuality.FULL_HD_1080P
        )
        
        # 估算渲染时间
        estimated_time = engine.estimate_render_time(frame_count, config)
        
        # 1-3分钟视频应在5分钟内完成
        assert estimated_time < 5.0, f"渲染时间 {estimated_time:.2f} 分钟超过5分钟限制"
    
    @given(
        frame_count=st.integers(min_value=1, max_value=30)
    )
    @settings(max_examples=20)
    def test_render_time_scales_with_frame_count(self, frame_count):
        """
        属性：渲染时间应随帧数线性增长
        """
        engine = VideoRenderingEngine()
        
        config = VideoProjectConfig(
            duration_minutes=2.0,
            quality=VideoQuality.FULL_HD_1080P
        )
        
        time_for_n_frames = engine.estimate_render_time(frame_count, config)
        time_for_2n_frames = engine.estimate_render_time(frame_count * 2, config)
        
        # 双倍帧数应该需要更多时间（但不一定是精确的两倍，因为有编码开销）
        assert time_for_2n_frames > time_for_n_frames
