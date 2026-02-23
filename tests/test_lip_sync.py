"""口型同步单元测试"""
import pytest
import os
import tempfile
import numpy as np
from unittest.mock import Mock, patch, MagicMock

from app.services.lip_sync import (
    ChineseLipSyncEngine,
    AudioAnalysis,
    LipKeyframe,
    SyncAccuracyReport,
    get_lip_sync_engine
)


class TestChineseLipSyncEngine:
    """中文口型同步引擎测试"""
    
    @pytest.fixture
    def engine(self):
        """创建引擎实例"""
        with patch('app.services.lip_sync.whisper'):
            engine = ChineseLipSyncEngine(whisper_model_name="base")
            return engine
    
    @pytest.fixture
    def mock_audio_file(self):
        """创建模拟音频文件"""
        # 创建临时音频文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
            # 写入简单的音频数据（1秒，16kHz采样率）
            sample_rate = 16000
            duration = 1.0
            samples = np.zeros(int(sample_rate * duration), dtype=np.float32)
            f.write(samples.tobytes())
            temp_path = f.name
        
        yield temp_path
        
        # 清理
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    @pytest.fixture
    def mock_whisper_result(self):
        """模拟Whisper转录结果"""
        return {
            "text": "你好世界",
            "segments": [
                {
                    "words": [
                        {"word": "你好", "start": 0.0, "end": 0.5},
                        {"word": "世界", "start": 0.5, "end": 1.0}
                    ]
                }
            ]
        }
    
    def test_engine_initialization(self, engine):
        """测试引擎初始化"""
        assert engine.whisper_model_name == "base"
        assert engine.whisper_model is None
        assert len(engine.INITIALS) == 21
        assert len(engine.FINALS) >= 24
    
    def test_extract_tone(self, engine):
        """测试声调提取"""
        assert engine._extract_tone("ni3") == 3
        assert engine._extract_tone("hao3") == 3
        assert engine._extract_tone("ma1") == 1
        assert engine._extract_tone("de") == 0  # 轻声
    
    def test_split_pinyin(self, engine):
        """测试拼音分离"""
        # 测试双字母声母
        initial, final = engine._split_pinyin("zhang3")
        assert initial == "zh"
        assert final == "ang"
        
        # 测试单字母声母
        initial, final = engine._split_pinyin("ni3")
        assert initial == "n"
        assert final == "i"
        
        # 测试无声母
        initial, final = engine._split_pinyin("ai4")
        assert initial == ""
        assert final == "ai"
    
    def test_extract_chinese_phonemes(self, engine):
        """测试中文音素提取"""
        with patch('app.services.lip_sync.pinyin') as mock_pinyin:
            # 模拟pypinyin返回
            mock_pinyin.return_value = [['ni3'], ['hao3']]
            
            phonemes = engine._extract_chinese_phonemes("你好", 0.0, 1.0)
            
            # 应该有4个音素：n, i, h, ao
            assert len(phonemes) >= 2
            
            # 检查时间戳
            for p in phonemes:
                assert 0.0 <= p["start_time"] <= 1.0
                assert 0.0 <= p["end_time"] <= 1.0
                assert p["start_time"] < p["end_time"]
    
    @patch('app.services.lip_sync.librosa.load')
    @patch('app.services.lip_sync.whisper')
    def test_analyze_audio(self, mock_whisper_module, mock_librosa_load, engine, mock_whisper_result):
        """测试音频分析"""
        # 模拟librosa加载
        mock_librosa_load.return_value = (np.zeros(16000), 16000)
        
        # 模拟Whisper模型
        mock_model = MagicMock()
        mock_model.transcribe.return_value = mock_whisper_result
        engine.whisper_model = mock_model
        
        # 模拟pypinyin
        with patch('app.services.lip_sync.pinyin') as mock_pinyin:
            mock_pinyin.return_value = [['ni3'], ['hao3']]
            
            # 执行分析
            analysis = engine.analyze_audio("test.wav")
            
            # 验证结果
            assert isinstance(analysis, AudioAnalysis)
            assert analysis.duration > 0
            assert analysis.sample_rate == 16000
            assert analysis.transcript == "你好世界"
            assert len(analysis.phonemes) > 0
    
    def test_get_mouth_shape_for_phoneme(self, engine):
        """测试音素到口型的映射"""
        # 测试声母
        assert engine._get_mouth_shape_for_phoneme("b") == "closed"
        assert engine._get_mouth_shape_for_phoneme("f") == "teeth"
        assert engine._get_mouth_shape_for_phoneme("zh") == "round"
        
        # 测试韵母
        assert engine._get_mouth_shape_for_phoneme("a") == "wide_open"
        assert engine._get_mouth_shape_for_phoneme("i") == "smile"
        assert engine._get_mouth_shape_for_phoneme("u") == "round"
        
        # 测试未知音素
        assert engine._get_mouth_shape_for_phoneme("xyz") == "neutral"
    
    def test_calculate_intensity(self, engine):
        """测试口型强度计算"""
        # 测试不同声调
        intensity_1 = engine._calculate_intensity(1, "realistic")
        intensity_3 = engine._calculate_intensity(3, "realistic")
        assert 0.0 <= intensity_1 <= 1.0
        assert 0.0 <= intensity_3 <= 1.0
        
        # 测试动态漫风格（应该更夸张）
        intensity_anime = engine._calculate_intensity(3, "anime")
        intensity_realistic = engine._calculate_intensity(3, "realistic")
        assert intensity_anime >= intensity_realistic
    
    def test_generate_lip_keyframes(self, engine):
        """测试口型关键帧生成"""
        # 创建模拟音频分析结果
        analysis = AudioAnalysis(
            phonemes=[
                {"phoneme": "n", "start_time": 0.0, "end_time": 0.1, "tone": 0, "word": "你"},
                {"phoneme": "i", "start_time": 0.1, "end_time": 0.2, "tone": 3, "word": "你"},
            ],
            duration=0.2,
            sample_rate=16000,
            transcript="你"
        )
        
        # 生成关键帧
        keyframes = engine.generate_lip_keyframes(analysis, style="anime")
        
        # 验证结果
        assert len(keyframes) > 0
        assert all(isinstance(kf, LipKeyframe) for kf in keyframes)
        
        # 验证时间戳顺序
        for i in range(len(keyframes) - 1):
            assert keyframes[i].timestamp <= keyframes[i + 1].timestamp
    
    def test_validate_sync_accuracy(self, engine):
        """测试同步精度验证"""
        # 创建模拟数据
        analysis = AudioAnalysis(
            phonemes=[
                {"phoneme": "n", "start_time": 0.0, "end_time": 0.1, "tone": 0, "word": "你"},
                {"phoneme": "i", "start_time": 0.1, "end_time": 0.2, "tone": 3, "word": "你"},
            ],
            duration=0.2,
            sample_rate=16000,
            transcript="你"
        )
        
        keyframes = [
            LipKeyframe(timestamp=0.0, phoneme="n", mouth_shape="small_open", intensity=0.8),
            LipKeyframe(timestamp=0.1, phoneme="i", mouth_shape="smile", intensity=1.0),
        ]
        
        # 验证精度
        report = engine.validate_sync_accuracy(keyframes, analysis)
        
        # 验证报告
        assert isinstance(report, SyncAccuracyReport)
        assert report.average_error_ms >= 0
        assert report.max_error_ms >= 0
        assert 0.0 <= report.accuracy_rate <= 1.0
        assert report.total_keyframes == len(keyframes)
    
    def test_validate_sync_accuracy_empty(self, engine):
        """测试空数据的同步精度验证"""
        analysis = AudioAnalysis(
            phonemes=[],
            duration=0.0,
            sample_rate=16000,
            transcript=""
        )
        
        report = engine.validate_sync_accuracy([], analysis)
        
        assert report.average_error_ms == 0
        assert report.max_error_ms == 0
        assert report.accuracy_rate == 0
        assert report.total_keyframes == 0


