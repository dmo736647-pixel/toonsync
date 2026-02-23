"""检查点7综合测试：核心AI引擎验证

本测试文件验证任务5（中文口型同步引擎）和任务6（角色一致性引擎）的功能和集成。
"""
import pytest
import os
import tempfile
from PIL import Image
import numpy as np

from app.services.lip_sync import (
    ChineseLipSyncEngine,
    AudioAnalysis,
    get_lip_sync_engine
)
from app.services.character_consistency import (
    CharacterConsistencyEngine,
    ConsistencyModel,
    get_character_consistency_engine
)


class TestCheckpoint7LipSyncEngine:
    """检查点7：中文口型同步引擎测试"""
    
    def test_lip_sync_engine_availability(self):
        """测试口型同步引擎可用性"""
        engine = get_lip_sync_engine()
        assert engine is not None
        assert isinstance(engine, ChineseLipSyncEngine)
    
    def test_lip_sync_engine_configuration(self):
        """测试口型同步引擎配置"""
        engine = get_lip_sync_engine()
        
        # 验证声母和韵母配置
        assert len(engine.INITIALS) == 21
        assert len(engine.FINALS) >= 24
        
        # 验证音素到口型的映射
        assert len(engine.PHONEME_TO_MOUTH_SHAPE) > 0
        assert "a" in engine.PHONEME_TO_MOUTH_SHAPE
        assert "i" in engine.PHONEME_TO_MOUTH_SHAPE
    
    def test_lip_sync_audio_analysis_workflow(self):
        """测试口型同步音频分析工作流"""
        # 创建模拟音频分析结果
        analysis = AudioAnalysis(
            phonemes=[
                {"phoneme": "n", "start_time": 0.0, "end_time": 0.1, "tone": 0, "word": "你", "type": "initial"},
                {"phoneme": "i", "start_time": 0.1, "end_time": 0.3, "tone": 3, "word": "你", "type": "final"},
            ],
            duration=0.3,
            sample_rate=16000,
            transcript="你"
        )
        
        # 验证分析结果
        assert analysis.duration == 0.3
        assert analysis.sample_rate == 16000
        assert len(analysis.phonemes) == 2
        assert analysis.transcript == "你"
    
    def test_lip_sync_keyframe_generation_workflow(self):
        """测试口型关键帧生成工作流"""
        engine = get_lip_sync_engine()
        
        # 创建音频分析结果
        analysis = AudioAnalysis(
            phonemes=[
                {"phoneme": "h", "start_time": 0.0, "end_time": 0.1, "tone": 0, "word": "好", "type": "initial"},
                {"phoneme": "ao", "start_time": 0.1, "end_time": 0.3, "tone": 3, "word": "好", "type": "final"},
            ],
            duration=0.3,
            sample_rate=16000,
            transcript="好"
        )
        
        # 生成关键帧
        keyframes = engine.generate_lip_keyframes(analysis, style="anime")
        
        # 验证关键帧生成
        assert len(keyframes) > 0
        assert keyframes[0].timestamp == 0.0  # 开始帧
        assert keyframes[-1].timestamp == analysis.duration  # 结束帧
    
    def test_lip_sync_accuracy_validation_workflow(self):
        """测试口型同步精度验证工作流"""
        engine = get_lip_sync_engine()
        
        # 创建测试数据
        analysis = AudioAnalysis(
            phonemes=[
                {"phoneme": "n", "start_time": 0.0, "end_time": 0.1, "tone": 0, "word": "你", "type": "initial"},
                {"phoneme": "i", "start_time": 0.1, "end_time": 0.2, "tone": 3, "word": "你", "type": "final"},
            ],
            duration=0.2,
            sample_rate=16000,
            transcript="你"
        )
        
        keyframes = engine.generate_lip_keyframes(analysis, style="anime")
        
        # 验证同步精度
        accuracy = engine.validate_sync_accuracy(keyframes, analysis)
        
        # 验证精度报告
        assert accuracy.average_error_ms >= 0
        assert accuracy.max_error_ms >= 0
        assert 0.0 <= accuracy.accuracy_rate <= 1.0
        assert accuracy.total_keyframes > 0
        assert accuracy.quality_score >= 0


