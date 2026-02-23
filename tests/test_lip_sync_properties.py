"""口型同步属性测试

这些测试验证口型同步引擎的正确性属性，使用Hypothesis进行基于属性的测试。
"""
import pytest
from hypothesis import given, strategies as st, settings, assume
from unittest.mock import patch, MagicMock
import numpy as np

from app.services.lip_sync import (
    ChineseLipSyncEngine,
    AudioAnalysis,
    LipKeyframe,
    get_lip_sync_engine
)


# 测试策略定义
@st.composite
def audio_analysis_strategy(draw):
    """生成音频分析结果的策略"""
    duration = draw(st.floats(min_value=0.1, max_value=10.0))
    num_phonemes = draw(st.integers(min_value=1, max_value=50))
    
    phonemes = []
    current_time = 0.0
    
    for i in range(num_phonemes):
        phoneme_duration = draw(st.floats(min_value=0.05, max_value=0.3))
        if current_time + phoneme_duration > duration:
            break
        
        phoneme = draw(st.sampled_from(['a', 'i', 'u', 'n', 'zh', 'b', 'f']))
        tone = draw(st.integers(min_value=0, max_value=4))
        phoneme_type = draw(st.sampled_from(['initial', 'final']))
        
        phonemes.append({
            "phoneme": phoneme,
            "start_time": current_time,
            "end_time": current_time + phoneme_duration,
            "tone": tone,
            "word": "测试",
            "type": phoneme_type
        })
        
        current_time += phoneme_duration
    
    return AudioAnalysis(
        phonemes=phonemes,
        duration=duration,
        sample_rate=16000,
        transcript="测试文本"
    )


class TestLipSyncProperties:
    """口型同步属性测试"""
    
    @pytest.fixture
    def engine(self):
        """创建引擎实例"""
        with patch('app.services.lip_sync.whisper'):
            engine = ChineseLipSyncEngine(whisper_model_name="base")
            return engine
    
    @given(audio_analysis_strategy())
    @settings(max_examples=100, deadline=None)
    def test_property_1_sync_accuracy(self, engine, audio_analysis):
        """
        **属性1：中文口型同步精度**
        对于任意中文普通话音频文件和角色图像，生成的口型关键帧与音频的时间误差应不超过50毫秒
        **验证：需求1.3**
        """
        # 生成口型关键帧
        keyframes = engine.generate_lip_keyframes(audio_analysis, style="anime")
        
        # 验证同步精度
        accuracy = engine.validate_sync_accuracy(keyframes, audio_analysis)
        
        # 断言：平均误差应不超过50ms
        assert accuracy.average_error_ms <= 50.0, \
            f"平均误差 {accuracy.average_error_ms}ms 超过了50ms的要求"
        
        # 断言：准确率应该较高（至少80%的关键帧误差<50ms）
        assert accuracy.accuracy_rate >= 0.8, \
            f"准确率 {accuracy.accuracy_rate} 低于80%的要求"
    
    @given(audio_analysis_strategy())
    @settings(max_examples=100, deadline=None)
    def test_property_2_processing_speed(self, engine, audio_analysis):
        """
        **属性2：口型同步处理速度**
        对于任意音频文件，口型动画生成的处理时间应不超过音频时长的1.5倍
        **验证：需求1.5**
        """
        import time
        
        # 记录开始时间
        start_time = time.time()
        
        # 生成口型关键帧
        keyframes = engine.generate_lip_keyframes(audio_analysis, style="anime")
        
        # 计算处理时间
        processing_time = time.time() - start_time
        
        # 断言：处理时间应不超过音频时长的1.5倍
        max_allowed_time = audio_analysis.duration * 1.5
        assert processing_time <= max_allowed_time, \
            f"处理时间 {processing_time}s 超过了音频时长的1.5倍 ({max_allowed_time}s)"
    
    @given(
        audio_analysis_strategy(),
        st.sampled_from(["anime", "realistic"])
    )
    @settings(max_examples=100, deadline=None)
    def test_property_3_style_support(self, engine, audio_analysis, style):
        """
        **属性3：口型同步风格支持**
        对于任意音频分析结果和角色图像，系统应能成功生成动态漫和真人短剧两种风格的口型关键帧
        **验证：需求1.6**
        """
        # 生成指定风格的口型关键帧
        keyframes = engine.generate_lip_keyframes(audio_analysis, style=style)
        
        # 断言：应该成功生成关键帧
        assert len(keyframes) > 0, f"未能生成{style}风格的口型关键帧"
        
        # 断言：所有关键帧都应该有效
        for kf in keyframes:
            assert isinstance(kf, LipKeyframe)
            assert 0.0 <= kf.timestamp <= audio_analysis.duration
            assert 0.0 <= kf.intensity <= 1.0
            assert kf.mouth_shape in [
                "neutral", "closed", "teeth", "small_open", "medium_open",
                "wide_open", "smile", "round", "round_smile"
            ]
    
    @given(audio_analysis_strategy())
    @settings(max_examples=100, deadline=None)
    def test_property_5_audio_analysis_and_keyframe_generation(self, engine, audio_analysis):
        """
        **属性5：音频分析和关键帧生成**
        对于任意中文普通话音频文件，系统应能分析音频提取音素和声调信息，
        并生成与时间轴精确匹配的口型关键帧序列
        **验证：需求1.1, 1.2, 1.4**
        """
        # 验证音频分析结果
        assert audio_analysis.duration > 0
        assert audio_analysis.sample_rate > 0
        assert len(audio_analysis.phonemes) > 0
        
        # 验证音素信息完整性
        for phoneme in audio_analysis.phonemes:
            assert "phoneme" in phoneme
            assert "start_time" in phoneme
            assert "end_time" in phoneme
            assert "tone" in phoneme
            assert phoneme["start_time"] < phoneme["end_time"]
            assert 0 <= phoneme["tone"] <= 5
        
        # 生成口型关键帧
        keyframes = engine.generate_lip_keyframes(audio_analysis, style="anime")
        
        # 验证关键帧生成
        assert len(keyframes) > 0, "未能生成口型关键帧"
        
        # 验证关键帧时间轴匹配
        for i in range(len(keyframes) - 1):
            assert keyframes[i].timestamp <= keyframes[i + 1].timestamp, \
                "关键帧时间戳应该递增"
        
        # 验证关键帧在音频时长范围内
        for kf in keyframes:
            assert 0.0 <= kf.timestamp <= audio_analysis.duration, \
                f"关键帧时间戳 {kf.timestamp} 超出音频时长 {audio_analysis.duration}"