class TestAudioAnalysis:
    """音频分析结果测试"""
    
    def test_audio_analysis_creation(self):
        """测试音频分析结果创建"""
        phonemes = [
            {"phoneme": "n", "start_time": 0.0, "end_time": 0.1, "tone": 0, "word": "你"}
        ]
        
        analysis = AudioAnalysis(
            phonemes=phonemes,
            duration=1.0,
            sample_rate=16000,
            transcript="你好"
        )
        
        assert analysis.phonemes == phonemes
        assert analysis.duration == 1.0
        assert analysis.sample_rate == 16000
        assert analysis.transcript == "你好"
        assert analysis.created_at is not None
    
    def test_audio_analysis_to_dict(self):
        """测试音频分析结果转换为字典"""
        phonemes = [
            {"phoneme": "n", "start_time": 0.0, "end_time": 0.1, "tone": 0, "word": "你"}
        ]
        
        analysis = AudioAnalysis(
            phonemes=phonemes,
            duration=1.0,
            sample_rate=16000,
            transcript="你好"
        )
        
        data = analysis.to_dict()
        
        assert data["phonemes"] == phonemes
        assert data["duration"] == 1.0
        assert data["sample_rate"] == 16000
        assert data["transcript"] == "你好"
        assert "created_at" in data


class TestLipKeyframe:
    """口型关键帧测试"""
    
    def test_lip_keyframe_creation(self):
        """测试口型关键帧创建"""
        keyframe = LipKeyframe(
            timestamp=0.5,
            phoneme="a",
            mouth_shape="wide_open",
            intensity=0.9
        )
        
        assert keyframe.timestamp == 0.5
        assert keyframe.phoneme == "a"
        assert keyframe.mouth_shape == "wide_open"
        assert keyframe.intensity == 0.9
    
    def test_lip_keyframe_to_dict(self):
        """测试口型关键帧转换为字典"""
        keyframe = LipKeyframe(
            timestamp=0.5,
            phoneme="a",
            mouth_shape="wide_open",
            intensity=0.9
        )
        
        data = keyframe.to_dict()
        
        assert data["timestamp"] == 0.5
        assert data["phoneme"] == "a"
        assert data["mouth_shape"] == "wide_open"
        assert data["intensity"] == 0.9


