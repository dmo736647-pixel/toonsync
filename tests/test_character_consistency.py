"""角色一致性单元测试"""
import pytest
import os
import tempfile
import json
from unittest.mock import Mock, patch, MagicMock
from PIL import Image
import numpy as np

from app.services.character_consistency import (
    CharacterConsistencyEngine,
    ConsistencyModel,
    ConsistencyScore,
    get_character_consistency_engine
)


class TestConsistencyModel:
    """一致性模型测试"""
    
    def test_consistency_model_creation(self):
        """测试一致性模型创建"""
        model = ConsistencyModel(
            character_id="char_123",
            reference_image_path="/path/to/image.png",
            facial_features={"eyes": 0.5},
            clothing_features={"color": "blue"},
            style="anime"
        )
        
        assert model.character_id == "char_123"
        assert model.reference_image_path == "/path/to/image.png"
        assert model.facial_features == {"eyes": 0.5}
        assert model.clothing_features == {"color": "blue"}
        assert model.style == "anime"
        assert model.created_at is not None
    
    def test_consistency_model_to_dict(self):
        """测试一致性模型转换为字典"""
        model = ConsistencyModel(
            character_id="char_123",
            reference_image_path="/path/to/image.png",
            facial_features={"eyes": 0.5},
            clothing_features={"color": "blue"},
            style="anime"
        )
        
        data = model.to_dict()
        
        assert data["character_id"] == "char_123"
        assert data["reference_image_path"] == "/path/to/image.png"
        assert data["facial_features"] == {"eyes": 0.5}
        assert data["clothing_features"] == {"color": "blue"}
        assert data["style"] == "anime"
        assert "created_at" in data
    
    def test_consistency_model_save_and_load(self):
        """测试一致性模型保存和加载"""
        model = ConsistencyModel(
            character_id="char_123",
            reference_image_path="/path/to/image.png",
            facial_features={"eyes": 0.5},
            clothing_features={"color": "blue"},
            style="anime"
        )
        
        # 保存到临时文件
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".json") as f:
            temp_path = f.name
        
        try:
            model.save(temp_path)
            
            # 加载模型
            loaded_model = ConsistencyModel.load(temp_path)
            
            assert loaded_model.character_id == model.character_id
            assert loaded_model.reference_image_path == model.reference_image_path
            assert loaded_model.facial_features == model.facial_features
            assert loaded_model.clothing_features == model.clothing_features
            assert loaded_model.style == model.style
        
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


class TestConsistencyScore:
    """一致性评分测试"""
    
    def test_consistency_score_creation(self):
        """测试一致性评分创建"""
        score = ConsistencyScore(
            facial_similarity=0.95,
            clothing_consistency=0.90,
            overall_score=0.925
        )
        
        assert score.facial_similarity == 0.95
        assert score.clothing_consistency == 0.90
        assert score.overall_score == 0.925
    
    def test_consistency_score_meets_requirements(self):
        """测试一致性评分是否满足要求"""
        # 满足要求的评分
        score1 = ConsistencyScore(
            facial_similarity=0.95,
            clothing_consistency=0.90,
            overall_score=0.925
        )
        assert score1.meets_requirements() is True
        
        # 不满足要求的评分（面部相似度低）
        score2 = ConsistencyScore(
            facial_similarity=0.85,
            clothing_consistency=0.90,
            overall_score=0.875
        )
        assert score2.meets_requirements() is False
        
        # 不满足要求的评分（服装一致性低）
        score3 = ConsistencyScore(
            facial_similarity=0.95,
            clothing_consistency=0.80,
            overall_score=0.875
        )
        assert score3.meets_requirements() is False
    
    def test_consistency_score_to_dict(self):
        """测试一致性评分转换为字典"""
        score = ConsistencyScore(
            facial_similarity=0.95,
            clothing_consistency=0.90,
            overall_score=0.925,
            details={"num_frames": 5}
        )
        
        data = score.to_dict()
        
        assert data["facial_similarity"] == 0.95
        assert data["clothing_consistency"] == 0.90
        assert data["overall_score"] == 0.925
        assert data["meets_requirements"] is True
        assert data["details"] == {"num_frames": 5}


