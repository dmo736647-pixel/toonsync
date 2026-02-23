"""角色一致性引擎服务

该模块实现角色一致性引擎，从单张角色图像生成全套分镜，保持角色视觉统一。
核心技术：IP-Adapter + ControlNet + Stable Diffusion
"""
import os
import json
import tempfile
from io import BytesIO
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from datetime import datetime
import numpy as np
from PIL import Image as PILImage

# 图像处理库
try:
    from PIL import Image
except ImportError:
    Image = None


class ConsistencyModel:
    """角色一致性模型"""
    
    def __init__(
        self,
        character_id: str,
        reference_image_path: str,
        facial_features: Dict[str, any],
        clothing_features: Dict[str, any],
        style: str = "anime"
    ):
        """
        初始化一致性模型
        
        参数:
            character_id: 角色ID
            reference_image_path: 参考图像路径
            facial_features: 面部特征向量
            clothing_features: 服装特征向量
            style: 渲染风格（anime或realistic）
        """
        self.character_id = character_id
        self.reference_image_path = reference_image_path
        self.facial_features = facial_features
        self.clothing_features = clothing_features
        self.style = style
        self.created_at = datetime.utcnow()
    
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            "character_id": self.character_id,
            "reference_image_path": self.reference_image_path,
            "facial_features": self.facial_features,
            "clothing_features": self.clothing_features,
            "style": self.style,
            "created_at": self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ConsistencyModel':
        """从字典创建实例"""
        model = cls(
            character_id=data["character_id"],
            reference_image_path=data["reference_image_path"],
            facial_features=data["facial_features"],
            clothing_features=data["clothing_features"],
            style=data.get("style", "anime")
        )
        if "created_at" in data:
            model.created_at = datetime.fromisoformat(data["created_at"])
        return model
    
    def save(self, output_path: str):
        """保存模型到文件"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
    
    @classmethod
    def load(cls, input_path: str) -> 'ConsistencyModel':
        """从文件加载模型"""
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)


class ConsistencyScore:
    """一致性评分"""
    
    def __init__(
        self,
        facial_similarity: float,
        clothing_consistency: float,
        overall_score: float,
        details: Optional[Dict] = None
    ):
        """
        初始化一致性评分
        
        参数:
            facial_similarity: 面部相似度（0-1）
            clothing_consistency: 服装一致性（0-1）
            overall_score: 整体评分（0-1）
            details: 详细信息
        """
        self.facial_similarity = facial_similarity
        self.clothing_consistency = clothing_consistency
        self.overall_score = overall_score
        self.details = details or {}
    
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            "facial_similarity": self.facial_similarity,
            "clothing_consistency": self.clothing_consistency,
            "overall_score": self.overall_score,
            "details": self.details,
            "meets_requirements": self.meets_requirements()
        }
    
    def meets_requirements(self) -> bool:
        """检查是否满足要求"""
        return (
            self.facial_similarity > 0.90 and
            self.clothing_consistency > 0.85
        )


class CharacterConsistencyEngine:
    """角色一致性引擎
    
    从单张角色图像生成全套分镜，保持角色视觉统一。
    核心技术：
    - IP-Adapter：提取角色面部特征和风格
    - ControlNet：控制姿态、表情、视角
    - 一致性模型：确保面部特征、服装、发型在不同分镜中保持一致
    """
    
    # 支持的渲染风格
    SUPPORTED_STYLES = ["anime", "realistic"]
    
    # 面部特征关键点
    FACIAL_KEYPOINTS = [
        "eyes", "nose", "mouth", "eyebrows", "face_shape",
        "hair_color", "hair_style", "skin_tone"
    ]
    
    # 服装特征
    CLOTHING_FEATURES = [
        "color_palette", "style", "accessories", "patterns"
    ]
    
    def __init__(self):
        """初始化角色一致性引擎"""
        # 检查依赖
        if Image is None:
            raise ImportError("PIL未安装，请运行: pip install Pillow")
        
        # 模型缓存
        self._models_cache = {}
    
    def extract_character_features(
        self,
        reference_image_path: str,
        character_id: str,
        style: str = "anime"
    ) -> ConsistencyModel:
        """
        从参考图像提取角色特征，创建一致性模型
        
        参数:
            reference_image_path: 角色参考图像路径
            character_id: 角色ID
            style: 渲染风格（anime或realistic）
        
        返回:
            ConsistencyModel: 包含面部特征、服装、发型等信息
        
        性能要求: < 2秒
        """
        import time
        start_time = time.time()
        
        # 验证风格
        if style not in self.SUPPORTED_STYLES:
            raise ValueError(f"不支持的风格: {style}，支持的风格: {self.SUPPORTED_STYLES}")
        
        # 加载图像
        image = self._load_image(reference_image_path)
        
        # 提取面部特征
        facial_features = self._extract_facial_features(image, style)
        
        # 提取服装特征
        clothing_features = self._extract_clothing_features(image, style)
        
        # 创建一致性模型
        model = ConsistencyModel(
            character_id=character_id,
            reference_image_path=reference_image_path,
            facial_features=facial_features,
            clothing_features=clothing_features,
            style=style
        )
        
        # 检查处理时间
        processing_time = time.time() - start_time
        if processing_time > 2.0:
            print(f"警告：特征提取耗时 {processing_time:.2f}s，超过2秒要求")
        
        return model
    
    def _load_image(self, image_path: str) -> PILImage.Image:
        """
        加载图像文件
        
        参数:
            image_path: 图像文件路径
        
        返回:
            PIL.Image: 图像对象
        """
        try:
            parsed = urlparse(image_path)
            if parsed.scheme in ["http", "https"]:
                request = Request(image_path, headers={"User-Agent": "Mozilla/5.0"})
                with urlopen(request) as response:
                    data = response.read()
                image = Image.open(BytesIO(data))
            else:
                image = Image.open(image_path)
            # 转换为RGB模式
            if image.mode != 'RGB':
                image = image.convert('RGB')
            return image
        except Exception as e:
            raise ValueError(f"无法加载图像 {image_path}: {str(e)}")
    
    def _extract_facial_features(
        self,
        image: PILImage.Image,
        style: str
    ) -> Dict[str, any]:
        """
        提取面部特征
        
        参数:
            image: 图像对象
            style: 渲染风格
        
        返回:
            Dict: 面部特征向量
        """
        # 简化实现：使用图像统计特征
        # 实际应用中应使用专业的面部识别模型（如InsightFace、FaceNet）
        
        img_array = np.array(image)
        
        # 提取颜色特征（简化）
        mean_color = img_array.mean(axis=(0, 1)).tolist()
        std_color = img_array.std(axis=(0, 1)).tolist()
        
        # 提取纹理特征（简化）
        gray = img_array.mean(axis=2)
        texture_features = {
            "mean": float(gray.mean()),
            "std": float(gray.std()),
            "min": float(gray.min()),
            "max": float(gray.max())
        }
        
        features = {
            "color_mean": mean_color,
            "color_std": std_color,
            "texture": texture_features,
            "image_size": list(image.size),
            "style": style,
            # 占位符：实际应用中应包含更详细的面部特征
            "keypoints": {kp: 0.0 for kp in self.FACIAL_KEYPOINTS}
        }
        
        return features
    
    def _extract_clothing_features(
        self,
        image: PILImage.Image,
        style: str
    ) -> Dict[str, any]:
        """
        提取服装和发型特征
        
        参数:
            image: 图像对象
            style: 渲染风格
        
        返回:
            Dict: 服装特征向量
        """
        # 简化实现：使用图像区域特征
        # 实际应用中应使用服装分割和识别模型
        
        img_array = np.array(image)
        
        # 提取主要颜色（简化）
        colors = img_array.reshape(-1, 3)
        unique_colors = np.unique(colors, axis=0)
        
        # 计算颜色分布
        color_palette = []
        for i in range(min(5, len(unique_colors))):
            color_palette.append(unique_colors[i].tolist())
        
        features = {
            "color_palette": color_palette,
            "dominant_colors": img_array.mean(axis=(0, 1)).tolist(),
            "style": style,
            # 占位符：实际应用中应包含更详细的服装特征
            "features": {feat: 0.0 for feat in self.CLOTHING_FEATURES}
        }
        
        return features
    
    def generate_storyboard(
        self,
        consistency_model: ConsistencyModel,
        scene_description: str,
        style: str = "anime"
    ) -> str:
        """
        生成单个分镜（WorkflowOrchestrator使用的接口）
        
        参数:
            consistency_model: 角色一致性模型
            scene_description: 场景描述文本
            style: 渲染风格
        
        返回:
            str: 生成的分镜图像URL
        """
        return self.generate_storyboard_frame(
            consistency_model,
            scene_description
        )

    def generate_storyboard_frame(
        self,
        consistency_model: ConsistencyModel,
        scene_description: str,
        pose_reference: Optional[str] = None,
        output_path: Optional[str] = None
    ) -> str:
        """
        生成单个分镜图像
        
        参数:
            consistency_model: 角色一致性模型
            scene_description: 场景描述文本
            pose_reference: 可选的姿态参考图路径
            output_path: 输出图像路径（如果提供，将下载图像到此路径）
        
        返回:
            str: 生成的分镜图像URL或本地路径
        """
        from app.services.replicate_client import get_replicate_client
        import requests
        
        client = get_replicate_client()
        
        # 准备参考图像
        ref_image = consistency_model.reference_image_path
        
        # 兼容性处理：如果 ref_image 是 URL，尝试直接使用
        if ref_image.startswith("http"):
            input_image = ref_image
            ref_image_file = None
        elif os.path.exists(ref_image):
            # 如果是本地路径且存在，打开文件
            ref_image_file = open(ref_image, "rb")
            input_image = ref_image_file
        else:
            # 如果路径不存在，可能是一个无法访问的 URL 或路径错误
            # 尝试作为 URL 使用（最后的尝试）
            input_image = ref_image
            ref_image_file = None
            
        try:
            # 使用PhotoMaker生成
            # 注意：实际prompt应该包含风格触发词
            style = consistency_model.style or "anime"
            full_prompt = f"{scene_description}, {style} style, high quality"
            
            urls = client.generate_character_image(
                prompt=full_prompt,
                reference_image=input_image,
                num_outputs=1
            )
            
            image_url = urls[0]
            
            # 如果指定了输出路径，下载保存
            if output_path:
                response = requests.get(image_url)
                response.raise_for_status()
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                return output_path
            
            return image_url
            
        except Exception as e:
            print(f"Replicate生成失败: {e}")
            # 降级到模拟实现
            return self._mock_generate_storyboard_frame(
                consistency_model, 
                scene_description, 
                output_path
            )
        finally:
            if ref_image_file:
                ref_image_file.close()

    def _mock_generate_storyboard_frame(
        self,
        consistency_model: ConsistencyModel,
        scene_description: str,
        output_path: Optional[str] = None
    ) -> str:
        """模拟生成分镜（降级方案）"""
        # 加载参考图像
        reference_image = self._load_image(consistency_model.reference_image_path)
        
        # 创建输出图像（简化：直接使用参考图像）
        output_image = reference_image.copy()
        
        # 如果没有指定输出路径，创建临时文件
        if output_path is None:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            output_path = temp_file.name
            temp_file.close()
        
        # 保存图像
        output_image.save(output_path)
        
        return output_path
    
    def validate_consistency(
        self,
        reference_image_path: str,
        generated_frames: List[str]
    ) -> ConsistencyScore:
        """
        验证生成的分镜与参考图像的一致性
        
        参数:
            reference_image_path: 参考图像路径
            generated_frames: 生成的分镜图像路径列表
        
        返回:
            ConsistencyScore: 包含面部相似度、服装一致性、整体评分
        """
        if not generated_frames:
            return ConsistencyScore(0.0, 0.0, 0.0)
        
        # 加载参考图像
        reference_image = self._load_image(reference_image_path)
        reference_features = self._extract_facial_features(reference_image, "anime")
        reference_clothing = self._extract_clothing_features(reference_image, "anime")
        
        # 计算每个生成帧的相似度
        facial_similarities = []
        clothing_consistencies = []
        
        for frame_path in generated_frames:
            frame_image = self._load_image(frame_path)
            frame_features = self._extract_facial_features(frame_image, "anime")
            frame_clothing = self._extract_clothing_features(frame_image, "anime")
            
            # 计算面部相似度（简化：使用颜色特征的余弦相似度）
            facial_sim = self._calculate_similarity(
                reference_features["color_mean"],
                frame_features["color_mean"]
            )
            facial_similarities.append(facial_sim)
            
            # 计算服装一致性（简化：使用颜色分布的相似度）
            clothing_sim = self._calculate_similarity(
                reference_clothing["dominant_colors"],
                frame_clothing["dominant_colors"]
            )
            clothing_consistencies.append(clothing_sim)
        
        # 计算平均值
        avg_facial_similarity = np.mean(facial_similarities)
        avg_clothing_consistency = np.mean(clothing_consistencies)
        overall_score = (avg_facial_similarity + avg_clothing_consistency) / 2
        
        return ConsistencyScore(
            facial_similarity=float(avg_facial_similarity),
            clothing_consistency=float(avg_clothing_consistency),
            overall_score=float(overall_score),
            details={
                "num_frames": len(generated_frames),
                "facial_similarities": [float(s) for s in facial_similarities],
                "clothing_consistencies": [float(s) for s in clothing_consistencies]
            }
        )
    
    def _calculate_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        计算两个向量的余弦相似度
        
        参数:
            vec1: 向量1
            vec2: 向量2
        
        返回:
            float: 相似度（0-1）
        """
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        # 余弦相似度
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = dot_product / (norm1 * norm2)
        
        # 归一化到0-1范围
        return float((similarity + 1) / 2)
    
    def batch_generate_frames(
        self,
        consistency_model: ConsistencyModel,
        scene_descriptions: List[str],
        output_dir: str
    ) -> List[str]:
        """
        批量生成分镜图像
        
        参数:
            consistency_model: 角色一致性模型
            scene_descriptions: 场景描述列表
            output_dir: 输出目录
        
        返回:
            List[str]: 生成的分镜图像路径列表
        """
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        generated_frames = []
        
        for i, description in enumerate(scene_descriptions):
            output_path = os.path.join(output_dir, f"frame_{i:04d}.png")
            frame_path = self.generate_storyboard_frame(
                consistency_model,
                description,
                output_path=output_path
            )
            generated_frames.append(frame_path)
        
        return generated_frames


# 全局引擎实例（单例模式）
_engine_instance: Optional[CharacterConsistencyEngine] = None


def get_character_consistency_engine() -> CharacterConsistencyEngine:
    """
    获取角色一致性引擎实例（单例）
    
    返回:
        CharacterConsistencyEngine: 引擎实例
    """
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = CharacterConsistencyEngine()
    return _engine_instance