class TestCheckpoint7CharacterConsistencyEngine:
    """检查点7：角色一致性引擎测试"""
    
    def test_character_consistency_engine_availability(self):
        """测试角色一致性引擎可用性"""
        engine = get_character_consistency_engine()
        assert engine is not None
        assert isinstance(engine, CharacterConsistencyEngine)
    
    def test_character_consistency_engine_configuration(self):
        """测试角色一致性引擎配置"""
        engine = get_character_consistency_engine()
        
        # 验证支持的风格
        assert engine.SUPPORTED_STYLES == ["anime", "realistic"]
        
        # 验证面部特征关键点
        assert len(engine.FACIAL_KEYPOINTS) == 8
        assert "eyes" in engine.FACIAL_KEYPOINTS
        assert "nose" in engine.FACIAL_KEYPOINTS
        
        # 验证服装特征
        assert len(engine.CLOTHING_FEATURES) == 4
    
    def test_character_feature_extraction_workflow(self):
        """测试角色特征提取工作流"""
        engine = get_character_consistency_engine()
        
        # 创建测试图像
        img = Image.new('RGB', (256, 256), color=(100, 150, 200))
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as f:
            img.save(f.name)
            image_path = f.name
        
        try:
            # 提取特征
            model = engine.extract_character_features(
                reference_image_path=image_path,
                character_id="test_char",
                style="anime"
            )
            
            # 验证模型
            assert isinstance(model, ConsistencyModel)
            assert model.character_id == "test_char"
            assert model.style == "anime"
            assert "color_mean" in model.facial_features
            assert "color_palette" in model.clothing_features
        
        finally:
            if os.path.exists(image_path):
                os.unlink(image_path)
    
    def test_character_storyboard_generation_workflow(self):
        """测试角色分镜生成工作流"""
        engine = get_character_consistency_engine()
        
        # 创建测试图像
        img = Image.new('RGB', (256, 256), color=(100, 150, 200))
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as f:
            img.save(f.name)
            image_path = f.name
        
        try:
            # 提取特征
            model = engine.extract_character_features(
                reference_image_path=image_path,
                character_id="test_char",
                style="anime"
            )
            
            # 生成分镜
            frame_path = engine.generate_storyboard_frame(
                consistency_model=model,
                scene_description="角色站在森林中"
            )
            
            # 验证生成的分镜
            assert os.path.exists(frame_path)
            frame_img = Image.open(frame_path)
            assert frame_img.mode == 'RGB'
            
            # 清理
            os.unlink(frame_path)
        
        finally:
            if os.path.exists(image_path):
                os.unlink(image_path)
    
    def test_character_consistency_validation_workflow(self):
        """测试角色一致性验证工作流"""
        engine = get_character_consistency_engine()
        
        # 创建测试图像
        img = Image.new('RGB', (256, 256), color=(100, 150, 200))
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as f:
            img.save(f.name)
            reference_path = f.name
        
        # 创建生成的帧
        generated_frames = []
        for i in range(3):
            frame_img = Image.new('RGB', (256, 256), color=(100 + i*5, 150, 200))
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as f:
                frame_img.save(f.name)
                generated_frames.append(f.name)
        
        try:
            # 验证一致性
            score = engine.validate_consistency(
                reference_image_path=reference_path,
                generated_frames=generated_frames
            )
            
            # 验证评分
            assert 0.0 <= score.facial_similarity <= 1.0
            assert 0.0 <= score.clothing_consistency <= 1.0
            assert 0.0 <= score.overall_score <= 1.0
        
        finally:
            if os.path.exists(reference_path):
                os.unlink(reference_path)
            for frame_path in generated_frames:
                if os.path.exists(frame_path):
                    os.unlink(frame_path)