class TestCharacterConsistencyEngine:
    """角色一致性引擎测试"""
    
    @pytest.fixture
    def engine(self):
        """创建引擎实例"""
        return CharacterConsistencyEngine()
    
    @pytest.fixture
    def test_image(self):
        """创建测试图像"""
        # 创建一个简单的RGB图像
        img = Image.new('RGB', (256, 256), color=(100, 150, 200))
        
        # 保存到临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as f:
            img.save(f.name)
            temp_path = f.name
        
        yield temp_path
        
        # 清理
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    def test_engine_initialization(self, engine):
        """测试引擎初始化"""
        assert engine.SUPPORTED_STYLES == ["anime", "realistic"]
        assert len(engine.FACIAL_KEYPOINTS) == 8
        assert len(engine.CLOTHING_FEATURES) == 4
    
    def test_load_image(self, engine, test_image):
        """测试图像加载"""
        image = engine._load_image(test_image)
        
        assert isinstance(image, Image.Image)
        assert image.mode == 'RGB'
        assert image.size == (256, 256)
    
    def test_load_image_invalid_path(self, engine):
        """测试加载无效图像路径"""
        with pytest.raises(ValueError):
            engine._load_image("/invalid/path/to/image.png")
    
    def test_extract_facial_features(self, engine, test_image):
        """测试面部特征提取"""
        image = engine._load_image(test_image)
        features = engine._extract_facial_features(image, "anime")
        
        assert "color_mean" in features
        assert "color_std" in features
        assert "texture" in features
        assert "image_size" in features
        assert "style" in features
        assert "keypoints" in features
        
        # 验证颜色特征
        assert len(features["color_mean"]) == 3  # RGB
        assert len(features["color_std"]) == 3
        
        # 验证纹理特征
        assert "mean" in features["texture"]
        assert "std" in features["texture"]
        
        # 验证关键点
        assert len(features["keypoints"]) == len(engine.FACIAL_KEYPOINTS)
    
    def test_extract_clothing_features(self, engine, test_image):
        """测试服装特征提取"""
        image = engine._load_image(test_image)
        features = engine._extract_clothing_features(image, "anime")
        
        assert "color_palette" in features
        assert "dominant_colors" in features
        assert "style" in features
        assert "features" in features
        
        # 验证颜色调色板
        assert len(features["color_palette"]) > 0
        assert len(features["dominant_colors"]) == 3  # RGB
        
        # 验证服装特征
        assert len(features["features"]) == len(engine.CLOTHING_FEATURES)
    
    def test_extract_character_features(self, engine, test_image):
        """测试角色特征提取"""
        model = engine.extract_character_features(
            reference_image_path=test_image,
            character_id="char_123",
            style="anime"
        )
        
        assert isinstance(model, ConsistencyModel)
        assert model.character_id == "char_123"
        assert model.reference_image_path == test_image
        assert model.style == "anime"
        assert "color_mean" in model.facial_features
        assert "color_palette" in model.clothing_features
    
    def test_extract_character_features_invalid_style(self, engine, test_image):
        """测试使用无效风格提取特征"""
        with pytest.raises(ValueError):
            engine.extract_character_features(
                reference_image_path=test_image,
                character_id="char_123",
                style="invalid_style"
            )
    
    def test_extract_character_features_processing_time(self, engine, test_image):
        """测试特征提取处理时间（应< 2秒）"""
        import time
        
        start_time = time.time()
        model = engine.extract_character_features(
            reference_image_path=test_image,
            character_id="char_123",
            style="anime"
        )
        processing_time = time.time() - start_time
        
        # 验证处理时间
        assert processing_time < 2.0, f"处理时间 {processing_time}s 超过2秒要求"
    
    def test_calculate_similarity(self, engine):
        """测试相似度计算"""
        vec1 = [1.0, 2.0, 3.0]
        vec2 = [1.0, 2.0, 3.0]
        
        # 相同向量应该有高相似度
        similarity = engine._calculate_similarity(vec1, vec2)
        assert 0.9 < similarity <= 1.0
        
        # 不同向量应该有较低相似度
        vec3 = [10.0, 20.0, 30.0]
        similarity2 = engine._calculate_similarity(vec1, vec3)
        assert 0.0 <= similarity2 < 1.0
    
    def test_calculate_similarity_zero_vectors(self, engine):
        """测试零向量的相似度计算"""
        vec1 = [0.0, 0.0, 0.0]
        vec2 = [1.0, 2.0, 3.0]
        
        similarity = engine._calculate_similarity(vec1, vec2)
        assert similarity == 0.0
    
    def test_generate_storyboard_frame(self, engine, test_image):
        """测试分镜生成"""
        # 创建一致性模型
        model = engine.extract_character_features(
            reference_image_path=test_image,
            character_id="char_123",
            style="anime"
        )
        
        # 生成分镜
        frame_path = engine.generate_storyboard_frame(
            consistency_model=model,
            scene_description="角色站在森林中"
        )
        
        # 验证生成的文件存在
        assert os.path.exists(frame_path)
        
        # 验证是有效的图像文件
        image = Image.open(frame_path)
        assert image.size == (256, 256)
        
        # 清理
        os.unlink(frame_path)
    
    def test_validate_consistency(self, engine, test_image):
        """测试一致性验证"""
        # 创建多个测试图像
        generated_frames = []
        for i in range(3):
            img = Image.new('RGB', (256, 256), color=(100 + i*10, 150, 200))
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as f:
                img.save(f.name)
                generated_frames.append(f.name)
        
        try:
            # 验证一致性
            score = engine.validate_consistency(
                reference_image_path=test_image,
                generated_frames=generated_frames
            )
            
            assert isinstance(score, ConsistencyScore)
            assert 0.0 <= score.facial_similarity <= 1.0
            assert 0.0 <= score.clothing_consistency <= 1.0
            assert 0.0 <= score.overall_score <= 1.0
            assert score.details["num_frames"] == 3
        
        finally:
            # 清理
            for frame_path in generated_frames:
                if os.path.exists(frame_path):
                    os.unlink(frame_path)
    
    def test_validate_consistency_empty_frames(self, engine, test_image):
        """测试空帧列表的一致性验证"""
        score = engine.validate_consistency(
            reference_image_path=test_image,
            generated_frames=[]
        )
        
        assert score.facial_similarity == 0.0
        assert score.clothing_consistency == 0.0
        assert score.overall_score == 0.0
    
    def test_batch_generate_frames(self, engine, test_image):
        """测试批量生成分镜"""
        # 创建一致性模型
        model = engine.extract_character_features(
            reference_image_path=test_image,
            character_id="char_123",
            style="anime"
        )
        
        # 批量生成
        scene_descriptions = [
            "角色站在森林中",
            "角色坐在椅子上",
            "角色在奔跑"
        ]
        
        output_dir = tempfile.mkdtemp()
        
        try:
            frame_paths = engine.batch_generate_frames(
                consistency_model=model,
                scene_descriptions=scene_descriptions,
                output_dir=output_dir
            )
            
            # 验证生成的帧数
            assert len(frame_paths) == 3
            
            # 验证所有文件都存在
            for frame_path in frame_paths:
                assert os.path.exists(frame_path)
                
                # 验证是有效的图像文件
                image = Image.open(frame_path)
                assert image.size == (256, 256)
        
        finally:
            # 清理
            import shutil
            if os.path.exists(output_dir):
                shutil.rmtree(output_dir)


class TestGetCharacterConsistencyEngine:
    """获取引擎实例测试"""
    
    def test_get_character_consistency_engine_singleton(self):
        """测试引擎单例模式"""
        # 重置全局实例
        import app.services.character_consistency as cc_module
        cc_module._engine_instance = None
        
        # 获取两次实例
        engine1 = get_character_consistency_engine()
        engine2 = get_character_consistency_engine()
        
        # 应该是同一个实例
        assert engine1 is engine2
