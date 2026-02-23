"""角色一致性属性测试

这些测试验证角色一致性引擎的正确性属性，使用Hypothesis进行基于属性的测试。
"""
import pytest
from hypothesis import given, strategies as st, settings, assume
import tempfile
import os
from PIL import Image

from app.services.character_consistency import (
    CharacterConsistencyEngine,
    ConsistencyModel,
    get_character_consistency_engine
)


# 测试策略定义
@st.composite
def test_image_strategy(draw):
    """生成测试图像的策略"""
    width = draw(st.integers(min_value=128, max_value=512))
    height = draw(st.integers(min_value=128, max_value=512))
    r = draw(st.integers(min_value=0, max_value=255))
    g = draw(st.integers(min_value=0, max_value=255))
    b = draw(st.integers(min_value=0, max_value=255))
    
    # 创建图像
    img = Image.new('RGB', (width, height), color=(r, g, b))
    
    # 保存到临时文件
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as f:
        img.save(f.name)
        return f.name


class TestCharacterConsistencyProperties:
    """角色一致性属性测试"""
    
    @pytest.fixture
    def engine(self):
        """创建引擎实例"""
        return CharacterConsistencyEngine()
    
    @given(
        test_image_strategy(),
        st.sampled_from(["anime", "realistic"])
    )
    @settings(max_examples=100, deadline=None)
    def test_property_7_feature_extraction_speed(self, engine, image_path, style):
        """
        **属性7：角色特征提取速度**
        对于任意角色参考图像，特征提取和一致性模型创建的处理时间应不超过2秒
        **验证：需求2.6**
        """
        import time
        
        try:
            # 记录开始时间
            start_time = time.time()
            
            # 提取特征
            model = engine.extract_character_features(
                reference_image_path=image_path,
                character_id="test_char",
                style=style
            )
            
            # 计算处理时间
            processing_time = time.time() - start_time
            
            # 断言：处理时间应不超过2秒
            assert processing_time < 2.0, \
                f"处理时间 {processing_time}s 超过了2秒的要求"
            
            # 验证模型创建成功
            assert isinstance(model, ConsistencyModel)
            assert model.character_id == "test_char"
            assert model.style == style
        
        finally:
            # 清理临时文件
            if os.path.exists(image_path):
                os.unlink(image_path)
    
    @given(
        test_image_strategy(),
        st.sampled_from(["anime", "realistic"])
    )
    @settings(max_examples=100, deadline=None)
    def test_property_8_style_support(self, engine, image_path, style):
        """
        **属性8：角色渲染风格支持**
        对于任意角色一致性模型和场景描述，系统应能成功生成动态漫和真人短剧两种风格的分镜图像
        **验证：需求2.3**
        """
        try:
            # 提取特征
            model = engine.extract_character_features(
                reference_image_path=image_path,
                character_id="test_char",
                style=style
            )
            
            # 生成分镜
            frame_path = engine.generate_storyboard_frame(
                consistency_model=model,
                scene_description="测试场景"
            )
            
            # 断言：应该成功生成分镜
            assert os.path.exists(frame_path), f"未能生成{style}风格的分镜图像"
            
            # 验证是有效的图像文件
            img = Image.open(frame_path)
            assert img.mode == 'RGB'
            
            # 清理生成的帧
            os.unlink(frame_path)
        
        finally:
            # 清理临时文件
            if os.path.exists(image_path):
                os.unlink(image_path)
    
    @given(test_image_strategy())
    @settings(max_examples=100, deadline=None)
    def test_property_10_character_to_storyboard(self, engine, image_path):
        """
        **属性10：角色图像到分镜生成**
        对于任意角色参考图像，系统应能提取视觉特征创建一致性模型，
        并使用该模型生成视觉风格一致的分镜图像
        **验证：需求2.1, 2.2**
        """
        try:
            # 1. 提取视觉特征创建一致性模型
            model = engine.extract_character_features(
                reference_image_path=image_path,
                character_id="test_char",
                style="anime"
            )
            
            # 验证模型创建成功
            assert isinstance(model, ConsistencyModel)
            assert "color_mean" in model.facial_features
            assert "color_palette" in model.clothing_features
            
            # 2. 使用模型生成分镜图像
            scene_descriptions = ["场景1", "场景2", "场景3"]
            output_dir = tempfile.mkdtemp()
            
            try:
                frame_paths = engine.batch_generate_frames(
                    consistency_model=model,
                    scene_descriptions=scene_descriptions,
                    output_dir=output_dir
                )
                
                # 验证生成成功
                assert len(frame_paths) == len(scene_descriptions)
                
                # 验证所有帧都存在且有效
                for frame_path in frame_paths:
                    assert os.path.exists(frame_path)
                    img = Image.open(frame_path)
                    assert img.mode == 'RGB'
            
            finally:
                # 清理输出目录
                import shutil
                if os.path.exists(output_dir):
                    shutil.rmtree(output_dir)
        
        finally:
            # 清理临时文件
            if os.path.exists(image_path):
                os.unlink(image_path)