class TestPhonemeExtraction:
    """音素提取属性测试"""
    
    @pytest.fixture
    def engine(self):
        """创建引擎实例"""
        with patch('app.services.lip_sync.whisper'):
            engine = ChineseLipSyncEngine(whisper_model_name="base")
            return engine
    
    @given(
        st.text(
            alphabet=st.characters(whitelist_categories=('Lo',), min_codepoint=0x4E00, max_codepoint=0x9FFF),
            min_size=1,
            max_size=10
        ),
        st.floats(min_value=0.0, max_value=1.0),
        st.floats(min_value=1.0, max_value=5.0)
    )
    @settings(max_examples=100, deadline=None)
    def test_chinese_phoneme_extraction(self, engine, text, start_time, end_time):
        """测试中文音素提取的正确性"""
        assume(start_time < end_time)
        
        with patch('app.services.lip_sync.pinyin') as mock_pinyin:
            # 模拟pypinyin返回
            mock_pinyin.return_value = [['ni3'] for _ in text]
            
            phonemes = engine._extract_chinese_phonemes(text, start_time, end_time)
            
            # 验证音素数量
            assert len(phonemes) > 0
            
            # 验证时间范围
            for p in phonemes:
                assert start_time <= p["start_time"] <= end_time
                assert start_time <= p["end_time"] <= end_time
                assert p["start_time"] < p["end_time"]
    
    @given(st.sampled_from(['ni3', 'hao3', 'ma1', 'de', 'zhang3']))
    @settings(max_examples=100, deadline=None)
    def test_tone_extraction(self, engine, pinyin_str):
        """测试声调提取的正确性"""
        tone = engine._extract_tone(pinyin_str)
        
        # 验证声调范围
        assert 0 <= tone <= 5
    
    @given(st.sampled_from(['ni3', 'hao3', 'zhang3', 'chi1', 'shi4', 'ai4']))
    @settings(max_examples=100, deadline=None)
    def test_pinyin_splitting(self, engine, pinyin_str):
        """测试拼音分离的正确性"""
        initial, final = engine._split_pinyin(pinyin_str)
        
        # 验证分离结果
        assert isinstance(initial, str)
        assert isinstance(final, str)
        
        # 至少应该有声母或韵母之一
        assert initial or final