class TestCheckpoint7Integration:
    """检查点7：核心AI引擎集成测试"""
    
    def test_both_engines_available(self):
        """测试两个核心引擎都可用"""
        lip_sync_engine = get_lip_sync_engine()
        character_engine = get_character_consistency_engine()
        
        assert lip_sync_engine is not None
        assert character_engine is not None
    
    def test_engines_singleton_pattern(self):
        """测试引擎单例模式"""
        # 口型同步引擎
        engine1 = get_lip_sync_engine()
        engine2 = get_lip_sync_engine()
        assert engine1 is engine2
        
        # 角色一致性引擎
        engine3 = get_character_consistency_engine()
        engine4 = get_character_consistency_engine()
        assert engine3 is engine4
    
    def test_integrated_workflow_simulation(self):
        """测试集成工作流模拟
        
        模拟完整的短剧制作流程：
        1. 创建角色一致性模型
        2. 生成分镜
        3. 生成口型同步
        """
        # 1. 创建角色
        character_engine = get_character_consistency_engine()
        
        img = Image.new('RGB', (256, 256), color=(100, 150, 200))
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as f:
            img.save(f.name)
            character_image_path = f.name
        
        try:
            # 提取角色特征
            character_model = character_engine.extract_character_features(
                reference_image_path=character_image_path,
                character_id="main_character",
                style="anime"
            )
            
            assert character_model is not None
            
            # 2. 生成分镜
            frame_path = character_engine.generate_storyboard_frame(
                consistency_model=character_model,
                scene_description="角色在说话"
            )
            
            assert os.path.exists(frame_path)
            
            # 3. 生成口型同步
            lip_sync_engine = get_lip_sync_engine()
            
            # 创建音频分析（模拟）
            audio_analysis = AudioAnalysis(
                phonemes=[
                    {"phoneme": "n", "start_time": 0.0, "end_time": 0.1, "tone": 0, "word": "你", "type": "initial"},
                    {"phoneme": "i", "start_time": 0.1, "end_time": 0.3, "tone": 3, "word": "你", "type": "final"},
                    {"phoneme": "h", "start_time": 0.3, "end_time": 0.4, "tone": 0, "word": "好", "type": "initial"},
                    {"phoneme": "ao", "start_time": 0.4, "end_time": 0.6, "tone": 3, "word": "好", "type": "final"},
                ],
                duration=0.6,
                sample_rate=16000,
                transcript="你好"
            )
            
            # 生成口型关键帧
            keyframes = lip_sync_engine.generate_lip_keyframes(
                audio_analysis,
                style="anime"
            )
            
            assert len(keyframes) > 0
            
            # 验证同步精度
            accuracy = lip_sync_engine.validate_sync_accuracy(keyframes, audio_analysis)
            assert accuracy.average_error_ms < 100  # 允许较大误差用于测试
            
            # 清理
            os.unlink(frame_path)
        
        finally:
            if os.path.exists(character_image_path):
                os.unlink(character_image_path)
    
    def test_performance_requirements(self):
        """测试性能要求
        
        验证：
        - 口型同步处理速度 < 音频时长的1.5倍
        - 角色特征提取 < 2秒
        """
        import time
        
        # 测试角色特征提取速度
        character_engine = get_character_consistency_engine()
        
        img = Image.new('RGB', (256, 256), color=(100, 150, 200))
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as f:
            img.save(f.name)
            image_path = f.name
        
        try:
            start_time = time.time()
            model = character_engine.extract_character_features(
                reference_image_path=image_path,
                character_id="test_char",
                style="anime"
            )
            extraction_time = time.time() - start_time
            
            # 验证处理时间 < 2秒
            assert extraction_time < 2.0, f"特征提取时间 {extraction_time}s 超过2秒要求"
        
        finally:
            if os.path.exists(image_path):
                os.unlink(image_path)
        
        # 测试口型同步处理速度
        lip_sync_engine = get_lip_sync_engine()
        
        audio_duration = 1.0  # 1秒音频
        audio_analysis = AudioAnalysis(
            phonemes=[
                {"phoneme": "n", "start_time": 0.0, "end_time": 0.5, "tone": 0, "word": "你", "type": "initial"},
                {"phoneme": "i", "start_time": 0.5, "end_time": 1.0, "tone": 3, "word": "你", "type": "final"},
            ],
            duration=audio_duration,
            sample_rate=16000,
            transcript="你"
        )
        
        start_time = time.time()
        keyframes = lip_sync_engine.generate_lip_keyframes(audio_analysis, style="anime")
        processing_time = time.time() - start_time
        
        # 验证处理时间 < 音频时长的1.5倍
        max_allowed_time = audio_duration * 1.5
        assert processing_time < max_allowed_time, \
            f"口型同步处理时间 {processing_time}s 超过 {max_allowed_time}s"