class TestConsistencyValidationProperties:
    """一致性验证属性测试"""
    
    @pytest.fixture
    def engine(self):
        """创建引擎实例"""
        return CharacterConsistencyEngine()
    
    @given(
        test_image_strategy(),
        st.integers(min_value=2, max_value=10)
    )
    @settings(max_examples=50, deadline=None)
    def test_property_6_consistency_guarantee(self, engine, image_path, num_frames):
        """
        **属性6：角色一致性保证**
        对于任意角色一致性模型，生成的多个分镜图像之间的面部特征相似度应大于90%，
        服装和发型一致性应大于85%
        **验证：需求2.4**
        
        注意：由于当前实现是简化版本（直接复制参考图像），
        一致性评分会非常高。实际应用中使用真实的AI模型时，
        需要确保满足这些要求。
        """
        try:
            # 提取特征
            model = engine.extract_character_features(
                reference_image_path=image_path,
                character_id="test_char",
                style="anime"
            )
            
            # 生成多个分镜
            scene_descriptions = [f"场景{i}" for i in range(num_frames)]
            output_dir = tempfile.mkdtemp()
            
            try:
                frame_paths = engine.batch_generate_frames(
                    consistency_model=model,
                    scene_descriptions=scene_descriptions,
                    output_dir=output_dir
                )
                
                # 验证一致性
                score = engine.validate_consistency(
                    reference_image_path=image_path,
                    generated_frames=frame_paths
                )
                
                # 断言：面部相似度应大于90%
                assert score.facial_similarity > 0.90, \
                    f"面部相似度 {score.facial_similarity} 低于90%的要求"
                
                # 断言：服装一致性应大于85%
                assert score.clothing_consistency > 0.85, \
                    f"服装一致性 {score.clothing_consistency} 低于85%的要求"
            
            finally:
                # 清理输出目录
                import shutil
                if os.path.exists(output_dir):
                    shutil.rmtree(output_dir)
        
        finally:
            # 清理临时文件
            if os.path.exists(image_path):
                os.unlink(image_path)


class TestFeatureExtractionProperties:
    """特征提取属性测试"""
    
    @pytest.fixture
    def engine(self):
        """创建引擎实例"""
        return CharacterConsistencyEngine()
    
    @given(test_image_strategy())
    @settings(max_examples=100, deadline=None)
    def test_feature_extraction_completeness(self, engine, image_path):
        """测试特征提取的完整性"""
        try:
            model = engine.extract_character_features(
                reference_image_path=image_path,
                character_id="test_char",
                style="anime"
            )
            
            # 验证面部特征完整性
            assert "color_mean" in model.facial_features
            assert "color_std" in model.facial_features
            assert "texture" in model.facial_features
            assert "keypoints" in model.facial_features
            
            # 验证服装特征完整性
            assert "color_palette" in model.clothing_features
            assert "dominant_colors" in model.clothing_features
            assert "features" in model.clothing_features
        
        finally:
            if os.path.exists(image_path):
                os.unlink(image_path)
    
    @given(test_image_strategy())
    @settings(max_examples=100, deadline=None)
    def test_model_serialization(self, engine, image_path):
        """测试模型序列化和反序列化"""
        try:
            # 提取特征
            model = engine.extract_character_features(
                reference_image_path=image_path,
                character_id="test_char",
                style="anime"
            )
            
            # 保存模型
            with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as f:
                model_path = f.name
            
            try:
                model.save(model_path)
                
                # 加载模型
                loaded_model = ConsistencyModel.load(model_path)
                
                # 验证加载的模型与原模型一致
                assert loaded_model.character_id == model.character_id
                assert loaded_model.style == model.style
                assert loaded_model.facial_features == model.facial_features
                assert loaded_model.clothing_features == model.clothing_features
            
            finally:
                if os.path.exists(model_path):
                    os.unlink(model_path)
        
        finally:
            if os.path.exists(image_path):
                os.unlink(image_path)
