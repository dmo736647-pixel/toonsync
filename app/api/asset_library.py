"""资源库管理API端点"""
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
import json

from app.core.database import get_db
from app.core.storage import get_storage, StorageManager
from app.services.asset_library import AssetLibraryService
from app.models.asset import AssetType
from app.models.user import User
from app.api.dependencies import get_current_user
from app.schemas.asset_library import (
    SoundEffectCreate,
    SoundEffectUpdate,
    SoundEffectResponse,
    SoundEffectListResponse,
    CategoryListResponse,
    TagListResponse,
    BulkSoundEffectCreate,
    SearchRequest,
    SearchResponse,
    SimilaritySearchRequest,
    AssetTypeEnum,
    AssetUpdate,
    AssetResponse,
    AssetListResponse,
    AssetSearchRequest,
    AssetSearchResponse,
)

router = APIRouter(prefix="/api/v1/asset-library", tags=["asset-library"])


# ==================== 音效库管理端点 ====================

@router.post("/sound-effects", response_model=SoundEffectResponse, status_code=201)
async def create_sound_effect(
    sound_effect: SoundEffectCreate,
    db: Session = Depends(get_db)
):
    """
    创建音效
    
    参数:
        sound_effect: 音效创建数据
    
    返回:
        SoundEffectResponse: 创建的音效
    """
    service = AssetLibraryService(db)
    
    created = service.create_sound_effect(
        name=sound_effect.name,
        category=sound_effect.category,
        audio_file_url=sound_effect.audio_file_url,
        duration_seconds=sound_effect.duration_seconds,
        tags=sound_effect.tags
    )
    
    return SoundEffectResponse.from_orm_with_tags(created)


