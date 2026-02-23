"""ElevenLabs TTS服务 - 全球化语音合成"""
import httpx
import asyncio
from typing import Optional, Dict, Any, List
from app.core.config import settings
import logging
import azure.cognitiveservices.speech as speechsdk

logger = logging.getLogger(__name__)


class ElevenLabsTTSService:
    """ElevenLabs TTS服务"""
    
    def __init__(self):
        self.api_key = settings.ELEVENLABS_API_KEY
        self.base_url = "https://api.elevenlabs.io/v1"
        self.headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
    
    async def get_voices(self) -> List[Dict[str, Any]]:
        """获取可用语音列表"""
        if not self.api_key:
            logger.warning("ElevenLabs API key not configured")
            return []
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/voices",
                    headers={"xi-api-key": self.api_key}
                )
                response.raise_for_status()
                data = response.json()
                return data.get("voices", [])
        except Exception as e:
            logger.error(f"Failed to get ElevenLabs voices: {e}")
            return []
    
    async def text_to_speech(
        self,
        text: str,
        voice_id: str = "21m00Tcm4TlvDq8ikWAM",  # Rachel voice (default)
        model_id: str = "eleven_multilingual_v2",
        voice_settings: Optional[Dict[str, float]] = None
    ) -> Optional[bytes]:
        """文本转语音"""
        if not self.api_key:
            logger.warning("ElevenLabs API key not configured")
            return None
        
        if voice_settings is None:
            voice_settings = {
                "stability": 0.5,
                "similarity_boost": 0.5,
                "style": 0.0,
                "use_speaker_boost": True
            }
        
        payload = {
            "text": text,
            "model_id": model_id,
            "voice_settings": voice_settings
        }
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/text-to-speech/{voice_id}",
                    json=payload,
                    headers=self.headers
                )
                response.raise_for_status()
                return response.content
        except Exception as e:
            logger.error(f"ElevenLabs TTS failed: {e}")
            return None
    
    async def get_voice_by_language(self, language: str) -> Optional[str]:
        """根据语言获取推荐语音ID"""
        voice_mapping = {
            "en": "21m00Tcm4TlvDq8ikWAM",  # Rachel - English
            "es": "XB0fDUnXU5powFXDhCwa",  # Charlotte - Spanish
            "fr": "ThT5KcBeYPX3keUQqHPh",  # Dorothy - French
            "de": "TxGEqnHWrfWFTfGW9XjX",  # Josh - German
            "it": "XB0fDUnXU5powFXDhCwa",  # Charlotte - Italian
            "pt": "XB0fDUnXU5powFXDhCwa",  # Charlotte - Portuguese
        }
        return voice_mapping.get(language, "21m00Tcm4TlvDq8ikWAM")
    
    async def generate_speech_for_language(
        self,
        text: str,
        language: str = "en",
        emotion: str = "neutral"
    ) -> Optional[bytes]:
        """为特定语言生成语音"""
        voice_id = await self.get_voice_by_language(language)
        
        # 根据情感调整语音设置
        voice_settings = self._get_voice_settings_for_emotion(emotion)
        
        return await self.text_to_speech(
            text=text,
            voice_id=voice_id,
            voice_settings=voice_settings
        )
    
    def _get_voice_settings_for_emotion(self, emotion: str) -> Dict[str, float]:
        """根据情感获取语音设置"""
        emotion_settings = {
            "neutral": {
                "stability": 0.5,
                "similarity_boost": 0.5,
                "style": 0.0,
                "use_speaker_boost": True
            },
            "happy": {
                "stability": 0.3,
                "similarity_boost": 0.7,
                "style": 0.3,
                "use_speaker_boost": True
            },
            "sad": {
                "stability": 0.7,
                "similarity_boost": 0.3,
                "style": 0.1,
                "use_speaker_boost": True
            },
            "angry": {
                "stability": 0.2,
                "similarity_boost": 0.8,
                "style": 0.5,
                "use_speaker_boost": True
            },
            "excited": {
                "stability": 0.1,
                "similarity_boost": 0.9,
                "style": 0.7,
                "use_speaker_boost": True
            }
        }
        return emotion_settings.get(emotion, emotion_settings["neutral"])


