"""
智能音效匹配器服务

实现剧本解析、音效推荐和自动放置功能。
"""
import re
import json
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import numpy as np


class SceneType(str, Enum):
    """场景类型枚举"""
    ACTION = "action"  # 动作场景
    DIALOGUE = "dialogue"  # 对话场景
    ENVIRONMENT = "environment"  # 环境场景
    EMOTIONAL = "emotional"  # 情感场景
    TRANSITION = "transition"  # 转场


class EmotionType(str, Enum):
    """情感类型枚举"""
    HAPPY = "happy"  # 快乐
    SAD = "sad"  # 悲伤
    ANGRY = "angry"  # 愤怒
    FEAR = "fear"  # 恐惧
    SURPRISE = "surprise"  # 惊讶
    NEUTRAL = "neutral"  # 中性


@dataclass
class SceneSegment:
    """场景片段"""
    scene_id: str
    text: str
    scene_type: SceneType
    actions: List[str]
    emotions: List[EmotionType]
    characters: List[str]
    start_time: float  # 秒
    duration: float  # 秒
    keywords: List[str]
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "scene_id": self.scene_id,
            "text": self.text,
            "scene_type": self.scene_type.value,
            "actions": self.actions,
            "emotions": [e.value for e in self.emotions],
            "characters": self.characters,
            "start_time": self.start_time,
            "duration": self.duration,
            "keywords": self.keywords
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "SceneSegment":
        """从字典创建"""
        return cls(
            scene_id=data["scene_id"],
            text=data["text"],
            scene_type=SceneType(data["scene_type"]),
            actions=data["actions"],
            emotions=[EmotionType(e) for e in data["emotions"]],
            characters=data["characters"],
            start_time=data["start_time"],
            duration=data["duration"],
            keywords=data["keywords"]
        )


@dataclass
class SoundEffect:
    """音效"""
    effect_id: str
    name: str
    description: str
    category: str
    tags: List[str]
    duration: float  # 秒
    file_url: str
    embedding: Optional[List[float]] = None  # 向量表示
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "effect_id": self.effect_id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "tags": self.tags,
            "duration": self.duration,
            "file_url": self.file_url,
            "embedding": self.embedding
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "SoundEffect":
        """从字典创建"""
        return cls(
            effect_id=data["effect_id"],
            name=data["name"],
            description=data["description"],
            category=data["category"],
            tags=data["tags"],
            duration=data["duration"],
            file_url=data["file_url"],
            embedding=data.get("embedding")
        )


