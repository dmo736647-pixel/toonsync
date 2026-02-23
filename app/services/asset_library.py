"""资源库管理服务"""
from typing import List, Optional, Dict, Any, BinaryIO
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, and_
import uuid
import time
import mimetypes
from pathlib import Path

from app.models.sound_effect import SoundEffect
from app.models.asset import Asset, AssetType
from app.models.user import User, SubscriptionTier
from app.core.storage import StorageManager, get_storage


class AssetLibraryService:
    """资源库管理服务"""
    
    def __init__(self, db: Session, storage: Optional[StorageManager] = None):
        self.db = db
        self.storage = storage or get_storage()
    
    # ==================== 权限控制 ====================
    
    def check_asset_access_permission(
        self,
        user: User,
        asset: Asset
    ) -> bool:
        """
        检查用户是否有权限访问素材
        
        参数:
            user: 用户对象
            asset: 素材对象
        
        返回:
            bool: 是否有权限访问
        
        权限规则:
            - 基础版（免费）：只能访问基础素材库
            - 按量付费：只能访问基础素材库
            - 专业版：可以访问基础和高级素材库
            - 企业版：可以访问所有素材库
        """
        # 如果素材没有标记为高级素材，所有用户都可以访问
        if not asset.category or "premium" not in asset.category.lower():
            return True
        
        # 高级素材只有专业版和企业版可以访问
        if user.subscription_tier in [SubscriptionTier.PROFESSIONAL, SubscriptionTier.ENTERPRISE]:
            return True
        
        return False
    
    def check_sound_effect_access_permission(
        self,
        user: User,
        sound_effect: SoundEffect
    ) -> bool:
        """
        检查用户是否有权限访问音效
        
        参数:
            user: 用户对象
            sound_effect: 音效对象
        
        返回:
            bool: 是否有权限访问
        
        权限规则:
            - 基础版（免费）：只能访问基础音效库
            - 按量付费：只能访问基础音效库
            - 专业版：可以访问基础和高级音效库
            - 企业版：可以访问所有音效库
        """
        # 如果音效没有标记为高级音效，所有用户都可以访问
        if not sound_effect.category or "premium" not in sound_effect.category.lower():
            return True
        
        # 高级音效只有专业版和企业版可以访问
        if user.subscription_tier in [SubscriptionTier.PROFESSIONAL, SubscriptionTier.ENTERPRISE]:
            return True
        
        return False
    
    def filter_accessible_assets(
        self,
        user: User,
        assets: List[Asset]
    ) -> List[Asset]:
        """
        过滤用户可访问的素材列表
        
        参数:
            user: 用户对象
            assets: 素材列表
        
        返回:
            List[Asset]: 用户可访问的素材列表
        """
        return [
            asset for asset in assets
            if self.check_asset_access_permission(user, asset)
        ]
    
    def filter_accessible_sound_effects(
        self,
        user: User,
        sound_effects: List[SoundEffect]
    ) -> List[SoundEffect]:
        """
        过滤用户可访问的音效列表
        
        参数:
            user: 用户对象
            sound_effects: 音效列表
        
        返回:
            List[SoundEffect]: 用户可访问的音效列表
        """
        return [
            se for se in sound_effects
            if self.check_sound_effect_access_permission(user, se)
        ]
    
    # ==================== 音效库管理 ====================
    
    def create_sound_effect(
        self,
        name: str,
        category: str,
        audio_file_url: str,
        duration_seconds: float,
        tags: Optional[List[str]] = None
    ) -> SoundEffect:
        """
        创建音效
        
        参数:
            name: 音效名称
            category: 音效分类
            audio_file_url: 音频文件URL
            duration_seconds: 音频时长（秒）
            tags: 标签列表
        
        返回:
            SoundEffect: 创建的音效对象
        """
        # 将标签列表转换为逗号分隔的字符串
        tags_str = ",".join(tags) if tags else None
        
        sound_effect = SoundEffect(
            name=name,
            category=category,
            audio_file_url=audio_file_url,
            duration_seconds=duration_seconds,
            tags=tags_str
        )
        
        self.db.add(sound_effect)
        self.db.commit()
        self.db.refresh(sound_effect)
        
        return sound_effect
    
    def get_sound_effect(self, sound_effect_id: uuid.UUID) -> Optional[SoundEffect]:
        """
        获取音效
        
        参数:
            sound_effect_id: 音效ID
        
        返回:
            Optional[SoundEffect]: 音效对象，如果不存在则返回None
        """
        return self.db.query(SoundEffect).filter(
            SoundEffect.id == sound_effect_id
        ).first()
    
    def list_sound_effects(
        self,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[SoundEffect]:
        """
        列出音效
        
        参数:
            category: 分类过滤（可选）
            tags: 标签过滤（可选）
            skip: 跳过数量
            limit: 返回数量限制
        
        返回:
            List[SoundEffect]: 音效列表
        """
        query = self.db.query(SoundEffect)
        
        # 分类过滤
        if category:
            query = query.filter(SoundEffect.category == category)
        
        # 标签过滤
        if tags:
            # 使用LIKE查询匹配标签
            tag_filters = []
            for tag in tags:
                tag_filters.append(SoundEffect.tags.like(f"%{tag}%"))
            query = query.filter(or_(*tag_filters))
        
        return query.offset(skip).limit(limit).all()
    
    def update_sound_effect(
        self,
        sound_effect_id: uuid.UUID,
        name: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Optional[SoundEffect]:
        """
        更新音效
        
        参数:
            sound_effect_id: 音效ID
            name: 新名称（可选）
            category: 新分类（可选）
            tags: 新标签列表（可选）
        
        返回:
            Optional[SoundEffect]: 更新后的音效对象
        """
        sound_effect = self.get_sound_effect(sound_effect_id)
        if not sound_effect:
            return None
        
        if name is not None:
            sound_effect.name = name
        if category is not None:
            sound_effect.category = category
        if tags is not None:
            sound_effect.tags = ",".join(tags) if tags else None
        
        self.db.commit()
        self.db.refresh(sound_effect)
        
        return sound_effect
    
    def delete_sound_effect(self, sound_effect_id: uuid.UUID) -> bool:
        """
        删除音效
        
        参数:
            sound_effect_id: 音效ID
        
        返回:
            bool: 是否删除成功
        """
        sound_effect = self.get_sound_effect(sound_effect_id)
        if not sound_effect:
            return False
        
        self.db.delete(sound_effect)
        self.db.commit()
        
        return True
    
    def get_categories(self) -> List[str]:
        """
        获取所有音效分类
        
        返回:
            List[str]: 分类列表
        """
        categories = self.db.query(SoundEffect.category).distinct().all()
        return [cat[0] for cat in categories]
    
    def get_tags(self) -> List[str]:
        """
        获取所有音效标签
        
        返回:
            List[str]: 标签列表
        """
        # 获取所有标签字符串
        tags_results = self.db.query(SoundEffect.tags).filter(
            SoundEffect.tags.isnot(None)
        ).all()
        
        # 解析标签
        all_tags = set()
        for tags_str in tags_results:
            if tags_str[0]:
                tags = tags_str[0].split(",")
                all_tags.update(tag.strip() for tag in tags if tag.strip())
        
        return sorted(list(all_tags))
    
    def count_sound_effects(
        self,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> int:
        """
        统计音效数量
        
        参数:
            category: 分类过滤（可选）
            tags: 标签过滤（可选）
        
        返回:
            int: 音效数量
        """
        query = self.db.query(func.count(SoundEffect.id))
        
        if category:
            query = query.filter(SoundEffect.category == category)
        
        if tags:
            tag_filters = []
            for tag in tags:
                tag_filters.append(SoundEffect.tags.like(f"%{tag}%"))
            query = query.filter(or_(*tag_filters))
        
        return query.scalar()
    
    def bulk_create_sound_effects(
        self,
        sound_effects_data: List[Dict[str, Any]]
    ) -> List[SoundEffect]:
        """
        批量创建音效
        
        参数:
            sound_effects_data: 音效数据列表，每个元素包含name、category、audio_file_url、duration_seconds、tags
        
        返回:
            List[SoundEffect]: 创建的音效列表
        """
        sound_effects = []
        
        for data in sound_effects_data:
            tags = data.get("tags", [])
            tags_str = ",".join(tags) if tags else None
            
            sound_effect = SoundEffect(
                name=data["name"],
                category=data["category"],
                audio_file_url=data["audio_file_url"],
                duration_seconds=data["duration_seconds"],
                tags=tags_str
            )
            sound_effects.append(sound_effect)
        
        self.db.bulk_save_objects(sound_effects, return_defaults=True)
        self.db.commit()
        
        return sound_effects

    
    # ==================== 素材搜索功能 ====================
    
    def search_sound_effects(
        self,
        query: str,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[SoundEffect], float]:
        """
        搜索音效（全文搜索）
        
        参数:
            query: 搜索关键词
            category: 分类过滤（可选）
            tags: 标签过滤（可选）
            skip: 跳过数量
            limit: 返回数量限制
        
        返回:
            tuple[List[SoundEffect], float]: (音效列表, 搜索耗时秒数)
        """
        start_time = time.time()
        
        # 构建搜索查询
        search_query = self.db.query(SoundEffect)
        
        # 全文搜索：在名称、分类和标签中搜索
        if query:
            search_pattern = f"%{query}%"
            search_query = search_query.filter(
                or_(
                    SoundEffect.name.like(search_pattern),
                    SoundEffect.category.like(search_pattern),
                    SoundEffect.tags.like(search_pattern)
                )
            )
        
        # 分类过滤
        if category:
            search_query = search_query.filter(SoundEffect.category == category)
        
        # 标签过滤
        if tags:
            tag_filters = []
            for tag in tags:
                tag_filters.append(SoundEffect.tags.like(f"%{tag}%"))
            search_query = search_query.filter(or_(*tag_filters))
        
        # 执行查询
        results = search_query.offset(skip).limit(limit).all()
        
        # 计算搜索耗时
        elapsed_time = time.time() - start_time
        
        return results, elapsed_time
    
    def count_search_results(
        self,
        query: str,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> int:
        """
        统计搜索结果数量
        
        参数:
            query: 搜索关键词
            category: 分类过滤（可选）
            tags: 标签过滤（可选）
        
        返回:
            int: 搜索结果数量
        """
        search_query = self.db.query(func.count(SoundEffect.id))
        
        # 全文搜索
        if query:
            search_pattern = f"%{query}%"
            search_query = search_query.filter(
                or_(
                    SoundEffect.name.like(search_pattern),
                    SoundEffect.category.like(search_pattern),
                    SoundEffect.tags.like(search_pattern)
                )
            )
        
        # 分类过滤
        if category:
            search_query = search_query.filter(SoundEffect.category == category)
        
        # 标签过滤
        if tags:
            tag_filters = []
            for tag in tags:
                tag_filters.append(SoundEffect.tags.like(f"%{tag}%"))
            search_query = search_query.filter(or_(*tag_filters))
        
        return search_query.scalar()
    
    def search_sound_effects_by_similarity(
        self,
        reference_tags: List[str],
        category: Optional[str] = None,
        top_k: int = 10
    ) -> List[SoundEffect]:
        """
        基于标签相似度搜索音效（简化版向量检索）
        
        参数:
            reference_tags: 参考标签列表
            category: 分类过滤（可选）
            top_k: 返回前k个结果
        
        返回:
            List[SoundEffect]: 相似音效列表
        
        注意：这是简化版实现，使用标签匹配度作为相似度。
        生产环境应使用pgvector扩展进行真正的向量检索。
        """
        # 获取候选音效
        query = self.db.query(SoundEffect)
        
        if category:
            query = query.filter(SoundEffect.category == category)
        
        # 获取所有音效
        all_effects = query.all()
        
        # 计算相似度（基于标签匹配数量）
        scored_effects = []
        for effect in all_effects:
            if not effect.tags:
                continue
            
            effect_tags = set(tag.strip() for tag in effect.tags.split(",") if tag.strip())
            reference_tags_set = set(reference_tags)
            
            # 计算交集数量作为相似度分数
            similarity_score = len(effect_tags & reference_tags_set)
            
            if similarity_score > 0:
                scored_effects.append((effect, similarity_score))
        
        # 按相似度排序
        scored_effects.sort(key=lambda x: x[1], reverse=True)
        
        # 返回前k个结果
        return [effect for effect, score in scored_effects[:top_k]]


    
    # ==================== 素材管理功能 ====================
    
    def upload_asset(
        self,
        file: BinaryIO,
        filename: str,
        asset_type: AssetType,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Asset:
        """
        上传素材
        
        参数:
            file: 文件对象
            filename: 文件名
            asset_type: 素材类型
            category: 分类（可选）
            tags: 标签列表（可选）
            description: 描述（可选）
            metadata: 元数据（可选），包含width、height、duration_seconds等
        
        返回:
            Asset: 创建的素材对象
        """
        # 生成唯一的对象键
        file_ext = Path(filename).suffix
        object_key = f"assets/{asset_type.value}/{uuid.uuid4()}{file_ext}"
        
        # 获取MIME类型
        mime_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        
        # 获取文件大小
        file.seek(0, 2)  # 移动到文件末尾
        file_size = file.tell()
        file.seek(0)  # 重置到文件开头
        
        # 上传文件
        file_url = self.storage.upload_file(file, object_key, mime_type)
        
        # 提取元数据
        width = metadata.get("width") if metadata else None
        height = metadata.get("height") if metadata else None
        duration_seconds = metadata.get("duration_seconds") if metadata else None
        
        # 将标签列表转换为逗号分隔的字符串
        tags_str = ",".join(tags) if tags else None
        
        # 创建素材记录
        asset = Asset(
            name=filename,
            asset_type=asset_type,
            file_url=file_url,
            file_size=file_size,
            mime_type=mime_type,
            duration_seconds=duration_seconds,
            width=width,
            height=height,
            category=category,
            tags=tags_str,
            description=description
        )
        
        self.db.add(asset)
        self.db.commit()
        self.db.refresh(asset)
        
        return asset
    
    def get_asset(self, asset_id: uuid.UUID) -> Optional[Asset]:
        """
        获取素材
        
        参数:
            asset_id: 素材ID
        
        返回:
            Optional[Asset]: 素材对象，如果不存在则返回None
        """
        return self.db.query(Asset).filter(Asset.id == asset_id).first()
    
    def list_assets(
        self,
        asset_type: Optional[AssetType] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Asset]:
        """
        列出素材
        
        参数:
            asset_type: 素材类型过滤（可选）
            category: 分类过滤（可选）
            tags: 标签过滤（可选）
            skip: 跳过数量
            limit: 返回数量限制
        
        返回:
            List[Asset]: 素材列表
        """
        query = self.db.query(Asset)
        
        # 类型过滤
        if asset_type:
            query = query.filter(Asset.asset_type == asset_type)
        
        # 分类过滤
        if category:
            query = query.filter(Asset.category == category)
        
        # 标签过滤
        if tags:
            tag_filters = []
            for tag in tags:
                tag_filters.append(Asset.tags.like(f"%{tag}%"))
            query = query.filter(or_(*tag_filters))
        
        return query.offset(skip).limit(limit).all()
    
    def update_asset(
        self,
        asset_id: uuid.UUID,
        name: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        description: Optional[str] = None
    ) -> Optional[Asset]:
        """
        更新素材
        
        参数:
            asset_id: 素材ID
            name: 新名称（可选）
            category: 新分类（可选）
            tags: 新标签列表（可选）
            description: 新描述（可选）
        
        返回:
            Optional[Asset]: 更新后的素材对象
        """
        asset = self.get_asset(asset_id)
        if not asset:
            return None
        
        if name is not None:
            asset.name = name
        if category is not None:
            asset.category = category
        if tags is not None:
            asset.tags = ",".join(tags) if tags else None
        if description is not None:
            asset.description = description
        
        self.db.commit()
        self.db.refresh(asset)
        
        return asset
    
    def delete_asset(self, asset_id: uuid.UUID) -> bool:
        """
        删除素材
        
        参数:
            asset_id: 素材ID
        
        返回:
            bool: 是否删除成功
        """
        asset = self.get_asset(asset_id)
        if not asset:
            return False
        
        # 从存储中删除文件
        # 提取对象键（从URL中）
        if asset.file_url.startswith("/storage/"):
            object_key = asset.file_url.replace("/storage/", "")
        else:
            # S3 URL格式
            object_key = asset.file_url.split("/")[-1]
        
        self.storage.delete_file(object_key)
        
        # 删除数据库记录
        self.db.delete(asset)
        self.db.commit()
        
        return True
    
    def generate_preview(self, asset_id: uuid.UUID) -> Optional[str]:
        """
        生成素材预览
        
        参数:
            asset_id: 素材ID
        
        返回:
            Optional[str]: 预览URL，如果生成失败则返回None
        
        注意：这是简化版实现，实际应使用图像处理库（如Pillow）或视频处理库（如FFmpeg）
        """
        asset = self.get_asset(asset_id)
        if not asset:
            return None
        
        # 简化实现：直接返回原文件URL作为预览
        # 实际应生成缩略图或低分辨率预览
        asset.preview_url = asset.file_url
        asset.thumbnail_url = asset.file_url
        
        self.db.commit()
        self.db.refresh(asset)
        
        return asset.preview_url
    
    def count_assets(
        self,
        asset_type: Optional[AssetType] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> int:
        """
        统计素材数量
        
        参数:
            asset_type: 素材类型过滤（可选）
            category: 分类过滤（可选）
            tags: 标签过滤（可选）
        
        返回:
            int: 素材数量
        """
        query = self.db.query(func.count(Asset.id))
        
        if asset_type:
            query = query.filter(Asset.asset_type == asset_type)
        
        if category:
            query = query.filter(Asset.category == category)
        
        if tags:
            tag_filters = []
            for tag in tags:
                tag_filters.append(Asset.tags.like(f"%{tag}%"))
            query = query.filter(or_(*tag_filters))
        
        return query.scalar()
    
    def search_assets(
        self,
        query: str,
        asset_type: Optional[AssetType] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[Asset], float]:
        """
        搜索素材（全文搜索）
        
        参数:
            query: 搜索关键词
            asset_type: 素材类型过滤（可选）
            category: 分类过滤（可选）
            tags: 标签过滤（可选）
            skip: 跳过数量
            limit: 返回数量限制
        
        返回:
            tuple[List[Asset], float]: (素材列表, 搜索耗时秒数)
        """
        start_time = time.time()
        
        # 构建搜索查询
        search_query = self.db.query(Asset)
        
        # 全文搜索：在名称、描述、分类和标签中搜索
        if query:
            search_pattern = f"%{query}%"
            search_query = search_query.filter(
                or_(
                    Asset.name.like(search_pattern),
                    Asset.description.like(search_pattern),
                    Asset.category.like(search_pattern),
                    Asset.tags.like(search_pattern)
                )
            )
        
        # 类型过滤
        if asset_type:
            search_query = search_query.filter(Asset.asset_type == asset_type)
        
        # 分类过滤
        if category:
            search_query = search_query.filter(Asset.category == category)
        
        # 标签过滤
        if tags:
            tag_filters = []
            for tag in tags:
                tag_filters.append(Asset.tags.like(f"%{tag}%"))
            search_query = search_query.filter(or_(*tag_filters))
        
        # 执行查询
        results = search_query.offset(skip).limit(limit).all()
        
        # 计算搜索耗时
        elapsed_time = time.time() - start_time
        
        return results, elapsed_time