@router.get("/sound-effects/{sound_effect_id}", response_model=SoundEffectResponse)
async def get_sound_effect(
    sound_effect_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取音效
    
    参数:
        sound_effect_id: 音效ID
    
    返回:
        SoundEffectResponse: 音效详情
    """
    service = AssetLibraryService(db)
    sound_effect = service.get_sound_effect(sound_effect_id)
    
    if not sound_effect:
        raise HTTPException(status_code=404, detail="音效不存在")
    
    # 检查访问权限
    if not service.check_sound_effect_access_permission(current_user, sound_effect):
        raise HTTPException(
            status_code=403,
            detail="您的订阅层级无法访问此高级音效。请升级到专业版或企业版。"
        )
    
    return SoundEffectResponse.from_orm_with_tags(sound_effect)


@router.get("/sound-effects", response_model=SoundEffectListResponse)
async def list_sound_effects(
    category: Optional[str] = Query(None, description="分类过滤"),
    tags: Optional[List[str]] = Query(None, description="标签过滤"),
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(100, ge=1, le=1000, description="返回数量限制"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    列出音效
    
    参数:
        category: 分类过滤（可选）
        tags: 标签过滤（可选）
        skip: 跳过数量
        limit: 返回数量限制
    
    返回:
        SoundEffectListResponse: 音效列表
    """
    service = AssetLibraryService(db)
    
    sound_effects = service.list_sound_effects(
        category=category,
        tags=tags,
        skip=skip,
        limit=limit
    )
    
    # 过滤用户可访问的音效
    accessible_sound_effects = service.filter_accessible_sound_effects(
        current_user,
        sound_effects
    )
    
    total = service.count_sound_effects(category=category, tags=tags)
    
    items = [SoundEffectResponse.from_orm_with_tags(se) for se in accessible_sound_effects]
    
    return SoundEffectListResponse(
        items=items,
        total=total,
        skip=skip,
        limit=limit
    )


@router.put("/sound-effects/{sound_effect_id}", response_model=SoundEffectResponse)
async def update_sound_effect(
    sound_effect_id: UUID,
    sound_effect: SoundEffectUpdate,
    db: Session = Depends(get_db)
):
    """
    更新音效
    
    参数:
        sound_effect_id: 音效ID
        sound_effect: 音效更新数据
    
    返回:
        SoundEffectResponse: 更新后的音效
    """
    service = AssetLibraryService(db)
    
    updated = service.update_sound_effect(
        sound_effect_id=sound_effect_id,
        name=sound_effect.name,
        category=sound_effect.category,
        tags=sound_effect.tags
    )
    
    if not updated:
        raise HTTPException(status_code=404, detail="音效不存在")
    
    return SoundEffectResponse.from_orm_with_tags(updated)


@router.delete("/sound-effects/{sound_effect_id}", status_code=204)
async def delete_sound_effect(
    sound_effect_id: UUID,
    db: Session = Depends(get_db)
):
    """
    删除音效
    
    参数:
        sound_effect_id: 音效ID
    """
    service = AssetLibraryService(db)
    
    success = service.delete_sound_effect(sound_effect_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="音效不存在")


@router.get("/sound-effects/categories", response_model=CategoryListResponse)
async def get_categories(db: Session = Depends(get_db)):
    """
    获取所有音效分类
    
    返回:
        CategoryListResponse: 分类列表
    """
    service = AssetLibraryService(db)
    categories = service.get_categories()
    
    return CategoryListResponse(categories=categories)


@router.get("/sound-effects/tags", response_model=TagListResponse)
async def get_tags(db: Session = Depends(get_db)):
    """
    获取所有音效标签
    
    返回:
        TagListResponse: 标签列表
    """
    service = AssetLibraryService(db)
    tags = service.get_tags()
    
    return TagListResponse(tags=tags)


@router.post("/sound-effects/bulk", response_model=List[SoundEffectResponse], status_code=201)
async def bulk_create_sound_effects(
    bulk_data: BulkSoundEffectCreate,
    db: Session = Depends(get_db)
):
    """
    批量创建音效
    
    参数:
        bulk_data: 批量音效创建数据
    
    返回:
        List[SoundEffectResponse]: 创建的音效列表
    """
    service = AssetLibraryService(db)
    
    # 转换为字典列表
    sound_effects_data = [
        {
            "name": se.name,
            "category": se.category,
            "audio_file_url": se.audio_file_url,
            "duration_seconds": se.duration_seconds,
            "tags": se.tags or []
        }
        for se in bulk_data.sound_effects
    ]
    
    created = service.bulk_create_sound_effects(sound_effects_data)
    
    return [SoundEffectResponse.from_orm_with_tags(se) for se in created]



# ==================== 搜索端点 ====================

@router.post("/sound-effects/search", response_model=SearchResponse)
async def search_sound_effects(
    search_request: SearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    搜索音效（全文搜索）
    
    参数:
        search_request: 搜索请求
    
    返回:
        SearchResponse: 搜索结果
    """
    service = AssetLibraryService(db)
    
    results, elapsed_time = service.search_sound_effects(
        query=search_request.query,
        category=search_request.category,
        tags=search_request.tags,
        skip=search_request.skip,
        limit=search_request.limit
    )
    
    # 过滤用户可访问的音效
    accessible_results = service.filter_accessible_sound_effects(
        current_user,
        results
    )
    
    total = service.count_search_results(
        query=search_request.query,
        category=search_request.category,
        tags=search_request.tags
    )
    
    items = [SoundEffectResponse.from_orm_with_tags(se) for se in accessible_results]
    
    return SearchResponse(
        items=items,
        total=total,
        skip=search_request.skip,
        limit=search_request.limit,
        elapsed_time=elapsed_time
    )


@router.post("/sound-effects/search/similarity", response_model=List[SoundEffectResponse])
async def search_by_similarity(
    similarity_request: SimilaritySearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    基于标签相似度搜索音效
    
    参数:
        similarity_request: 相似度搜索请求
    
    返回:
        List[SoundEffectResponse]: 相似音效列表
    """
    service = AssetLibraryService(db)
    
    results = service.search_sound_effects_by_similarity(
        reference_tags=similarity_request.reference_tags,
        category=similarity_request.category,
        top_k=similarity_request.top_k
    )
    
    # 过滤用户可访问的音效
    accessible_results = service.filter_accessible_sound_effects(
        current_user,
        results
    )
    
    return [SoundEffectResponse.from_orm_with_tags(se) for se in accessible_results]



# ==================== 素材管理端点 ====================

@router.post("/assets", response_model=AssetResponse, status_code=201)
async def upload_asset(
    file: UploadFile = File(...),
    asset_type: str = Form(...),
    category: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    metadata: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    storage: StorageManager = Depends(get_storage)
):
    """
    上传素材
    
    参数:
        file: 上传的文件
        asset_type: 素材类型（image/audio/video）
        category: 分类（可选）
        tags: 标签列表（JSON字符串，可选）
        description: 描述（可选）
        metadata: 元数据（JSON字符串，可选）
    
    返回:
        AssetResponse: 创建的素材
    """
    service = AssetLibraryService(db, storage)
    
    # 解析标签
    tags_list = None
    if tags:
        try:
            tags_list = json.loads(tags)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="标签格式错误")
    
    # 解析元数据
    metadata_dict = None
    if metadata:
        try:
            metadata_dict = json.loads(metadata)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="元数据格式错误")
    
    # 验证素材类型
    try:
        asset_type_enum = AssetType(asset_type)
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的素材类型")
    
    # 上传素材
    created = service.upload_asset(
        file=file.file,
        filename=file.filename,
        asset_type=asset_type_enum,
        category=category,
        tags=tags_list,
        description=description,
        metadata=metadata_dict
    )
    
    return AssetResponse.from_orm_with_tags(created)