class ScriptParser:
    """剧本解析器"""
    
    # 动作关键词
    ACTION_KEYWORDS = [
        "打", "跑", "跳", "推", "拉", "扔", "抓", "踢", "击", "砸",
        "fight", "run", "jump", "push", "pull", "throw", "grab", "kick"
    ]
    
    # 情感关键词
    EMOTION_KEYWORDS = {
        EmotionType.HAPPY: ["笑", "开心", "高兴", "快乐", "喜悦", "happy", "smile", "joy"],
        EmotionType.SAD: ["哭", "伤心", "难过", "悲伤", "痛苦", "sad", "cry", "pain"],
        EmotionType.ANGRY: ["怒", "生气", "愤怒", "恼火", "angry", "mad", "furious"],
        EmotionType.FEAR: ["怕", "害怕", "恐惧", "惊恐", "fear", "scared", "afraid"],
        EmotionType.SURPRISE: ["惊", "惊讶", "吃惊", "震惊", "surprise", "shocked", "amazed"],
    }
    
    # 环境关键词
    ENVIRONMENT_KEYWORDS = [
        "室内", "室外", "街道", "房间", "办公室", "公园", "森林", "海边",
        "indoor", "outdoor", "street", "room", "office", "park", "forest", "beach"
    ]
    
    def parse_script(self, script: str) -> List[SceneSegment]:
        """
        解析剧本，提取场景片段
        
        参数:
            script: 剧本文本
        
        返回:
            场景片段列表
        """
        if not script or not script.strip():
            return []
        
        # 按场景分割（假设场景以"场景"或"Scene"开头）
        scene_pattern = r'(?:场景|Scene)\s*\d+|^.+?(?=场景|Scene|\Z)'
        scenes = re.split(scene_pattern, script, flags=re.MULTILINE | re.IGNORECASE)
        scenes = [s.strip() for s in scenes if s.strip()]
        
        # 如果没有明确的场景标记，按段落分割
        if len(scenes) <= 1:
            scenes = [p.strip() for p in script.split('\n\n') if p.strip()]
        
        segments = []
        current_time = 0.0
        
        for i, scene_text in enumerate(scenes):
            if not scene_text:
                continue
            
            # 提取场景信息
            scene_type = self._detect_scene_type(scene_text)
            actions = self._extract_actions(scene_text)
            emotions = self._extract_emotions(scene_text)
            characters = self._extract_characters(scene_text)
            keywords = self._extract_keywords(scene_text)
            
            # 估算场景时长（基于文本长度）
            duration = max(3.0, len(scene_text) / 50)  # 假设每50字约1秒
            
            segment = SceneSegment(
                scene_id=f"scene_{i+1}",
                text=scene_text,
                scene_type=scene_type,
                actions=actions,
                emotions=emotions,
                characters=characters,
                start_time=current_time,
                duration=duration,
                keywords=keywords
            )
            
            segments.append(segment)
            current_time += duration
        
        return segments
    
    def _detect_scene_type(self, text: str) -> SceneType:
        """检测场景类型"""
        text_lower = text.lower()
        
        # 检查动作关键词
        action_count = sum(1 for kw in self.ACTION_KEYWORDS if kw in text_lower)
        
        # 检查对话标记
        dialogue_count = text.count('"') + text.count('"') + text.count('"') + text.count(':')
        
        # 检查环境关键词
        env_count = sum(1 for kw in self.ENVIRONMENT_KEYWORDS if kw in text_lower)
        
        # 检查情感关键词
        emotion_count = sum(
            sum(1 for kw in keywords if kw in text_lower)
            for keywords in self.EMOTION_KEYWORDS.values()
        )
        
        # 根据关键词数量判断场景类型
        if action_count >= 2:
            return SceneType.ACTION
        elif dialogue_count >= 2:
            return SceneType.DIALOGUE
        elif env_count >= 1:
            return SceneType.ENVIRONMENT
        elif emotion_count >= 2:
            return SceneType.EMOTIONAL
        else:
            return SceneType.TRANSITION
    
    def _extract_actions(self, text: str) -> List[str]:
        """提取动作"""
        text_lower = text.lower()
        actions = []
        
        for keyword in self.ACTION_KEYWORDS:
            if keyword in text_lower:
                actions.append(keyword)
        
        return list(set(actions))[:5]  # 最多返回5个
    
    def _extract_emotions(self, text: str) -> List[EmotionType]:
        """提取情感"""
        text_lower = text.lower()
        emotions = []
        
        for emotion, keywords in self.EMOTION_KEYWORDS.items():
            if any(kw in text_lower for kw in keywords):
                emotions.append(emotion)
        
        if not emotions:
            emotions.append(EmotionType.NEUTRAL)
        
        return emotions
    
    def _extract_characters(self, text: str) -> List[str]:
        """提取角色名（简化实现）"""
        # 查找对话标记前的名字
        pattern = r'([A-Za-z\u4e00-\u9fa5]+)\s*[:：]'
        matches = re.findall(pattern, text)
        
        characters = list(set(matches))[:5]  # 最多返回5个
        return characters
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词（简化实现）"""
        # 移除标点符号
        text_clean = re.sub(r'[^\w\s]', ' ', text)
        
        # 分词（简化：按空格分割）
        words = text_clean.split()
        
        # 过滤短词和常见词
        stop_words = {'的', '了', '在', '是', '我', '你', '他', '她', 'the', 'a', 'an', 'is', 'are'}
        keywords = [w for w in words if len(w) > 1 and w.lower() not in stop_words]
        
        # 返回前10个关键词
        return keywords[:10]


class SoundEffectLibrary:
    """音效库"""
    
    def __init__(self):
        """初始化音效库"""
        self.effects: Dict[str, SoundEffect] = {}
        self._initialize_default_effects()
    
    def _initialize_default_effects(self):
        """初始化默认音效库"""
        # 创建一些示例音效
        default_effects = [
            # 动作音效
            SoundEffect("sfx_001", "拳击声", "拳头击打的声音", "action", ["打斗", "拳击", "击打"], 1.5, "sfx/punch.mp3"),
            SoundEffect("sfx_002", "脚步声", "快速奔跑的脚步声", "action", ["跑步", "脚步", "奔跑"], 2.0, "sfx/footsteps.mp3"),
            SoundEffect("sfx_003", "门开声", "木门打开的声音", "action", ["开门", "门", "进入"], 1.0, "sfx/door_open.mp3"),
            SoundEffect("sfx_004", "玻璃碎裂", "玻璃破碎的声音", "action", ["破碎", "玻璃", "打碎"], 2.0, "sfx/glass_break.mp3"),
            
            # 环境音效
            SoundEffect("sfx_101", "城市街道", "繁忙的城市街道环境音", "environment", ["城市", "街道", "车流"], 10.0, "sfx/city_street.mp3"),
            SoundEffect("sfx_102", "森林鸟鸣", "森林中的鸟叫声", "environment", ["森林", "鸟", "自然"], 8.0, "sfx/forest_birds.mp3"),
            SoundEffect("sfx_103", "海浪声", "海边的波浪声", "environment", ["海边", "海浪", "海洋"], 12.0, "sfx/ocean_waves.mp3"),
            SoundEffect("sfx_104", "雨声", "下雨的声音", "environment", ["雨", "下雨", "雨天"], 10.0, "sfx/rain.mp3"),
            
            # 情感音效
            SoundEffect("sfx_201", "欢快音乐", "轻快愉悦的背景音乐", "emotional", ["快乐", "开心", "欢乐"], 15.0, "sfx/happy_music.mp3"),
            SoundEffect("sfx_202", "悲伤音乐", "忧伤的背景音乐", "emotional", ["悲伤", "伤心", "忧伤"], 15.0, "sfx/sad_music.mp3"),
            SoundEffect("sfx_203", "紧张音乐", "紧张刺激的背景音乐", "emotional", ["紧张", "刺激", "惊险"], 12.0, "sfx/tense_music.mp3"),
            SoundEffect("sfx_204", "惊吓音效", "突然的惊吓声音", "emotional", ["惊吓", "恐怖", "害怕"], 1.0, "sfx/scare.mp3"),
            
            # 对话音效
            SoundEffect("sfx_301", "电话铃声", "手机铃声", "dialogue", ["电话", "铃声", "来电"], 3.0, "sfx/phone_ring.mp3"),
            SoundEffect("sfx_302", "敲门声", "敲门的声音", "dialogue", ["敲门", "门", "访客"], 2.0, "sfx/knock.mp3"),
            SoundEffect("sfx_303", "笑声", "人群笑声", "dialogue", ["笑", "笑声", "欢笑"], 3.0, "sfx/laughter.mp3"),
            SoundEffect("sfx_304", "掌声", "热烈的掌声", "dialogue", ["掌声", "鼓掌", "喝彩"], 4.0, "sfx/applause.mp3"),
        ]
        
        for effect in default_effects:
            # 生成简单的向量表示（基于标签）
            effect.embedding = self._generate_embedding(effect)
            self.effects[effect.effect_id] = effect
    
    def _generate_embedding(self, effect: SoundEffect) -> List[float]:
        """生成音效的向量表示（简化实现）"""
        # 使用标签和描述生成简单的向量
        text = f"{effect.name} {effect.description} {' '.join(effect.tags)}"
        
        # 简化：使用字符频率作为向量（实际应使用词嵌入模型）
        vector = [0.0] * 128
        for i, char in enumerate(text[:128]):
            vector[i] = ord(char) / 1000.0
        
        # 归一化
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = [v / norm for v in vector]
        
        return vector
    
    def add_effect(self, effect: SoundEffect):
        """添加音效到库"""
        if effect.embedding is None:
            effect.embedding = self._generate_embedding(effect)
        self.effects[effect.effect_id] = effect
    
    def get_effect(self, effect_id: str) -> Optional[SoundEffect]:
        """获取音效"""
        return self.effects.get(effect_id)
    
    def search_by_category(self, category: str) -> List[SoundEffect]:
        """按类别搜索音效"""
        return [e for e in self.effects.values() if e.category == category]
    
    def search_by_tags(self, tags: List[str]) -> List[SoundEffect]:
        """按标签搜索音效"""
        results = []
        for effect in self.effects.values():
            if any(tag in effect.tags for tag in tags):
                results.append(effect)
        return results
    
    def get_all_effects(self) -> List[SoundEffect]:
        """获取所有音效"""
        return list(self.effects.values())


class SoundEffectMatcher:
    """
    智能音效匹配器
    
    核心功能：
    1. 剧本解析
    2. 音效推荐
    3. 自动放置
    """
    
    _instance = None
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """初始化音效匹配器"""
        if self._initialized:
            return
        
        self.parser = ScriptParser()
        self.library = SoundEffectLibrary()
        self._initialized = True
    
    def parse_script(self, script: str) -> List[SceneSegment]:
        """
        解析剧本，提取场景片段
        
        参数:
            script: 剧本文本
        
        返回:
            场景片段列表
        """
        return self.parser.parse_script(script)
    
    def recommend_sound_effects(
        self,
        scene_segment: SceneSegment,
        top_k: int = 3
    ) -> List[Tuple[SoundEffect, float]]:
        """
        推荐匹配的音效
        
        参数:
            scene_segment: 场景片段
            top_k: 返回前k个推荐
        
        返回:
            (音效, 相似度分数)的列表
        """
        # 获取所有音效
        all_effects = self.library.get_all_effects()
        
        # 计算相似度
        scores = []
        for effect in all_effects:
            score = self._calculate_similarity(scene_segment, effect)
            scores.append((effect, score))
        
        # 按分数排序
        scores.sort(key=lambda x: x[1], reverse=True)
        
        # 返回前k个
        return scores[:top_k]
    
    def _calculate_similarity(
        self,
        scene: SceneSegment,
        effect: SoundEffect
    ) -> float:
        """
        计算场景和音效的相似度
        
        参数:
            scene: 场景片段
            effect: 音效
        
        返回:
            相似度分数（0-1）
        """
        score = 0.0
        
        # 1. 场景类型匹配（权重0.3）
        type_match = {
            SceneType.ACTION: ["action"],
            SceneType.DIALOGUE: ["dialogue"],
            SceneType.ENVIRONMENT: ["environment"],
            SceneType.EMOTIONAL: ["emotional"],
            SceneType.TRANSITION: ["action", "environment"]
        }
        
        if effect.category in type_match.get(scene.scene_type, []):
            score += 0.3
        
        # 2. 关键词匹配（权重0.4）
        scene_keywords = set(scene.keywords + scene.actions)
        effect_keywords = set(effect.tags)
        
        if scene_keywords and effect_keywords:
            intersection = scene_keywords & effect_keywords
            union = scene_keywords | effect_keywords
            keyword_score = len(intersection) / len(union) if union else 0
            score += 0.4 * keyword_score
        
        # 3. 情感匹配（权重0.3）
        emotion_keywords = {
            EmotionType.HAPPY: ["快乐", "欢乐", "happy"],
            EmotionType.SAD: ["悲伤", "忧伤", "sad"],
            EmotionType.ANGRY: ["愤怒", "angry"],
            EmotionType.FEAR: ["恐怖", "害怕", "scare"],
            EmotionType.SURPRISE: ["惊", "surprise"]
        }
        
        for emotion in scene.emotions:
            if emotion != EmotionType.NEUTRAL:
                emotion_tags = emotion_keywords.get(emotion, [])
                if any(tag in effect.tags or tag in effect.description for tag in emotion_tags):
                    score += 0.3
                    break
        
        return min(score, 1.0)
    
    def auto_place_sound_effects(
        self,
        segments: List[SceneSegment],
        effect_placements: List[Tuple[str, str]]  # (scene_id, effect_id)
    ) -> List[Dict]:
        """
        自动将音效放置在时间轴上
        
        参数:
            segments: 场景片段列表
            effect_placements: (场景ID, 音效ID)的配对列表
        
        返回:
            时间轴放置信息列表
        """
        placements = []
        
        # 创建场景ID到场景的映射
        scene_map = {seg.scene_id: seg for seg in segments}
        
        for scene_id, effect_id in effect_placements:
            scene = scene_map.get(scene_id)
            effect = self.library.get_effect(effect_id)
            
            if scene and effect:
                placement = {
                    "scene_id": scene_id,
                    "effect_id": effect_id,
                    "effect_name": effect.name,
                    "start_time": scene.start_time,
                    "duration": min(effect.duration, scene.duration),
                    "file_url": effect.file_url,
                    "volume": 0.7  # 默认音量
                }
                placements.append(placement)
        
        return placements
    
    def upload_custom_effect(
        self,
        name: str,
        description: str,
        category: str,
        tags: List[str],
        duration: float,
        file_url: str
    ) -> SoundEffect:
        """
        上传自定义音效
        
        参数:
            name: 音效名称
            description: 描述
            category: 类别
            tags: 标签列表
            duration: 时长
            file_url: 文件URL
        
        返回:
            创建的音效对象
        """
        # 生成ID
        effect_id = f"custom_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # 创建音效
        effect = SoundEffect(
            effect_id=effect_id,
            name=name,
            description=description,
            category=category,
            tags=tags,
            duration=duration,
            file_url=file_url
        )
        
        # 添加到库
        self.library.add_effect(effect)
        
        return effect
