"""中文口型同步引擎服务"""
import os
import tempfile
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import numpy as np
from datetime import datetime

# 音频处理库
try:
    import librosa
    import soundfile as sf
except ImportError:
    librosa = None
    sf = None

# Whisper模型（用于语音识别）
try:
    import whisper
except ImportError:
    whisper = None

# 拼音转换库
try:
    from pypinyin import pinyin, Style
except ImportError:
    pinyin = None


class AudioAnalysis:
    """音频分析结果"""
    
    def __init__(
        self,
        phonemes: List[Dict[str, any]],
        duration: float,
        sample_rate: int,
        transcript: str = ""
    ):
        """
        初始化音频分析结果
        
        参数:
            phonemes: 音素序列，每个音素包含 {phoneme, start_time, end_time, tone}
            duration: 音频时长（秒）
            sample_rate: 采样率
            transcript: 转录文本
        """
        self.phonemes = phonemes
        self.duration = duration
        self.sample_rate = sample_rate
        self.transcript = transcript
        self.created_at = datetime.utcnow()
    
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            "phonemes": self.phonemes,
            "duration": self.duration,
            "sample_rate": self.sample_rate,
            "transcript": self.transcript,
            "created_at": self.created_at.isoformat()
        }


class LipKeyframe:
    """口型关键帧"""
    
    def __init__(
        self,
        timestamp: float,
        phoneme: str,
        mouth_shape: str,
        intensity: float = 1.0
    ):
        """
        初始化口型关键帧
        
        参数:
            timestamp: 时间戳（秒）
            phoneme: 音素
            mouth_shape: 口型形状标识
            intensity: 口型强度（0-1）
        """
        self.timestamp = timestamp
        self.phoneme = phoneme
        self.mouth_shape = mouth_shape
        self.intensity = intensity
    
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            "timestamp": self.timestamp,
            "phoneme": self.phoneme,
            "mouth_shape": self.mouth_shape,
            "intensity": self.intensity
        }


class SyncAccuracyReport:
    """同步精度报告"""
    
    def __init__(
        self,
        average_error_ms: float,
        max_error_ms: float,
        accuracy_rate: float,
        total_keyframes: int,
        error_distribution: Optional[Dict[str, int]] = None,
        quality_score: Optional[float] = None
    ):
        """
        初始化同步精度报告
        
        参数:
            average_error_ms: 平均误差（毫秒）
            max_error_ms: 最大误差（毫秒）
            accuracy_rate: 准确率（0-1）
            total_keyframes: 总关键帧数
            error_distribution: 误差分布统计
            quality_score: 质量评分（0-100）
        """
        self.average_error_ms = average_error_ms
        self.max_error_ms = max_error_ms
        self.accuracy_rate = accuracy_rate
        self.total_keyframes = total_keyframes
        self.error_distribution = error_distribution or {}
        self.quality_score = quality_score or self._calculate_quality_score()
    
    def _calculate_quality_score(self) -> float:
        """
        计算质量评分（0-100）
        
        评分标准：
        - 平均误差 < 20ms: 优秀 (90-100分)
        - 平均误差 20-50ms: 良好 (70-90分)
        - 平均误差 > 50ms: 需要改进 (< 70分)
        """
        if self.average_error_ms < 20:
            base_score = 90
            score = base_score + (20 - self.average_error_ms) / 20 * 10
        elif self.average_error_ms < 50:
            base_score = 70
            score = base_score + (50 - self.average_error_ms) / 30 * 20
        else:
            score = max(0, 70 - (self.average_error_ms - 50) / 10)
        
        # 根据准确率调整
        score *= self.accuracy_rate
        
        return min(100.0, max(0.0, score))
    
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            "average_error_ms": self.average_error_ms,
            "max_error_ms": self.max_error_ms,
            "accuracy_rate": self.accuracy_rate,
            "total_keyframes": self.total_keyframes,
            "error_distribution": self.error_distribution,
            "quality_score": self.quality_score,
            "quality_level": self.get_quality_level()
        }
    
    def get_quality_level(self) -> str:
        """获取质量等级"""
        if self.quality_score >= 90:
            return "优秀"
        elif self.quality_score >= 70:
            return "良好"
        elif self.quality_score >= 50:
            return "一般"
        else:
            return "需要改进"


