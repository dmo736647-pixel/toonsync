"""资源库管理属性测试"""
import pytest
from hypothesis import given, settings, strategies as st, HealthCheck
from sqlalchemy.orm import Session

from app.services.asset_library import AssetLibraryService
from app.models.user import SubscriptionTier


# ==================== Hypothesis策略 ====================

@st.composite
def sound_effect_data_strategy(draw):
    """生成音效数据策略"""
    name = draw(st.text(min_size=1, max_size=100))
    category = draw(st.sampled_from(["打斗", "对话", "环境", "情感转折"]))
    duration = draw(st.floats(min_value=0.1, max_value=300.0))
    # 标签不应包含逗号，因为逗号用作分隔符
    # 标签不应只包含空白字符
    tags = draw(st.lists(
        st.text(min_size=1, max_size=20).filter(lambda x: ',' not in x and x.strip() != ''),
        min_size=0,
        max_size=10
    ))
    
    return {
        "name": name,
        "category": category,
        "audio_file_url": f"s3://test/{name}.mp3",
        "duration_seconds": duration,
        "tags": tags
    }


# ==================== 属性测试 ====================

class TestAssetLibraryProperties:
    """资源库管理属性测试"""
    
    @given(sound_effect_data=sound_effect_data_strategy())
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_36_search_performance(
        self,
        db_session: Session,
        sound_effect_data: dict
    ):
        """
        属性36：素材搜索性能
        对于任意素材搜索请求，系统应在1秒内返回相关结果
        
        验证：需求10.2
        """
        service = AssetLibraryService(db_session)
        
        # 创建测试数据
        service.create_sound_effect(**sound_effect_data)
        
        # 执行搜索
        query = sound_effect_data["name"][:5] if len(sound_effect_data["name"]) >= 5 else sound_effect_data["name"]
        results, elapsed_time = service.search_sound_effects(query=query)
        
        # 验证搜索性能（需求10.2：应在1秒内完成）
        assert elapsed_time < 1.0, f"搜索耗时{elapsed_time}秒，超过1秒限制"
    
    @given(
        sound_effects=st.lists(sound_effect_data_strategy(), min_size=10, max_size=50)
    )
    @settings(
        max_examples=50,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
    )
    def test_property_36_bulk_search_performance(
        self,
        db_session: Session,
        sound_effects: list
    ):
        """
        属性36：批量数据搜索性能
        对于任意包含多个音效的数据库，搜索应在1秒内完成
        
        验证：需求10.2
        """
        service = AssetLibraryService(db_session)
        
        # 批量创建测试数据
        service.bulk_create_sound_effects(sound_effects)
        
        # 执行搜索
        results, elapsed_time = service.search_sound_effects(query="音效")
        
        # 验证搜索性能
        assert elapsed_time < 1.0, f"搜索耗时{elapsed_time}秒，超过1秒限制"
    
    @given(sound_effect_data=sound_effect_data_strategy())
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_37_asset_upload(
        self,
        db_session: Session,
        sound_effect_data: dict
    ):
        """
        属性37：素材上传
        对于任意上传的素材文件，系统应成功存储素材
        
        验证：需求10.3
        """
        service = AssetLibraryService(db_session)
        
        # 创建音效（模拟上传）
        created = service.create_sound_effect(**sound_effect_data)
        
        # 验证创建成功
        assert created.id is not None
        assert created.name == sound_effect_data["name"]
        assert created.category == sound_effect_data["category"]
        assert created.audio_file_url == sound_effect_data["audio_file_url"]
        
        # 验证可以检索
        retrieved = service.get_sound_effect(created.id)
        assert retrieved is not None
        assert retrieved.id == created.id
    
    @given(sound_effect_data=sound_effect_data_strategy())
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_38_asset_metadata_tagging(
        self,
        db_session: Session,
        sound_effect_data: dict
    ):
        """
        属性38：素材元数据标记
        对于任意上传的素材，系统应自动标记元数据
        
        验证：需求10.4
        """
        service = AssetLibraryService(db_session)
        
        # 创建音效
        created = service.create_sound_effect(**sound_effect_data)
        
        # 验证元数据已标记
        assert created.name is not None
        assert created.category is not None
        assert created.duration_seconds > 0
        
        # 如果有标签，验证标签已保存
        if sound_effect_data["tags"]:
            assert created.tags is not None
            saved_tags = [tag.strip() for tag in created.tags.split(",") if tag.strip()]
            assert len(saved_tags) == len(sound_effect_data["tags"])
    
    @given(
        sound_effect_data=sound_effect_data_strategy(),
        query=st.text(min_size=1, max_size=50)
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_search_returns_relevant_results(
        self,
        db_session: Session,
        sound_effect_data: dict,
        query: str
    ):
        """
        属性：搜索返回相关结果
        对于任意搜索查询，系统应返回包含查询关键词的结果
        """
        service = AssetLibraryService(db_session)
        
        # 创建包含查询关键词的音效
        sound_effect_data["name"] = f"{query}_测试音效"
        created = service.create_sound_effect(**sound_effect_data)
        
        # 搜索
        results, elapsed_time = service.search_sound_effects(query=query)
        
        # 验证结果包含创建的音效
        result_ids = [r.id for r in results]
        assert created.id in result_ids, "搜索结果应包含匹配的音效"
    
    @given(
        category=st.sampled_from(["打斗", "对话", "环境", "情感转折"]),
        sound_effects=st.lists(sound_effect_data_strategy(), min_size=5, max_size=20)
    )
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_search_category_filter(
        self,
        db_session: Session,
        category: str,
        sound_effects: list
    ):
        """
        属性：分类过滤正确性
        对于任意分类过滤，搜索结果应只包含该分类的音效
        """
        service = AssetLibraryService(db_session)
        
        # 设置所有音效为指定分类
        for se in sound_effects:
            se["category"] = category
        
        # 批量创建
        service.bulk_create_sound_effects(sound_effects)
        
        # 按分类搜索
        results, elapsed_time = service.search_sound_effects(
            query="",
            category=category
        )
        
        # 验证所有结果都是指定分类
        assert all(r.category == category for r in results), \
            f"所有搜索结果应属于分类'{category}'"
    
    @given(
        reference_tags=st.lists(
            st.text(min_size=1, max_size=20).filter(lambda x: ',' not in x and x.strip() != ''),
            min_size=1,
            max_size=5
        ),
        sound_effects=st.lists(sound_effect_data_strategy(), min_size=5, max_size=20)
    )
    @settings(
        max_examples=50,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
        deadline=500  # 增加超时时间到500ms
    )
    def test_property_similarity_search_returns_similar_items(
        self,
        db_session: Session,
        reference_tags: list,
        sound_effects: list
    ):
        """
        属性：相似度搜索返回相似项
        对于任意参考标签，相似度搜索应返回包含相同标签的音效
        """
        service = AssetLibraryService(db_session)
        
        # 创建一个包含参考标签的音效
        matching_effect = sound_effects[0].copy()
        matching_effect["tags"] = reference_tags
        service.create_sound_effect(**matching_effect)
        
        # 创建其他音效
        for se in sound_effects[1:]:
            service.create_sound_effect(**se)
        
        # 基于相似度搜索
        results = service.search_sound_effects_by_similarity(
            reference_tags=reference_tags,
            top_k=10
        )
        
        # 验证返回了结果（至少应该返回我们创建的匹配音效）
        assert len(results) > 0, "相似度搜索应返回结果"
        
        # 第一个结果应该是最匹配的（包含所有参考标签）
        if results:
            first_result_tags = set(tag.strip() for tag in results[0].tags.split(",") if tag.strip()) if results[0].tags else set()
            reference_tags_set = set(reference_tags)
            # 至少应该有一些标签匹配
            assert len(first_result_tags & reference_tags_set) > 0, \
                "最相似的结果应包含至少一个参考标签"
    
    @given(
        sound_effects=st.lists(sound_effect_data_strategy(), min_size=1, max_size=100)
    )
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_count_matches_actual_results(
        self,
        db_session: Session,
        sound_effects: list
    ):
        """
        属性：统计数量与实际结果一致
        对于任意搜索，统计的结果数量应与实际返回的结果数量一致
        """
        service = AssetLibraryService(db_session)
        
        # 批量创建
        service.bulk_create_sound_effects(sound_effects)
        
        # 搜索并统计
        query = "音效"
        results, elapsed_time = service.search_sound_effects(query=query, limit=1000)
        count = service.count_search_results(query=query)
        
        # 验证数量一致
        assert len(results) == count, \
            f"搜索结果数量({len(results)})应与统计数量({count})一致"
    
    @given(
        sound_effect_data=sound_effect_data_strategy(),
        new_tags=st.lists(
            st.text(min_size=1, max_size=20).filter(lambda x: ',' not in x and x.strip()),
            min_size=1,
            max_size=5
        )
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_metadata_update_persists(
        self,
        db_session: Session,
        sound_effect_data: dict,
        new_tags: list
    ):
        """
        属性：元数据更新持久化
        对于任意元数据更新，更新应正确保存到数据库
        """
        service = AssetLibraryService(db_session)
        
        # 创建音效
        created = service.create_sound_effect(**sound_effect_data)
        
        # 更新标签
        updated = service.update_sound_effect(
            sound_effect_id=created.id,
            tags=new_tags
        )
        
        # 验证更新成功
        assert updated is not None
        assert updated.tags is not None
        
        # 重新获取验证持久化
        retrieved = service.get_sound_effect(created.id)
        assert retrieved.tags == updated.tags
        
        # 验证标签内容
        saved_tags = [tag.strip() for tag in retrieved.tags.split(",") if tag.strip()]
        assert len(saved_tags) == len(new_tags)
    
    @given(
        sound_effects=st.lists(sound_effect_data_strategy(), min_size=2, max_size=10)
    )
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_bulk_operations_atomic(
        self,
        db_session: Session,
        sound_effects: list
    ):
        """
        属性：批量操作原子性
        对于任意批量创建操作，要么全部成功，要么全部失败
        """
        service = AssetLibraryService(db_session)
        
        # 批量创建
        created = service.bulk_create_sound_effects(sound_effects)
        
        # 验证创建数量
        assert len(created) == len(sound_effects), \
            "批量创建应创建所有音效"
        
        # 验证所有音效都可以检索
        for effect in created:
            retrieved = service.get_sound_effect(effect.id)
            assert retrieved is not None, "批量创建的音效应可以检索"



# ==================== 素材管理属性测试 ====================

@st.composite
def asset_data_strategy(draw):
    """生成素材数据策略"""
    from io import BytesIO
    from app.models.asset import AssetType
    
    name = draw(st.text(min_size=1, max_size=100))
    asset_type = draw(st.sampled_from([AssetType.IMAGE, AssetType.AUDIO, AssetType.VIDEO]))
    category = draw(st.sampled_from(["分类A", "分类B", "分类C", None]))
    tags = draw(st.lists(
        st.text(min_size=1, max_size=20).filter(lambda x: ',' not in x and x.strip() != ''),
        min_size=0,
        max_size=5
    ))
    description = draw(st.text(min_size=0, max_size=200))
    
    # 创建模拟文件
    file_content = b"test file content"
    file = BytesIO(file_content)
    
    # 元数据
    metadata = {}
    if asset_type == AssetType.IMAGE or asset_type == AssetType.VIDEO:
        metadata["width"] = draw(st.integers(min_value=100, max_value=4000))
        metadata["height"] = draw(st.integers(min_value=100, max_value=4000))
    if asset_type == AssetType.AUDIO or asset_type == AssetType.VIDEO:
        metadata["duration_seconds"] = draw(st.floats(min_value=0.1, max_value=300.0))
    
    return {
        "file": file,
        "filename": f"{name}.{asset_type.value}",
        "asset_type": asset_type,
        "category": category,
        "tags": tags,
        "description": description if description else None,
        "metadata": metadata if metadata else None
    }


class TestAssetManagementProperties:
    """素材管理属性测试"""
    
    @given(asset_data=asset_data_strategy())
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_37_asset_upload(
        self,
        db_session: Session,
        asset_data: dict
    ):
        """
        属性37：素材上传
        对于任意上传的素材文件，系统应成功存储素材
        
        验证：需求10.3
        """
        service = AssetLibraryService(db_session)
        
        # 上传素材
        asset = service.upload_asset(**asset_data)
        
        # 验证上传成功
        assert asset.id is not None
        assert asset.name == asset_data["filename"]
        assert asset.asset_type == asset_data["asset_type"]
        assert asset.file_url is not None
        assert asset.file_size > 0
        
        # 验证可以检索
        retrieved = service.get_asset(asset.id)
        assert retrieved is not None
        assert retrieved.id == asset.id
    
    @given(asset_data=asset_data_strategy())
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_38_asset_metadata_tagging(
        self,
        db_session: Session,
        asset_data: dict
    ):
        """
        属性38：素材元数据标记
        对于任意上传的素材，系统应自动标记元数据
        
        验证：需求10.4
        """
        service = AssetLibraryService(db_session)
        
        # 上传素材
        asset = service.upload_asset(**asset_data)
        
        # 验证元数据已标记
        assert asset.name is not None
        assert asset.asset_type is not None
        assert asset.file_size > 0
        assert asset.mime_type is not None
        
        # 验证类型特定的元数据
        from app.models.asset import AssetType
        if asset_data["metadata"]:
            if asset_data["asset_type"] in [AssetType.IMAGE, AssetType.VIDEO]:
                if "width" in asset_data["metadata"]:
                    assert asset.width == asset_data["metadata"]["width"]
                if "height" in asset_data["metadata"]:
                    assert asset.height == asset_data["metadata"]["height"]
            
            if asset_data["asset_type"] in [AssetType.AUDIO, AssetType.VIDEO]:
                if "duration_seconds" in asset_data["metadata"]:
                    assert asset.duration_seconds == asset_data["metadata"]["duration_seconds"]
        
        # 验证标签
        if asset_data["tags"]:
            assert asset.tags is not None
            saved_tags = [tag.strip() for tag in asset.tags.split(",") if tag.strip()]
            assert len(saved_tags) == len(asset_data["tags"])
    
    @given(asset_data=asset_data_strategy())
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_40_asset_preview(
        self,
        db_session: Session,
        asset_data: dict
    ):
        """
        属性40：素材预览
        对于任意素材，系统应提供预览和快速试用功能
        
        验证：需求10.7
        """
        service = AssetLibraryService(db_session)
        
        # 上传素材
        asset = service.upload_asset(**asset_data)
        
        # 生成预览
        preview_url = service.generate_preview(asset.id)
        
        # 验证预览生成成功
        assert preview_url is not None
        assert isinstance(preview_url, str)
        assert len(preview_url) > 0
        
        # 验证预览URL已保存
        retrieved = service.get_asset(asset.id)
        assert retrieved.preview_url is not None
    
    @given(
        assets=st.lists(asset_data_strategy(), min_size=2, max_size=10)
    )
    @settings(
        max_examples=50,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
    )
    def test_property_asset_upload_multiple(
        self,
        db_session: Session,
        assets: list
    ):
        """
        属性：批量上传素材
        对于任意多个素材文件，系统应成功存储所有素材
        """
        service = AssetLibraryService(db_session)
        
        uploaded_ids = []
        
        # 批量上传
        for asset_data in assets:
            asset = service.upload_asset(**asset_data)
            uploaded_ids.append(asset.id)
        
        # 验证所有素材都已上传
        assert len(uploaded_ids) == len(assets)
        
        # 验证所有素材都可以检索
        for asset_id in uploaded_ids:
            retrieved = service.get_asset(asset_id)
            assert retrieved is not None
    
    @given(
        asset_data=asset_data_strategy(),
        new_tags=st.lists(
            st.text(min_size=1, max_size=20).filter(lambda x: ',' not in x and x.strip() != ''),
            min_size=1,
            max_size=5
        )
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_asset_metadata_update(
        self,
        db_session: Session,
        asset_data: dict,
        new_tags: list
    ):
        """
        属性：素材元数据更新
        对于任意素材元数据更新，更新应正确保存
        """
        service = AssetLibraryService(db_session)
        
        # 上传素材
        asset = service.upload_asset(**asset_data)
        
        # 更新元数据
        updated = service.update_asset(
            asset_id=asset.id,
            tags=new_tags,
            description="更新后的描述"
        )
        
        # 验证更新成功
        assert updated is not None
        assert updated.description == "更新后的描述"
        
        # 验证标签更新
        if new_tags:
            assert updated.tags is not None
            saved_tags = [tag.strip() for tag in updated.tags.split(",") if tag.strip()]
            assert len(saved_tags) == len(new_tags)
    
    @given(asset_data=asset_data_strategy())
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_asset_deletion(
        self,
        db_session: Session,
        asset_data: dict
    ):
        """
        属性：素材删除
        对于任意素材，删除操作应成功移除素材
        """
        service = AssetLibraryService(db_session)
        
        # 上传素材
        asset = service.upload_asset(**asset_data)
        asset_id = asset.id
        
        # 删除素材
        success = service.delete_asset(asset_id)
        
        # 验证删除成功
        assert success is True
        
        # 验证素材已不存在
        retrieved = service.get_asset(asset_id)
        assert retrieved is None
    
    @given(
        assets=st.lists(asset_data_strategy(), min_size=5, max_size=20)
    )
    @settings(
        max_examples=50,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
    )
    def test_property_asset_search_performance(
        self,
        db_session: Session,
        assets: list
    ):
        """
        属性：素材搜索性能
        对于任意素材搜索，系统应在1秒内返回结果
        """
        service = AssetLibraryService(db_session)
        
        # 批量上传素材
        for asset_data in assets:
            service.upload_asset(**asset_data)
        
        # 搜索素材
        results, elapsed_time = service.search_assets(query="test")
        
        # 验证搜索性能
        assert elapsed_time < 1.0, f"搜索耗时{elapsed_time}秒，超过1秒限制"



# Feature: short-drama-production-tool, Property 39: 素材访问权限控制
@given(
    subscription_tier=st.sampled_from([
        SubscriptionTier.FREE,
        SubscriptionTier.PAY_PER_USE,
        SubscriptionTier.PROFESSIONAL,
        SubscriptionTier.ENTERPRISE
    ]),
    asset_category=st.sampled_from(["basic", "premium", "advanced_premium"])
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_39_asset_access_permission_control(
    db_session: Session,
    subscription_tier: SubscriptionTier,
    asset_category: str
):
    """
    属性39：素材访问权限控制
    
    对于任意素材访问请求，系统应根据用户订阅层级正确控制访问权限
    （专业版和企业版可访问高级素材库）
    
    **验证：需求10.5**
    """
    from tests.factories import UserFactory
    from app.models.asset import Asset, AssetType
    
    service = AssetLibraryService(db_session)
    
    # 创建用户
    user = UserFactory.create(db_session, subscription_tier=subscription_tier)
    
    # 创建素材
    asset = Asset(
        name=f"测试素材_{asset_category}",
        asset_type=AssetType.IMAGE,
        file_url=f"s3://test/{asset_category}.jpg",
        file_size=1024,
        mime_type="image/jpeg",
        category=asset_category
    )
    db_session.add(asset)
    db_session.commit()
    
    # 检查权限
    has_permission = service.check_asset_access_permission(user, asset)
    
    # 验证权限规则
    is_premium = "premium" in asset_category.lower()
    is_privileged_user = subscription_tier in [
        SubscriptionTier.PROFESSIONAL,
        SubscriptionTier.ENTERPRISE
    ]
    
    if is_premium:
        # 高级素材只有专业版和企业版可以访问
        assert has_permission == is_privileged_user, \
            f"订阅层级{subscription_tier}访问{asset_category}素材的权限应为{is_privileged_user}，实际为{has_permission}"
    else:
        # 基础素材所有用户都可以访问
        assert has_permission is True, \
            f"所有用户都应该能访问基础素材，但订阅层级{subscription_tier}无法访问"


# Feature: short-drama-production-tool, Property 39: 音效访问权限控制
@given(
    subscription_tier=st.sampled_from([
        SubscriptionTier.FREE,
        SubscriptionTier.PAY_PER_USE,
        SubscriptionTier.PROFESSIONAL,
        SubscriptionTier.ENTERPRISE
    ]),
    sound_effect_category=st.sampled_from(["basic", "premium", "advanced_premium"])
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_39_sound_effect_access_permission_control(
    db_session: Session,
    subscription_tier: SubscriptionTier,
    sound_effect_category: str
):
    """
    属性39：音效访问权限控制
    
    对于任意音效访问请求，系统应根据用户订阅层级正确控制访问权限
    （专业版和企业版可访问高级音效库）
    
    **验证：需求10.5**
    """
    from tests.factories import UserFactory
    
    service = AssetLibraryService(db_session)
    
    # 创建用户
    user = UserFactory.create(db_session, subscription_tier=subscription_tier)
    
    # 创建音效
    sound_effect = service.create_sound_effect(
        name=f"测试音效_{sound_effect_category}",
        category=sound_effect_category,
        audio_file_url=f"s3://test/{sound_effect_category}.mp3",
        duration_seconds=1.5
    )
    
    # 检查权限
    has_permission = service.check_sound_effect_access_permission(user, sound_effect)
    
    # 验证权限规则
    is_premium = "premium" in sound_effect_category.lower()
    is_privileged_user = subscription_tier in [
        SubscriptionTier.PROFESSIONAL,
        SubscriptionTier.ENTERPRISE
    ]
    
    if is_premium:
        # 高级音效只有专业版和企业版可以访问
        assert has_permission == is_privileged_user, \
            f"订阅层级{subscription_tier}访问{sound_effect_category}音效的权限应为{is_privileged_user}，实际为{has_permission}"
    else:
        # 基础音效所有用户都可以访问
        assert has_permission is True, \
            f"所有用户都应该能访问基础音效，但订阅层级{subscription_tier}无法访问"


# Feature: short-drama-production-tool, Property 39: 批量素材过滤
@given(
    subscription_tier=st.sampled_from([
        SubscriptionTier.FREE,
        SubscriptionTier.PAY_PER_USE,
        SubscriptionTier.PROFESSIONAL,
        SubscriptionTier.ENTERPRISE
    ]),
    num_basic_assets=st.integers(min_value=1, max_value=5),
    num_premium_assets=st.integers(min_value=1, max_value=5)
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_39_filter_accessible_assets(
    db_session: Session,
    subscription_tier: SubscriptionTier,
    num_basic_assets: int,
    num_premium_assets: int
):
    """
    属性39：批量素材过滤
    
    对于任意素材列表，系统应正确过滤出用户可访问的素材
    
    **验证：需求10.5**
    """
    from tests.factories import UserFactory
    from app.models.asset import Asset, AssetType
    
    service = AssetLibraryService(db_session)
    
    # 创建用户
    user = UserFactory.create(db_session, subscription_tier=subscription_tier)
    
    # 创建基础素材
    basic_assets = []
    for i in range(num_basic_assets):
        asset = Asset(
            name=f"基础素材_{i}",
            asset_type=AssetType.IMAGE,
            file_url=f"s3://test/basic_{i}.jpg",
            file_size=1024,
            mime_type="image/jpeg",
            category="basic"
        )
        db_session.add(asset)
        basic_assets.append(asset)
    
    # 创建高级素材
    premium_assets = []
    for i in range(num_premium_assets):
        asset = Asset(
            name=f"高级素材_{i}",
            asset_type=AssetType.IMAGE,
            file_url=f"s3://test/premium_{i}.jpg",
            file_size=1024,
            mime_type="image/jpeg",
            category="premium"
        )
        db_session.add(asset)
        premium_assets.append(asset)
    
    db_session.commit()
    
    # 过滤素材
    all_assets = basic_assets + premium_assets
    accessible_assets = service.filter_accessible_assets(user, all_assets)
    
    # 验证过滤结果
    is_privileged_user = subscription_tier in [
        SubscriptionTier.PROFESSIONAL,
        SubscriptionTier.ENTERPRISE
    ]
    
    if is_privileged_user:
        # 专业版和企业版可以访问所有素材
        assert len(accessible_assets) == num_basic_assets + num_premium_assets, \
            f"专业版/企业版用户应该能访问所有{num_basic_assets + num_premium_assets}个素材，实际只能访问{len(accessible_assets)}个"
    else:
        # 免费版和按量付费只能访问基础素材
        assert len(accessible_assets) == num_basic_assets, \
            f"免费版/按量付费用户应该只能访问{num_basic_assets}个基础素材，实际能访问{len(accessible_assets)}个"
        
        # 验证所有可访问的素材都是基础素材
        for asset in accessible_assets:
            assert asset.category == "basic", \
                f"免费版/按量付费用户不应该能访问{asset.category}类别的素材"