class TestSyncAccuracyReport:
    """同步精度报告测试"""
    
    def test_sync_accuracy_report_creation(self):
        """测试同步精度报告创建"""
        report = SyncAccuracyReport(
            average_error_ms=25.5,
            max_error_ms=45.0,
            accuracy_rate=0.95,
            total_keyframes=100
        )
        
        assert report.average_error_ms == 25.5
        assert report.max_error_ms == 45.0
        assert report.accuracy_rate == 0.95
        assert report.total_keyframes == 100
    
    def test_sync_accuracy_report_to_dict(self):
        """测试同步精度报告转换为字典"""
        report = SyncAccuracyReport(
            average_error_ms=25.5,
            max_error_ms=45.0,
            accuracy_rate=0.95,
            total_keyframes=100
        )
        
        data = report.to_dict()
        
        assert data["average_error_ms"] == 25.5
        assert data["max_error_ms"] == 45.0
        assert data["accuracy_rate"] == 0.95
        assert data["total_keyframes"] == 100


class TestGetLipSyncEngine:
    """获取引擎实例测试"""
    
    def test_get_lip_sync_engine_singleton(self):
        """测试引擎单例模式"""
        with patch('app.services.lip_sync.whisper'):
            # 重置全局实例
            import app.services.lip_sync as lip_sync_module
            lip_sync_module._engine_instance = None
            
            # 获取两次实例
            engine1 = get_lip_sync_engine()
            engine2 = get_lip_sync_engine()
            
            # 应该是同一个实例
            assert engine1 is engine2