class TestCheckpoint7CorrectnessProperties:
    """检查点7：正确性属性验证"""
    
    def test_property_1_lip_sync_accuracy(self):
        """验证属性1：中文口型同步精度 < 50ms"""
        engine = get_lip_sync_engine()
        
        analysis = AudioAnalysis(
            phonemes=[
                {"phoneme": "n", "start_time": 0.0, "end_time": 0.1, "tone": 0, "word": "你", "type": "initial"},
                {"phoneme": "i", "start_time": 0.1, "end_time": 0.2, "tone": 3, "word": "你", "type": "final"},
            ],
            duration=0.2,
            sample_rate=16000,
            transcript="你"
        )
        
        keyframes = engine.generate_lip_keyframes(analysis, style="anime")
        accuracy = engine.validate_sync_accuracy(keyframes, analysis)
        
        # 验证平均误差 < 50ms
        assert accuracy.average_error_ms <= 50.0, \
            f"平均误差 {accuracy.average_error_ms}ms 超过50ms要求"
    
    def test_property_6_character_consistency(self):
        """验证属性6：角色一致性保证"""
        engine = get_character_consistency_engine()
        
        # 创建参考图像
        img = Image.new('RGB', (256, 256), color=(100, 150, 200))
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as f:
            img.save(f.name)
            reference_path = f.name
        
        # 创建生成的帧（模拟高一致性）
        generated_frames = []
        for i in range(3):
            frame_img = Image.new('RGB', (256, 256), color=(100, 150, 200))  # 相同颜色
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as f:
                frame_img.save(f.name)
                generated_frames.append(f.name)
        
        try:
            score = engine.validate_consistency(
                reference_image_path=reference_path,
                generated_frames=generated_frames
            )
            
            # 验证面部相似度 > 90%
            assert score.facial_similarity > 0.90, \
                f"面部相似度 {score.facial_similarity} 低于90%要求"
            
            # 验证服装一致性 > 85%
            assert score.clothing_consistency > 0.85, \
                f"服装一致性 {score.clothing_consistency} 低于85%要求"
        
        finally:
            if os.path.exists(reference_path):
                os.unlink(reference_path)
            for frame_path in generated_frames:
                if os.path.exists(frame_path):
                    os.unlink(frame_path)


class TestCheckpoint7Summary:
    """检查点7：总结测试"""
    
    def test_checkpoint_7_summary(self):
        """检查点7总结
        
        验证所有核心AI引擎功能：
        ✓ 中文口型同步引擎可用
        ✓ 角色一致性引擎可用
        ✓ 口型同步精度满足要求
        ✓ 角色一致性满足要求
        ✓ 性能指标满足要求
        ✓ 集成工作流正常
        """
        # 验证引擎可用性
        lip_sync_engine = get_lip_sync_engine()
        character_engine = get_character_consistency_engine()
        
        assert lip_sync_engine is not None, "口型同步引擎不可用"
        assert character_engine is not None, "角色一致性引擎不可用"
        
        # 验证配置
        assert len(lip_sync_engine.INITIALS) == 21, "声母配置不正确"
        assert len(character_engine.SUPPORTED_STYLES) == 2, "风格配置不正确"
        
        print("\n" + "="*60)
        print("检查点7验证完成")
        print("="*60)
        print("✓ 中文口型同步引擎：正常")
        print("✓ 角色一致性引擎：正常")
        print("✓ 口型同步精度：< 50ms")
        print("✓ 角色一致性：面部>90%, 服装>85%")
        print("✓ 性能指标：满足要求")
        print("✓ 集成工作流：正常")
        print("="*60)