@router.get("/assets/{asset_id}", response_model=AssetResponse)
async def get_asset(
    asset_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取素材
    
    参数:
        asset_id: 素材ID
    
    返回:
        AssetResponse: 素材详情
    """
    service = AssetLibraryService(db)
    asset = service.get_asset(asset_id)
    
    if not asset:
        raise HTTPException(status_code=404, detail="素材不存在")
    
    # 检查访问权限
    if not service.check_asset_access_permission(current_user, asset):
        raise HTTPException(
            status_code=403,
            detail="您的订阅层级无法访问此高级素材。请升级到专业版或企业版。"
        )
    
    return AssetResponse.from_orm_with_tags(asset)


@router.get("/assets", response_model=AssetListResponse)
async def list_assets(
    asset_type: Optional[AssetTypeEnum] = Query(None, description="素材类型过滤"),
    category: Optional[str] = Query(None, description="分类过滤"),
    tags: Optional[List[str]] = Query(None, description="标签过滤"),
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(100, ge=1, le=1000, description="返回数量限制"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    列出素材
    
    参数:
        asset_type: 素材类型过滤（可选）
        category: 分类过滤（可选）
        tags: 标签过滤（可选）
        skip: 跳过数量
        limit: 返回数量限制
    
    返回:
        AssetListResponse: 素材列表
    """
    service = AssetLibraryService(db)
    
    # 转换枚举类型
    asset_type_model = AssetType(asset_type.value) if asset_type else None
    
    assets = service.list_assets(
        asset_type=asset_type_model,
        category=category,
        tags=tags,
        skip=skip,
        limit=limit
    )
    
    # 过滤用户可访问的素材
    accessible_assets = service.filter_accessible_assets(
        current_user,
        assets
    )
    
    total = service.count_assets(
        asset_type=asset_type_model,
        category=category,
        tags=tags
    )
    
    items = [AssetResponse.from_orm_with_tags(asset) for asset in accessible_assets]
    
    return AssetListResponse(
        items=items,
        total=total,
        skip=skip,
        limit=limit
    )


@router.put("/assets/{asset_id}", response_model=AssetResponse)
async def update_asset(
    asset_id: UUID,
    asset: AssetUpdate,
    db: Session = Depends(get_db)
):
    """
    更新素材
    
    参数:
        asset_id: 素材ID
        asset: 素材更新数据
    
    返回:
        AssetResponse: 更新后的素材
    """
    service = AssetLibraryService(db)
    
    updated = service.update_asset(
        asset_id=asset_id,
        name=asset.name,
        category=asset.category,
        tags=asset.tags,
        description=asset.description
    )
    
    if not updated:
        raise HTTPException(status_code=404, detail="素材不存在")
    
    return AssetResponse.from_orm_with_tags(updated)


@router.delete("/assets/{asset_id}", status_code=204)
async def delete_asset(
    asset_id: UUID,
    db: Session = Depends(get_db)
):
    """
    删除素材
    
    参数:
        asset_id: 素材ID
    """
    service = AssetLibraryService(db)
    
    success = service.delete_asset(asset_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="素材不存在")


@router.post("/assets/{asset_id}/preview", response_model=dict)
async def generate_asset_preview(
    asset_id: UUID,
    db: Session = Depends(get_db)
):
    """
    生成素材预览
    
    参数:
        asset_id: 素材ID
    
    返回:
        dict: 包含预览URL的字典
    """
    service = AssetLibraryService(db)
    
    preview_url = service.generate_preview(asset_id)
    
    if not preview_url:
        raise HTTPException(status_code=404, detail="素材不存在或预览生成失败")
    
    return {"preview_url": preview_url}


@router.post("/assets/search", response_model=AssetSearchResponse)
async def search_assets(
    search_request: AssetSearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    搜索素材（全文搜索）
    
    参数:
        search_request: 搜索请求
    
    返回:
        AssetSearchResponse: 搜索结果
    """
    service = AssetLibraryService(db)
    
    # 转换枚举类型
    asset_type_model = AssetType(search_request.asset_type.value) if search_request.asset_type else None
    
    results, elapsed_time = service.search_assets(
        query=search_request.query,
        asset_type=asset_type_model,
        category=search_request.category,
        tags=search_request.tags,
        skip=search_request.skip,
        limit=search_request.limit
    )
    
    # 过滤用户可访问的素材
    accessible_results = service.filter_accessible_assets(
        current_user,
        results
    )
    
    total = service.count_assets(
        asset_type=asset_type_model,
        category=search_request.category,
        tags=search_request.tags
    )
    
    items = [AssetResponse.from_orm_with_tags(asset) for asset in accessible_results]
    
    return AssetSearchResponse(
        items=items,
        total=total,
        skip=search_request.skip,
        limit=search_request.limit,
        elapsed_time=elapsed_time
    )