class TestLipKeyframeGeneration:
    """口型关键帧生成测试"""
    
    @pytest.fixture
    def engine(self):
        """创建引擎实例"""
        with patch('app.services.lip_sync.whisper'):
            engine = ChineseLipSyncEngine(whisper_model_name="base")
            return engine
    
    def test_generate_keyframes_anime_style(self, engine):
        """测试动态漫风格口型生成"""
        analysis = AudioAnalysis(
            phonemes=[
                {"phoneme": "n", "start_time": 0.0, "end_time": 0.1, "tone": 0, "word": "你", "type": "initial"},
                {"phoneme": "i", "start_time": 0.1, "end_time": 0.3, "tone": 3, "word": "你", "type": "final"},
            ],
            duration=0.3,
            sample_rate=16000,
            transcript="你"
        )
        
        keyframes = engine.generate_lip_keyframes(analysis, style="anime")
        
        # 验证关键帧数量（应该有开始帧、音素帧、过渡帧、结束帧）
        assert len(keyframes) > 0
        
        # 验证所有关键帧都是LipKeyframe实例
        assert all(isinstance(kf, LipKeyframe) for kf in keyframes)
        
        # 验证时间戳递增
        for i in range(len(keyframes) - 1):
            assert keyframes[i].timestamp <= keyframes[i + 1].timestamp
        
        # 验证第一帧是静止帧
        assert keyframes[0].timestamp == 0.0
        assert keyframes[0].mouth_shape == "neutral"
        
        # 验证最后一帧是结束帧
        assert keyframes[-1].timestamp == analysis.duration
    
    def test_generate_keyframes_realistic_style(self, engine):
        """测试真人风格口型生成"""
        analysis = AudioAnalysis(
            phonemes=[
                {"phoneme": "h", "start_time": 0.0, "end_time": 0.1, "tone": 0, "word": "好", "type": "initial"},
                {"phoneme": "ao", "start_time": 0.1, "end_time": 0.3, "tone": 3, "word": "好", "type": "final"},
            ],
            duration=0.3,
            sample_rate=16000,
            transcript="好"
        )
        
        keyframes = engine.generate_lip_keyframes(analysis, style="realistic")
        
        # 验证关键帧生成
        assert len(keyframes) > 0
        
        # 真人风格的强度应该相对较低
        for kf in keyframes:
            if kf.mouth_shape != "neutral":
                assert kf.intensity <= 1.0
    
    def test_generate_keyframes_with_tones(self, engine):
        """测试不同声调的口型生成"""
        # 测试四个声调
        for tone in [1, 2, 3, 4]:
            analysis = AudioAnalysis(
                phonemes=[
                    {"phoneme": "a", "start_time": 0.0, "end_time": 0.2, "tone": tone, "word": "啊", "type": "final"},
                ],
                duration=0.2,
                sample_rate=16000,
                transcript="啊"
            )
            
            keyframes = engine.generate_lip_keyframes(analysis, style="anime")
            
            # 验证生成了关键帧
            assert len(keyframes) > 0
            
            # 验证强度在合理范围内
            for kf in keyframes:
                assert 0.0 <= kf.intensity <= 1.0
    
    def test_generate_keyframes_empty_phonemes(self, engine):
        """测试空音素列表"""
        analysis = AudioAnalysis(
            phonemes=[],
            duration=1.0,
            sample_rate=16000,
            transcript=""
        )
        
        keyframes = engine.generate_lip_keyframes(analysis, style="anime")
        
        # 空音素应该返回空关键帧列表
        assert len(keyframes) == 0
    
    def test_mouth_shape_mapping(self, engine):
        """测试音素到口型的映射"""
        # 测试各种音素类型
        test_cases = [
            ("b", "closed"),      # 双唇音
            ("f", "teeth"),       # 唇齿音
            ("a", "wide_open"),   # 开口韵母
            ("i", "smile"),       # 齐齿韵母
            ("u", "round"),       # 合口韵母
            ("zh", "round"),      # 翘舌音
        ]
        
        for phoneme, expected_shape in test_cases:
            shape = engine._get_mouth_shape_for_phoneme(phoneme)
            assert shape == expected_shape, f"音素 {phoneme} 应该映射到 {expected_shape}，但得到 {shape}"
    
    def test_intensity_calculation_by_tone(self, engine):
        """测试声调对强度的影响"""
        # 三声应该有最高强度
        intensity_tone3 = engine._calculate_intensity(3, "realistic")
        intensity_tone1 = engine._calculate_intensity(1, "realistic")
        intensity_tone0 = engine._calculate_intensity(0, "realistic")  # 轻声
        
        # 验证强度关系
        assert intensity_tone3 >= intensity_tone1
        assert intensity_tone1 >= intensity_tone0
    
    def test_intensity_calculation_by_style(self, engine):
        """测试风格对强度的影响"""
        # 动态漫风格应该比真人风格更夸张
        intensity_anime = engine._calculate_intensity(3, "anime")
        intensity_realistic = engine._calculate_intensity(3, "realistic")
        
        assert intensity_anime >= intensity_realistic
    
    def test_export_keyframes_for_wav2lip(self, engine):
        """测试导出Wav2Lip格式"""
        keyframes = [
            LipKeyframe(timestamp=0.0, phoneme="", mouth_shape="neutral", intensity=0.0),
            LipKeyframe(timestamp=0.1, phoneme="a", mouth_shape="wide_open", intensity=0.9),
            LipKeyframe(timestamp=0.2, phoneme="", mouth_shape="neutral", intensity=0.3),
        ]
        
        wav2lip_frames = engine.export_keyframes_for_wav2lip(keyframes, fps=25)
        
        # 验证帧数（0.2秒 * 25fps = 5帧）
        assert len(wav2lip_frames) == 5
        
        # 验证每帧都有必要的字段
        for frame in wav2lip_frames:
            assert "frame" in frame
            assert "timestamp" in frame
            assert "mouth_shape" in frame
            assert "intensity" in frame
            assert "phoneme" in frame
        
        # 验证帧号递增
        for i in range(len(wav2lip_frames) - 1):
            assert wav2lip_frames[i]["frame"] < wav2lip_frames[i + 1]["frame"]
    
    def test_export_keyframes_empty(self, engine):
        """测试导出空关键帧列表"""
        wav2lip_frames = engine.export_keyframes_for_wav2lip([], fps=25)
        
        assert len(wav2lip_frames) == 0
    
    def test_keyframe_interpolation(self, engine):
        """测试关键帧插值"""
        keyframes = [
            LipKeyframe(timestamp=0.0, phoneme="", mouth_shape="neutral", intensity=0.0),
            LipKeyframe(timestamp=0.1, phoneme="a", mouth_shape="wide_open", intensity=1.0),
        ]
        
        wav2lip_frames = engine.export_keyframes_for_wav2lip(keyframes, fps=10)
        
        # 验证插值效果（中间帧的强度应该在0.0和1.0之间）
        if len(wav2lip_frames) > 2:
            middle_frame = wav2lip_frames[len(wav2lip_frames) // 2]
            assert 0.0 < middle_frame["intensity"] < 1.0
