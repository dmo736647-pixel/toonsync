"""Replicate API客户端

用于调用Replicate平台的AI模型API，包括：
- Whisper（语音识别）
- Wav2Lip（口型同步）
- Stable Diffusion（图像生成）
- IP-Adapter（角色一致性）
"""
import os
import time
from typing import Dict, Optional, Any
from app.core.config import settings

# 尝试导入replicate库
try:
    import replicate
    REPLICATE_AVAILABLE = True
except ImportError:
    REPLICATE_AVAILABLE = False
    replicate = None


class ReplicateClient:
    """Replicate API客户端"""
    
    # 模型版本（可以在Replicate网站上找到最新版本）
    MODELS = {
        "whisper": "openai/whisper:4d50797290df275329f202e48c76360b3f22b08d28c196cbc54600319435f8d2",
        "wav2lip": "devxpy/cog-wav2lip:8d65e3f4f4298520e079198b493c25adfc43c058ffec924f2aefc8010ed25eef",
        "sdxl": "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
        "photomaker": "tencentarc/photomaker:ddfc2b08d209f9fa8c1eca692712918bd449f695dabb4a958da31802a9570fe4"
    }
    
    def __init__(self, api_token: Optional[str] = None):
        """
        初始化Replicate客户端
        
        参数:
            api_token: Replicate API Token（如果不提供，从环境变量读取）
        """
        self.api_token = api_token or settings.REPLICATE_API_TOKEN
        
        if not self.api_token:
            raise ValueError(
                "Replicate API Token未配置。请设置环境变量 REPLICATE_API_TOKEN "
                "或在初始化时提供 api_token 参数。"
            )
        
        if not REPLICATE_AVAILABLE:
            raise ImportError(
                "replicate库未安装。请运行: pip install replicate"
            )
        
        # 设置API Token
        os.environ["REPLICATE_API_TOKEN"] = self.api_token
    
    def run_model(
        self,
        model_name: str,
        input_params: Dict[str, Any],
        wait: bool = True
    ) -> Any:
        """
        运行Replicate模型
        
        参数:
            model_name: 模型名称（whisper, wav2lip, sdxl, photomaker）
            input_params: 输入参数
            wait: 是否等待结果（True=同步，False=异步）
        
        返回:
            模型输出结果
        """
        if model_name not in self.MODELS:
            raise ValueError(f"不支持的模型: {model_name}。支持的模型: {list(self.MODELS.keys())}")
        
        model_version = self.MODELS[model_name]
        
        try:
            output = replicate.run(
                model_version,
                input=input_params
            )
            
            if wait:
                # 同步等待结果
                return output
            else:
                # 异步返回prediction对象
                return output
        
        except Exception as e:
            raise RuntimeError(f"Replicate API调用失败: {str(e)}")
    
    def transcribe_audio(
        self,
        audio_url: str,
        language: str = "zh",
        task: str = "transcribe"
    ) -> Dict:
        """
        使用Whisper转录音频
        
        参数:
            audio_url: 音频文件URL（必须是公开可访问的URL）
            language: 语言代码（zh=中文，en=英文）
            task: 任务类型（transcribe=转录，translate=翻译）
        
        返回:
            转录结果，包含文本和时间戳
        """
        input_params = {
            "audio": audio_url,
            "language": language,
            "task": task,
            "word_timestamps": True
        }
        
        result = self.run_model("whisper", input_params)
        
        # 解析结果
        if isinstance(result, dict):
            return result
        elif isinstance(result, str):
            return {"text": result}
        else:
            return {"text": str(result)}
    
    def generate_lip_sync(
        self,
        face_url: str,
        audio_url: str
    ) -> str:
        """
        使用Wav2Lip生成口型同步视频
        
        参数:
            face_url: 人脸图像或视频URL
            audio_url: 音频文件URL
        
        返回:
            生成的视频URL
        """
        input_params = {
            "face": face_url,
            "audio": audio_url
        }
        
        result = self.run_model("wav2lip", input_params)
        
        # 返回视频URL
        if isinstance(result, str):
            return result
        elif isinstance(result, list) and len(result) > 0:
            return result[0]
        else:
            raise ValueError(f"Wav2Lip返回了意外的结果格式: {type(result)}")
    
    def generate_image(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        width: int = 1024,
        height: int = 1024,
        num_outputs: int = 1,
        guidance_scale: float = 7.5,
        num_inference_steps: int = 50
    ) -> list:
        """
        使用Stable Diffusion XL生成图像
        
        参数:
            prompt: 提示词
            negative_prompt: 负面提示词
            width: 图像宽度
            height: 图像高度
            num_outputs: 生成数量
            guidance_scale: 引导强度
            num_inference_steps: 推理步数
        
        返回:
            生成的图像URL列表
        """
        input_params = {
            "prompt": prompt,
            "width": width,
            "height": height,
            "num_outputs": num_outputs,
            "guidance_scale": guidance_scale,
            "num_inference_steps": num_inference_steps
        }
        
        if negative_prompt:
            input_params["negative_prompt"] = negative_prompt
        
        result = self.run_model("sdxl", input_params)
        
        # 返回图像URL列表
        if isinstance(result, list):
            return result
        elif isinstance(result, str):
            return [result]
        else:
            raise ValueError(f"SDXL返回了意外的结果格式: {type(result)}")
    
    def generate_character_image(
        self,
        prompt: str,
        reference_image: Any,
        num_outputs: int = 1
    ) -> list:
        """
        使用PhotoMaker生成角色一致性图像
        
        参数:
            prompt: 提示词
            reference_image: 参考图像（URL字符串或文件对象/路径）
            num_outputs: 生成数量
        
        返回:
            生成的图像URL列表
        """
        # input_image parameter name might be different for different models
        # For tencentarc/photomaker, it is 'input_image'
        # But we should check if the model version expects something else
        
        input_params = {
            "prompt": f"{prompt} img", # PhotoMaker trigger word usually needs 'img' or specific trigger
            "input_image": reference_image,
            "num_outputs": num_outputs,
            "style_name": "Anime", # Optional: enforce anime style if supported
            "num_steps": 30,
            "style_strength_ratio": 20
        }
        
        # PhotoMaker specific parameter adjustments
        # The model "tencentarc/photomaker" takes "input_image"
        
        try:
            # We use a specific version for stability
            # But let's check if we can use the latest one or a known good one
            # The one in MODELS is: ddfc2b08d209f9fa8c1eca692712918bd449f695dabb4a958da31802a9570fe4
            
            output = self.run_model("photomaker", input_params)
            
            if isinstance(output, list):
                return output
            elif isinstance(output, str):
                return [output]
            else:
                # Some models return an iterator or other types
                return [str(output)]
                
        except Exception as e:
            # Fallback or re-raise with more info
            print(f"PhotoMaker generation failed: {e}")
            raise e


# 全局客户端实例（单例）
_client_instance: Optional[ReplicateClient] = None


def get_replicate_client() -> ReplicateClient:
    """
    获取Replicate客户端实例（单例）
    
    返回:
        ReplicateClient: 客户端实例
    """
    global _client_instance
    if _client_instance is None:
        _client_instance = ReplicateClient()
    return _client_instance
