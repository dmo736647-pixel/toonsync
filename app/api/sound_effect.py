"""
音效匹配API端点
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.sound_effect import (
    ScriptParseRequest,
    ScriptParseResponse,
    SceneSegmentResponse,
    RecommendRequest,
    RecommendResponse,
    RecommendationResponse,
    SoundEffectResponse,
    AutoPlaceRequest,
    AutoPlaceResponse,
    PlacementResponse,
    UploadEffectRequest,
    SearchEffectsRequest,
    SearchEffectsResponse
)
from app.services.sound_effect_matcher import (
    SoundEffectMatcher,
    SceneSegment,
    SceneType,
    EmotionType
)


router = APIRouter(prefix="/sound-effects", tags=["sound-effects"])


@router.post("/parse-script", response_model=ScriptParseResponse)
async def parse_script(
    request: ScriptParseRequest,
    current_user: User = Depends(get_current_user)
):
    """
    解析剧本，提取场景片段
    
    使用NLP技术提取场景类型、动作、情感等信息
    """
    try:
        matcher = SoundEffectMatcher()
        
        # 解析剧本
        segments = matcher.parse_script(request.script)
        
        # 转换为响应格式
        segment_responses = [
            SceneSegmentResponse(
                scene_id=seg.scene_id,
                text=seg.text,
                scene_type=seg.scene_type.value,
                actions=seg.actions,
                emotions=[e.value for e in seg.emotions],
                characters=seg.characters,
                start_time=seg.start_time,
                duration=seg.duration,
                keywords=seg.keywords
            )
            for seg in segments
        ]
        
        # 计算总时长
        total_duration = sum(seg.duration for seg in segments)
        
        return ScriptParseResponse(
            segments=segment_responses,
            total_duration=total_duration,
            segment_count=len(segments)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"剧本解析失败: {str(e)}")


@router.post("/recommend", response_model=RecommendResponse)
async def recommend_sound_effects(
    request: RecommendRequest,
    current_user: User = Depends(get_current_user)
):
    """
    推荐匹配的音效
    
    基于场景内容推荐最相关的音效（默认返回前3个）
    """
    try:
        matcher = SoundEffectMatcher()
        
        # 创建场景片段
        scene = SceneSegment(
            scene_id=request.scene_id,
            text=request.scene_text,
            scene_type=SceneType(request.scene_type),
            actions=[],
            emotions=[EmotionType.NEUTRAL],
            characters=[],
            start_time=0.0,
            duration=5.0,
            keywords=request.scene_text.split()[:10]
        )
        
        # 获取推荐
        recommendations = matcher.recommend_sound_effects(scene, top_k=request.top_k)
        
        # 转换为响应格式
        recommendation_responses = [
            RecommendationResponse(
                effect=SoundEffectResponse(
                    effect_id=effect.effect_id,
                    name=effect.name,
                    description=effect.description,
                    category=effect.category,
                    tags=effect.tags,
                    duration=effect.duration,
                    file_url=effect.file_url
                ),
                score=score
            )
            for effect, score in recommendations
        ]
        
        return RecommendResponse(
            scene_id=request.scene_id,
            recommendations=recommendation_responses
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"推荐失败: {str(e)}")


@router.post("/auto-place", response_model=AutoPlaceResponse)
async def auto_place_sound_effects(
    request: AutoPlaceRequest,
    current_user: User = Depends(get_current_user)
):
    """
    自动将音效放置在时间轴上
    
    根据场景和音效的配对，自动计算放置位置和时长
    """
    try:
        matcher = SoundEffectMatcher()
        
        # 解析剧本
        segments = matcher.parse_script(request.script)
        
        # 准备放置列表
        placements = [
            (p.scene_id, p.effect_id)
            for p in request.placements
        ]
        
        # 自动放置
        placement_results = matcher.auto_place_sound_effects(segments, placements)
        
        # 转换为响应格式
        placement_responses = [
            PlacementResponse(**p)
            for p in placement_results
        ]
        
        return AutoPlaceResponse(
            placements=placement_responses,
            total_effects=len(placement_responses)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"自动放置失败: {str(e)}")


@router.post("/upload", response_model=SoundEffectResponse)
async def upload_custom_effect(
    request: UploadEffectRequest,
    current_user: User = Depends(get_current_user)
):
    """
    上传自定义音效
    
    支持用户上传自己的音效文件并自动标记元数据
    """
    try:
        matcher = SoundEffectMatcher()
        
        # 上传音效
        effect = matcher.upload_custom_effect(
            name=request.name,
            description=request.description,
            category=request.category,
            tags=request.tags,
            duration=request.duration,
            file_url=request.file_url
        )
        
        return SoundEffectResponse(
            effect_id=effect.effect_id,
            name=effect.name,
            description=effect.description,
            category=effect.category,
            tags=effect.tags,
            duration=effect.duration,
            file_url=effect.file_url
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")


@router.post("/search", response_model=SearchEffectsResponse)
async def search_sound_effects(
    request: SearchEffectsRequest,
    current_user: User = Depends(get_current_user)
):
    """
    搜索音效库
    
    支持按类别和标签搜索音效
    """
    try:
        matcher = SoundEffectMatcher()
        
        # 搜索音效
        if request.category:
            effects = matcher.library.search_by_category(request.category)
        elif request.tags:
            effects = matcher.library.search_by_tags(request.tags)
        else:
            effects = matcher.library.get_all_effects()
        
        # 转换为响应格式
        effect_responses = [
            SoundEffectResponse(
                effect_id=e.effect_id,
                name=e.name,
                description=e.description,
                category=e.category,
                tags=e.tags,
                duration=e.duration,
                file_url=e.file_url
            )
            for e in effects
        ]
        
        return SearchEffectsResponse(
            effects=effect_responses,
            total_count=len(effect_responses)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@router.get("/library", response_model=SearchEffectsResponse)
async def get_sound_library(
    current_user: User = Depends(get_current_user)
):
    """
    获取完整音效库
    
    返回所有可用的音效
    """
    try:
        matcher = SoundEffectMatcher()
        effects = matcher.library.get_all_effects()
        
        effect_responses = [
            SoundEffectResponse(
                effect_id=e.effect_id,
                name=e.name,
                description=e.description,
                category=e.category,
                tags=e.tags,
                duration=e.duration,
                file_url=e.file_url
            )
            for e in effects
        ]
        
        return SearchEffectsResponse(
            effects=effect_responses,
            total_count=len(effect_responses)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取音效库失败: {str(e)}")