class ChineseLipSyncEngine:
    """中文口型同步引擎"""
    
    # 中文普通话声母（21个）
    INITIALS = [
        'b', 'p', 'm', 'f',
        'd', 't', 'n', 'l',
        'g', 'k', 'h',
        'j', 'q', 'x',
        'zh', 'ch', 'sh', 'r',
        'z', 'c', 's'
    ]
    
    # 中文普通话韵母（39个，简化版）
    FINALS = [
        'a', 'o', 'e', 'i', 'u', 'ü',
        'ai', 'ei', 'ui', 'ao', 'ou', 'iu', 'ie', 'üe',
        'er', 'an', 'en', 'in', 'un', 'ün',
        'ang', 'eng', 'ing', 'ong'
    ]
    
    # 音素到口型的映射
    PHONEME_TO_MOUTH_SHAPE = {
        # 双唇音
        'b': 'closed', 'p': 'closed', 'm': 'closed',
        # 唇齿音
        'f': 'teeth',
        # 舌尖音
        'd': 'small_open', 't': 'small_open', 'n': 'small_open', 'l': 'small_open',
        # 舌根音
        'g': 'medium_open', 'k': 'medium_open', 'h': 'medium_open',
        # 舌面音
        'j': 'smile', 'q': 'smile', 'x': 'smile',
        # 翘舌音
        'zh': 'round', 'ch': 'round', 'sh': 'round', 'r': 'round',
        # 平舌音
        'z': 'small_open', 'c': 'small_open', 's': 'small_open',
        # 韵母
        'a': 'wide_open', 'o': 'round', 'e': 'medium_open',
        'i': 'smile', 'u': 'round', 'ü': 'round_smile',
        'ai': 'wide_open', 'ei': 'smile', 'ui': 'round',
        'ao': 'round', 'ou': 'round', 'iu': 'smile',
        'ie': 'smile', 'üe': 'round_smile',
        'er': 'medium_open',
        'an': 'wide_open', 'en': 'medium_open', 'in': 'smile',
        'un': 'round', 'ün': 'round_smile',
        'ang': 'wide_open', 'eng': 'medium_open', 'ing': 'smile', 'ong': 'round'
    }
    
    def __init__(self, whisper_model_name: str = "base"):
        """
        初始化中文口型同步引擎
        
        参数:
            whisper_model_name: Whisper模型名称（tiny, base, small, medium, large）
        """
        self.whisper_model_name = whisper_model_name
        self.whisper_model = None
        
        # 检查依赖
        if librosa is None:
            raise ImportError("librosa未安装，请运行: pip install librosa soundfile")
        if whisper is None:
            raise ImportError("whisper未安装，请运行: pip install openai-whisper")
        if pinyin is None:
            raise ImportError("pypinyin未安装，请运行: pip install pypinyin")
    
    def _load_whisper_model(self):
        """延迟加载Whisper模型"""
        if self.whisper_model is None:
            self.whisper_model = whisper.load_model(self.whisper_model_name)
    
    def analyze_audio(self, audio_file_path: str) -> AudioAnalysis:
        """
        分析中文音频，提取音素和时序信息
        
        参数:
            audio_file_path: 音频文件路径
        
        返回:
            AudioAnalysis: 包含音素序列、时间戳、声调信息
        """
        # 加载音频文件
        audio_data, sample_rate = librosa.load(audio_file_path, sr=16000)
        duration = len(audio_data) / sample_rate
        
        # 使用Whisper进行语音识别
        self._load_whisper_model()
        result = self.whisper_model.transcribe(
            audio_file_path,
            language="zh",
            word_timestamps=True
        )
        
        transcript = result.get("text", "")
        
        # 提取音素和时间戳
        phonemes = self._extract_phonemes_from_whisper(result)
        
        return AudioAnalysis(
            phonemes=phonemes,
            duration=duration,
            sample_rate=sample_rate,
            transcript=transcript
        )
    
    def _extract_phonemes_from_whisper(self, whisper_result: Dict) -> List[Dict]:
        """
        从Whisper结果中提取音素信息
        
        参数:
            whisper_result: Whisper转录结果
        
        返回:
            List[Dict]: 音素列表
        """
        phonemes = []
        
        # 从segments中提取词级时间戳
        segments = whisper_result.get("segments", [])
        
        for segment in segments:
            words = segment.get("words", [])
            for word_info in words:
                word = word_info.get("word", "").strip()
                start_time = word_info.get("start", 0.0)
                end_time = word_info.get("end", 0.0)
                
                if not word:
                    continue
                
                # 使用pypinyin提取拼音和声调
                word_phonemes = self._extract_chinese_phonemes(
                    word, start_time, end_time
                )
                phonemes.extend(word_phonemes)
        
        return phonemes
    
    def _extract_chinese_phonemes(
        self, 
        text: str, 
        start_time: float, 
        end_time: float
    ) -> List[Dict]:
        """
        提取中文文本的音素信息
        
        参数:
            text: 中文文本
            start_time: 开始时间
            end_time: 结束时间
        
        返回:
            List[Dict]: 音素列表
        """
        phonemes = []
        
        # 获取拼音（带声调）
        pinyin_list = pinyin(text, style=Style.TONE3, heteronym=False)
        
        # 计算每个字的时长
        char_duration = (end_time - start_time) / len(pinyin_list)
        
        for i, py_item in enumerate(pinyin_list):
            py = py_item[0]  # 获取拼音
            
            # 提取声调
            tone = self._extract_tone(py)
            
            # 分离声母和韵母
            initial, final = self._split_pinyin(py)
            
            # 计算时间戳
            char_start = start_time + i * char_duration
            char_end = char_start + char_duration
            
            # 如果有声母，添加声母音素
            if initial:
                initial_duration = char_duration * 0.3  # 声母占30%时长
                phonemes.append({
                    "phoneme": initial,
                    "start_time": char_start,
                    "end_time": char_start + initial_duration,
                    "tone": 0,  # 声母无声调
                    "word": text,
                    "type": "initial"
                })
                
                # 韵母从声母结束后开始
                final_start = char_start + initial_duration
            else:
                final_start = char_start
            
            # 添加韵母音素
            if final:
                phonemes.append({
                    "phoneme": final,
                    "start_time": final_start,
                    "end_time": char_end,
                    "tone": tone,
                    "word": text,
                    "type": "final"
                })
        
        return phonemes
    
    def _extract_tone(self, pinyin_str: str) -> int:
        """
        从拼音字符串中提取声调
        
        参数:
            pinyin_str: 拼音字符串（如 "ni3", "hao3"）
        
        返回:
            int: 声调（0-5）
        """
        # 检查最后一个字符是否是数字
        if pinyin_str and pinyin_str[-1].isdigit():
            return int(pinyin_str[-1])
        return 0  # 轻声
    
    def _split_pinyin(self, pinyin_str: str) -> Tuple[str, str]:
        """
        将拼音分离为声母和韵母
        
        参数:
            pinyin_str: 拼音字符串（如 "ni3", "hao3"）
        
        返回:
            Tuple[str, str]: (声母, 韵母)
        """
        # 移除声调数字
        py = pinyin_str.rstrip('012345')
        
        if not py:
            return "", ""
        
        # 检查双字母声母
        for initial in ['zh', 'ch', 'sh']:
            if py.startswith(initial):
                return initial, py[len(initial):]
        
        # 检查单字母声母
        for initial in self.INITIALS:
            if len(initial) == 1 and py.startswith(initial):
                return initial, py[1:]
        
        # 没有声母，全是韵母
        return "", py
    
    def generate_lip_keyframes(
        self,
        audio_analysis: AudioAnalysis,
        style: str = "anime"
    ) -> List[LipKeyframe]:
        """
        生成口型动画关键帧
        
        参数:
            audio_analysis: 音频分析结果
            style: 口型风格（anime=动态漫, realistic=真人）
        
        返回:
            List[LipKeyframe]: 口型关键帧序列
        """
        keyframes = []
        
        for phoneme_info in audio_analysis.phonemes:
            phoneme = phoneme_info["phoneme"]
            start_time = phoneme_info["start_time"]
            end_time = phoneme_info["end_time"]
            tone = phoneme_info.get("tone", 0)
            phoneme_type = phoneme_info.get("type", "unknown")
            
            # 获取口型形状
            mouth_shape = self._get_mouth_shape_for_phoneme(phoneme)
            
            # 根据声调和风格调整强度
            intensity = self._calculate_intensity(tone, style)
            
            # 根据音素类型调整强度
            if phoneme_type == "initial":
                # 声母通常更短促
                intensity *= 0.9
            elif phoneme_type == "final":
                # 韵母通常更持久
                intensity *= 1.0
            
            # 创建关键帧（在音素开始时）
            keyframes.append(LipKeyframe(
                timestamp=start_time,
                phoneme=phoneme,
                mouth_shape=mouth_shape,
                intensity=min(intensity, 1.0)
            ))
            
            # 在音素中间创建峰值帧（对于韵母）
            if phoneme_type == "final" and (end_time - start_time) > 0.05:
                mid_time = (start_time + end_time) / 2
                keyframes.append(LipKeyframe(
                    timestamp=mid_time,
                    phoneme=phoneme,
                    mouth_shape=mouth_shape,
                    intensity=min(intensity * 1.1, 1.0)
                ))
            
            # 在音素结束时创建过渡帧
            keyframes.append(LipKeyframe(
                timestamp=end_time,
                phoneme=phoneme,
                mouth_shape="neutral",
                intensity=0.3
            ))
        
        # 添加开始和结束的静止帧
        if keyframes:
            # 开始静止帧
            if keyframes[0].timestamp > 0:
                keyframes.insert(0, LipKeyframe(
                    timestamp=0.0,
                    phoneme="",
                    mouth_shape="neutral",
                    intensity=0.0
                ))
            
            # 结束静止帧
            last_time = keyframes[-1].timestamp
            if last_time < audio_analysis.duration:
                keyframes.append(LipKeyframe(
                    timestamp=audio_analysis.duration,
                    phoneme="",
                    mouth_shape="neutral",
                    intensity=0.0
                ))
        
        return keyframes
    
    def _get_mouth_shape_for_phoneme(self, phoneme: str) -> str:
        """
        获取音素对应的口型形状
        
        参数:
            phoneme: 音素
        
        返回:
            str: 口型形状标识
        """
        # 简化处理：直接返回默认口型
        # 实际应用中应使用拼音库将汉字转换为拼音，然后映射到口型
        return self.PHONEME_TO_MOUTH_SHAPE.get(phoneme, "neutral")
    
    def _calculate_intensity(self, tone: int, style: str) -> float:
        """
        根据声调和风格计算口型强度
        
        参数:
            tone: 声调（0-5，0表示轻声）
            style: 风格（anime或realistic）
        
        返回:
            float: 强度值（0-1）
        """
        # 基础强度
        base_intensity = 0.8
        
        # 根据声调调整
        tone_adjustment = {
            0: 0.6,  # 轻声
            1: 0.8,  # 一声
            2: 0.9,  # 二声
            3: 1.0,  # 三声
            4: 0.95, # 四声
        }
        
        intensity = tone_adjustment.get(tone, base_intensity)
        
        # 根据风格调整
        if style == "anime":
            intensity *= 1.1  # 动态漫风格更夸张
        elif style == "realistic":
            intensity *= 0.95  # 真人风格更自然
        
        return min(intensity, 1.0)
    
    def export_keyframes_for_wav2lip(
        self,
        keyframes: List[LipKeyframe],
        fps: int = 25
    ) -> List[Dict]:
        """
        将关键帧导出为Wav2Lip兼容格式
        
        参数:
            keyframes: 口型关键帧列表
            fps: 视频帧率
        
        返回:
            List[Dict]: Wav2Lip格式的帧数据
        """
        wav2lip_frames = []
        
        if not keyframes:
            return wav2lip_frames
        
        # 计算总帧数
        duration = keyframes[-1].timestamp
        total_frames = int(duration * fps)
        
        # 为每一帧生成口型参数
        for frame_idx in range(total_frames):
            timestamp = frame_idx / fps
            
            # 找到当前时间戳对应的关键帧
            current_kf = None
            next_kf = None
            
            for i, kf in enumerate(keyframes):
                if kf.timestamp <= timestamp:
                    current_kf = kf
                    if i + 1 < len(keyframes):
                        next_kf = keyframes[i + 1]
                else:
                    break
            
            if current_kf is None:
                current_kf = keyframes[0]
            
            # 插值计算当前帧的口型参数
            if next_kf and next_kf.timestamp > timestamp:
                # 线性插值
                t = (timestamp - current_kf.timestamp) / (next_kf.timestamp - current_kf.timestamp)
                intensity = current_kf.intensity * (1 - t) + next_kf.intensity * t
                mouth_shape = current_kf.mouth_shape if t < 0.5 else next_kf.mouth_shape
            else:
                intensity = current_kf.intensity
                mouth_shape = current_kf.mouth_shape
            
            wav2lip_frames.append({
                "frame": frame_idx,
                "timestamp": timestamp,
                "mouth_shape": mouth_shape,
                "intensity": intensity,
                "phoneme": current_kf.phoneme
            })
        
        return wav2lip_frames
    
    def validate_sync_accuracy(
        self,
        keyframes: List[LipKeyframe],
        audio_analysis: AudioAnalysis
    ) -> SyncAccuracyReport:
        """
        验证口型同步精度
        
        参数:
            keyframes: 口型关键帧列表
            audio_analysis: 音频分析结果
        
        返回:
            SyncAccuracyReport: 包含平均误差、最大误差、准确率、误差分布
        """
        if not keyframes or not audio_analysis.phonemes:
            return SyncAccuracyReport(0, 0, 0, 0)
        
        errors = []
        
        # 计算每个关键帧与对应音素的时间误差
        for keyframe in keyframes:
            # 跳过静止帧
            if keyframe.mouth_shape == "neutral" and keyframe.intensity < 0.1:
                continue
            
            # 找到最接近的音素
            closest_phoneme = min(
                audio_analysis.phonemes,
                key=lambda p: abs(p["start_time"] - keyframe.timestamp)
            )
            
            error_ms = abs(closest_phoneme["start_time"] - keyframe.timestamp) * 1000
            errors.append(error_ms)
        
        if not errors:
            return SyncAccuracyReport(0, 0, 1.0, 0)
        
        # 计算统计指标
        average_error = np.mean(errors)
        max_error = np.max(errors)
        min_error = np.min(errors)
        std_error = np.std(errors)
        
        # 计算准确率（误差<50ms的比例）
        accurate_count = sum(1 for e in errors if e < 50)
        accuracy_rate = accurate_count / len(errors)
        
        # 计算误差分布
        error_distribution = {
            "excellent": sum(1 for e in errors if e < 20),  # < 20ms
            "good": sum(1 for e in errors if 20 <= e < 50),  # 20-50ms
            "acceptable": sum(1 for e in errors if 50 <= e < 100),  # 50-100ms
            "poor": sum(1 for e in errors if e >= 100),  # >= 100ms
        }
        
        return SyncAccuracyReport(
            average_error_ms=float(average_error),
            max_error_ms=float(max_error),
            accuracy_rate=float(accuracy_rate),
            total_keyframes=len(keyframes),
            error_distribution=error_distribution
        )
    
    def generate_sync_report(
        self,
        keyframes: List[LipKeyframe],
        audio_analysis: AudioAnalysis,
        style: str
    ) -> Dict:
        """
        生成详细的同步报告
        
        参数:
            keyframes: 口型关键帧列表
            audio_analysis: 音频分析结果
            style: 口型风格
        
        返回:
            Dict: 详细报告
        """
        accuracy = self.validate_sync_accuracy(keyframes, audio_analysis)
        
        report = {
            "summary": {
                "total_duration": audio_analysis.duration,
                "total_phonemes": len(audio_analysis.phonemes),
                "total_keyframes": len(keyframes),
                "style": style,
                "transcript": audio_analysis.transcript
            },
            "accuracy": accuracy.to_dict(),
            "recommendations": self._generate_recommendations(accuracy)
        }
        
        return report
    
    def _generate_recommendations(self, accuracy: SyncAccuracyReport) -> List[str]:
        """
        根据精度报告生成改进建议
        
        参数:
            accuracy: 精度报告
        
        返回:
            List[str]: 建议列表
        """
        recommendations = []
        
        if accuracy.average_error_ms > 50:
            recommendations.append("平均误差较大，建议使用更高质量的音频文件")
            recommendations.append("考虑使用更精确的语音识别模型（如Whisper large）")
        
        if accuracy.accuracy_rate < 0.8:
            recommendations.append("准确率较低，建议检查音频质量和背景噪音")
        
        if accuracy.max_error_ms > 100:
            recommendations.append("存在较大的时间偏差，建议手动调整关键帧")
        
        if accuracy.quality_score >= 90:
            recommendations.append("同步质量优秀，可以直接使用")
        elif accuracy.quality_score >= 70:
            recommendations.append("同步质量良好，建议进行微调以获得更好效果")
        
        return recommendations


# 全局引擎实例（单例模式）
_engine_instance: Optional[ChineseLipSyncEngine] = None


def get_lip_sync_engine(whisper_model: str = "base") -> ChineseLipSyncEngine:
    """
    获取口型同步引擎实例（单例）
    
    参数:
        whisper_model: Whisper模型名称
    
    返回:
        ChineseLipSyncEngine: 引擎实例
    """
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = ChineseLipSyncEngine(whisper_model_name=whisper_model)
    return _engine_instance