class TestKeyframeValidation:
    """关键帧验证属性测试"""
    
    @pytest.fixture
    def engine(self):
        """创建引擎实例"""
        with patch('app.services.lip_sync.whisper'):
            engine = ChineseLipSyncEngine(whisper_model_name="base")
            return engine
    
    @given(audio_analysis_strategy())
    @settings(max_examples=100, deadline=None)
    def test_keyframe_temporal_consistency(self, engine, audio_analysis):
        """测试关键帧时间一致性"""
        keyframes = engine.generate_lip_keyframes(audio_analysis, style="anime")
        
        # 验证时间戳单调递增
        for i in range(len(keyframes) - 1):
            assert keyframes[i].timestamp <= keyframes[i + 1].timestamp, \
                "关键帧时间戳必须单调递增"
    
    @given(audio_analysis_strategy())
    @settings(max_examples=100, deadline=None)
    def test_keyframe_intensity_range(self, engine, audio_analysis):
        """测试关键帧强度范围"""
        keyframes = engine.generate_lip_keyframes(audio_analysis, style="anime")
        
        # 验证强度在有效范围内
        for kf in keyframes:
            assert 0.0 <= kf.intensity <= 1.0, \
                f"关键帧强度 {kf.intensity} 超出有效范围 [0, 1]"
    
    @given(audio_analysis_strategy())
    @settings(max_examples=100, deadline=None)
    def test_keyframe_coverage(self, engine, audio_analysis):
        """测试关键帧覆盖完整音频时长"""
        keyframes = engine.generate_lip_keyframes(audio_analysis, style="anime")
        
        if keyframes:
            # 第一个关键帧应该在开始附近
            assert keyframes[0].timestamp <= 0.1, \
                "第一个关键帧应该在音频开始附近"
            
            # 最后一个关键帧应该在结束附近
            assert keyframes[-1].timestamp >= audio_analysis.duration - 0.1, \
                "最后一个关键帧应该在音频结束附近"


class TestWav2LipExport:
    """Wav2Lip导出属性测试"""
    
    @pytest.fixture
    def engine(self):
        """创建引擎实例"""
        with patch('app.services.lip_sync.whisper'):
            engine = ChineseLipSyncEngine(whisper_model_name="base")
            return engine
    
    @given(
        audio_analysis_strategy(),
        st.integers(min_value=15, max_value=60)
    )
    @settings(max_examples=100, deadline=None)
    def test_wav2lip_frame_count(self, engine, audio_analysis, fps):
        """测试Wav2Lip导出的帧数正确性"""
        keyframes = engine.generate_lip_keyframes(audio_analysis, style="anime")
        wav2lip_frames = engine.export_keyframes_for_wav2lip(keyframes, fps=fps)
        
        # 验证帧数
        expected_frames = int(audio_analysis.duration * fps)
        assert len(wav2lip_frames) == expected_frames, \
            f"导出帧数 {len(wav2lip_frames)} 与预期 {expected_frames} 不符"
    
    @given(audio_analysis_strategy())
    @settings(max_examples=100, deadline=None)
    def test_wav2lip_frame_completeness(self, engine, audio_analysis):
        """测试Wav2Lip导出帧的完整性"""
        keyframes = engine.generate_lip_keyframes(audio_analysis, style="anime")
        wav2lip_frames = engine.export_keyframes_for_wav2lip(keyframes, fps=25)
        
        # 验证每帧都有必要的字段
        for frame in wav2lip_frames:
            assert "frame" in frame
            assert "timestamp" in frame
            assert "mouth_shape" in frame
            assert "intensity" in frame
            assert "phoneme" in frame
            
            # 验证值的有效性
            assert frame["frame"] >= 0
            assert 0.0 <= frame["timestamp"] <= audio_analysis.duration
            assert 0.0 <= frame["intensity"] <= 1.0