class AzureTTSService:
    """Azure TTS服务（用于中文、日文、韩文）"""
    
    def __init__(self):
        self.speech_key = settings.AZURE_SPEECH_KEY
        self.speech_region = settings.AZURE_SPEECH_REGION
        
    def text_to_speech(
        self,
        text: str,
        language: str = "zh-CN",
        voice_name: str = "zh-CN-XiaoxiaoNeural"
    ) -> Optional[bytes]:
        """文本转语音"""
        if not self.speech_key:
            logger.warning("Azure Speech key not configured")
            return None
        
        try:
            # 创建语音配置
            speech_config = speechsdk.SpeechConfig(
                subscription=self.speech_key,
                region=self.speech_region
            )
            
            # 设置输出格式
            speech_config.set_speech_synthesis_output_format(
                speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3
            )
            
            # 创建语音合成器
            speech_synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=speech_config,
                audio_config=None  # 内存流
            )
            
            # 合成语音
            result = speech_synthesizer.speak_text_async(text).get()
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                return result.audio_data
            else:
                logger.error(f"Azure TTS failed: {result.reason}")
                return None
        except Exception as e:
            logger.error(f"Azure TTS exception: {e}")
            return None
    
    def get_voice_by_language(self, language: str) -> str:
        """根据语言获取推荐语音"""
        voice_mapping = {
            "zh": "zh-CN-XiaoxiaoNeural",  # 中文 - 晓晓
            "ja": "ja-JP-AoiNeural",     # 日文 - 葵
            "ko": "ko-KR-SunHiNeural"     # 韩文 - 孙喜
        }
        return voice_mapping.get(language, "zh-CN-XiaoxiaoNeural")
    
    def generate_speech_for_language(
        self,
        text: str,
        language: str = "zh",
        emotion: str = "neutral"
    ) -> Optional[bytes]:
        """为特定语言生成语音"""
        voice_name = self.get_voice_by_language(language)
        
        # Azure TTS通过语音名称来表现情感
        # 这里可以根据情感选择不同的语音
        if emotion == "happy" and language == "zh":
            voice_name = "zh-CN-YunxiNeural"  # 云希（更欢快）
        elif emotion == "sad" and language == "zh":
            voice_name = "zh-CN-YunxiaNeural"  # 云夏（更柔和）
        
        return self.text_to_speech(
            text=text,
            language=f"{language}-{language.upper()}",
            voice_name=voice_name
        )


class MultiLanguageTTSService:
    """多语言TTS服务协调器"""
    
    def __init__(self):
        self.elevenlabs = ElevenLabsTTSService()
        self.azure = AzureTTSService()
        # 可以在这里添加其他TTS服务（Google等）
    
    async def generate_speech(
        self,
        text: str,
        language: str = "en",
        emotion: str = "neutral",
        provider: Optional[str] = None
    ) -> Optional[bytes]:
        """生成语音（自动选择最佳提供商）"""
        
        # 如果没有指定提供商，根据语言自动选择
        if provider is None:
            provider = settings.TTS_PROVIDERS.get(language, "elevenlabs")
        
        if provider == "elevenlabs":
            return await self.elevenlabs.generate_speech_for_language(
                text=text,
                language=language,
                emotion=emotion
            )
        elif provider == "azure":
            # 使用Azure TTS服务
            return self.azure.generate_speech_for_language(
                text=text,
                language=language,
                emotion=emotion
            )
        else:
            logger.error(f"Unknown TTS provider: {provider}")
            return None
    
    async def get_supported_languages(self) -> List[str]:
        """获取支持的语言列表"""
        return list(settings.TTS_PROVIDERS.keys())
    
    async def get_available_voices(self, language: str) -> List[Dict[str, Any]]:
        """获取指定语言的可用语音"""
        provider = settings.TTS_PROVIDERS.get(language, "elevenlabs")
        
        if provider == "elevenlabs":
            voices = await self.elevenlabs.get_voices()
            # 过滤出支持指定语言的语音
            return [
                voice for voice in voices 
                if language in voice.get("labels", {}).get("language", "")
            ]
        else:
            return []


# 全局实例
tts_service = MultiLanguageTTSService()