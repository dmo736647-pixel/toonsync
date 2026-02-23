"""资源库管理单元测试"""
import pytest
from sqlalchemy.orm import Session

from app.services.asset_library import AssetLibraryService
from app.models.sound_effect import SoundEffect


class TestSoundEffectManagement:
    """音效库管理测试"""
    
    def test_create_sound_effect(self, db_session: Session):
        """测试创建音效"""
        service = AssetLibraryService(db_session)
        
        sound_effect = service.create_sound_effect(
            name="测试音效",
            category="测试分类",
            audio_file_url="s3://test/test.mp3",
            duration_seconds=1.5,
            tags=["测试", "标签"]
        )
        
        assert sound_effect.id is not None
        assert sound_effect.name == "测试音效"
        assert sound_effect.category == "测试分类"
        assert sound_effect.duration_seconds == 1.5
        assert sound_effect.tags == "测试,标签"
    
    def test_get_sound_effect(self, db_session: Session):
        """测试获取音效"""
        service = AssetLibraryService(db_session)
        
        # 创建音效
        created = service.create_sound_effect(
            name="测试音效",
            category="测试分类",
            audio_file_url="s3://test/test.mp3",
            duration_seconds=1.5
        )
        
        # 获取音效
        retrieved = service.get_sound_effect(created.id)
        
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.name == "测试音效"
    
    def test_get_nonexistent_sound_effect(self, db_session: Session):
        """测试获取不存在的音效"""
        service = AssetLibraryService(db_session)
        
        import uuid
        result = service.get_sound_effect(uuid.uuid4())
        
        assert result is None
    
    def test_list_sound_effects(self, db_session: Session):
        """测试列出音效"""
        service = AssetLibraryService(db_session)
        
        # 创建多个音效
        for i in range(5):
            service.create_sound_effect(
                name=f"音效{i}",
                category="测试分类",
                audio_file_url=f"s3://test/test{i}.mp3",
                duration_seconds=1.0 + i * 0.5
            )
        
        # 列出音效
        results = service.list_sound_effects(skip=0, limit=10)
        
        assert len(results) == 5
    
    def test_list_sound_effects_with_category_filter(self, db_session: Session):
        """测试按分类过滤列出音效"""
        service = AssetLibraryService(db_session)
        
        # 创建不同分类的音效
        service.create_sound_effect(
            name="音效1",
            category="分类A",
            audio_file_url="s3://test/test1.mp3",
            duration_seconds=1.0
        )
        service.create_sound_effect(
            name="音效2",
            category="分类B",
            audio_file_url="s3://test/test2.mp3",
            duration_seconds=1.0
        )
        service.create_sound_effect(
            name="音效3",
            category="分类A",
            audio_file_url="s3://test/test3.mp3",
            duration_seconds=1.0
        )
        
        # 按分类过滤
        results = service.list_sound_effects(category="分类A")
        
        assert len(results) == 2
        assert all(se.category == "分类A" for se in results)
    
    def test_list_sound_effects_with_tags_filter(self, db_session: Session):
        """测试按标签过滤列出音效"""
        service = AssetLibraryService(db_session)
        
        # 创建带标签的音效
        service.create_sound_effect(
            name="音效1",
            category="测试",
            audio_file_url="s3://test/test1.mp3",
            duration_seconds=1.0,
            tags=["标签A", "标签B"]
        )
        service.create_sound_effect(
            name="音效2",
            category="测试",
            audio_file_url="s3://test/test2.mp3",
            duration_seconds=1.0,
            tags=["标签C"]
        )
        service.create_sound_effect(
            name="音效3",
            category="测试",
            audio_file_url="s3://test/test3.mp3",
            duration_seconds=1.0,
            tags=["标签A", "标签C"]
        )
        
        # 按标签过滤
        results = service.list_sound_effects(tags=["标签A"])
        
        assert len(results) == 2
    
    def test_update_sound_effect(self, db_session: Session):
        """测试更新音效"""
        service = AssetLibraryService(db_session)
        
        # 创建音效
        created = service.create_sound_effect(
            name="原始名称",
            category="原始分类",
            audio_file_url="s3://test/test.mp3",
            duration_seconds=1.0
        )
        
        # 更新音效
        updated = service.update_sound_effect(
            sound_effect_id=created.id,
            name="新名称",
            category="新分类",
            tags=["新标签"]
        )
        
        assert updated is not None
        assert updated.name == "新名称"
        assert updated.category == "新分类"
        assert updated.tags == "新标签"
    
    def test_update_nonexistent_sound_effect(self, db_session: Session):
        """测试更新不存在的音效"""
        service = AssetLibraryService(db_session)
        
        import uuid
        result = service.update_sound_effect(
            sound_effect_id=uuid.uuid4(),
            name="新名称"
        )
        
        assert result is None
    
    def test_delete_sound_effect(self, db_session: Session):
        """测试删除音效"""
        service = AssetLibraryService(db_session)
        
        # 创建音效
        created = service.create_sound_effect(
            name="测试音效",
            category="测试分类",
            audio_file_url="s3://test/test.mp3",
            duration_seconds=1.0
        )
        
        # 删除音效
        success = service.delete_sound_effect(created.id)
        
        assert success is True
        
        # 验证已删除
        retrieved = service.get_sound_effect(created.id)
        assert retrieved is None
    
    def test_delete_nonexistent_sound_effect(self, db_session: Session):
        """测试删除不存在的音效"""
        service = AssetLibraryService(db_session)
        
        import uuid
        success = service.delete_sound_effect(uuid.uuid4())
        
        assert success is False
    
    def test_get_categories(self, db_session: Session):
        """测试获取所有分类"""
        service = AssetLibraryService(db_session)
        
        # 创建不同分类的音效
        service.create_sound_effect(
            name="音效1",
            category="分类A",
            audio_file_url="s3://test/test1.mp3",
            duration_seconds=1.0
        )
        service.create_sound_effect(
            name="音效2",
            category="分类B",
            audio_file_url="s3://test/test2.mp3",
            duration_seconds=1.0
        )
        service.create_sound_effect(
            name="音效3",
            category="分类A",
            audio_file_url="s3://test/test3.mp3",
            duration_seconds=1.0
        )
        
        # 获取分类
        categories = service.get_categories()
        
        assert len(categories) == 2
        assert "分类A" in categories
        assert "分类B" in categories
    
    def test_get_tags(self, db_session: Session):
        """测试获取所有标签"""
        service = AssetLibraryService(db_session)
        
        # 创建带标签的音效
        service.create_sound_effect(
            name="音效1",
            category="测试",
            audio_file_url="s3://test/test1.mp3",
            duration_seconds=1.0,
            tags=["标签A", "标签B"]
        )
        service.create_sound_effect(
            name="音效2",
            category="测试",
            audio_file_url="s3://test/test2.mp3",
            duration_seconds=1.0,
            tags=["标签C"]
        )
        
        # 获取标签
        tags = service.get_tags()
        
        assert len(tags) == 3
        assert "标签A" in tags
        assert "标签B" in tags
        assert "标签C" in tags
    
    def test_count_sound_effects(self, db_session: Session):
        """测试统计音效数量"""
        service = AssetLibraryService(db_session)
        
        # 创建音效
        for i in range(5):
            service.create_sound_effect(
                name=f"音效{i}",
                category="测试分类",
                audio_file_url=f"s3://test/test{i}.mp3",
                duration_seconds=1.0
            )
        
        # 统计数量
        count = service.count_sound_effects()
        
        assert count == 5
    
    def test_count_sound_effects_with_filters(self, db_session: Session):
        """测试带过滤条件的统计"""
        service = AssetLibraryService(db_session)
        
        # 创建不同分类的音效
        service.create_sound_effect(
            name="音效1",
            category="分类A",
            audio_file_url="s3://test/test1.mp3",
            duration_seconds=1.0
        )
        service.create_sound_effect(
            name="音效2",
            category="分类B",
            audio_file_url="s3://test/test2.mp3",
            duration_seconds=1.0
        )
        service.create_sound_effect(
            name="音效3",
            category="分类A",
            audio_file_url="s3://test/test3.mp3",
            duration_seconds=1.0
        )
        
        # 按分类统计
        count = service.count_sound_effects(category="分类A")
        
        assert count == 2
    
    def test_bulk_create_sound_effects(self, db_session: Session):
        """测试批量创建音效"""
        service = AssetLibraryService(db_session)
        
        # 批量创建
        data = [
            {
                "name": f"音效{i}",
                "category": "测试分类",
                "audio_file_url": f"s3://test/test{i}.mp3",
                "duration_seconds": 1.0 + i * 0.5,
                "tags": [f"标签{i}"]
            }
            for i in range(10)
        ]
        
        created = service.bulk_create_sound_effects(data)
        
        assert len(created) == 10
        
        # 验证创建成功
        count = service.count_sound_effects()
        assert count == 10


class TestSoundEffectSearch:
    """音效搜索测试"""
    
    def test_search_by_name(self, db_session: Session):
        """测试按名称搜索"""
        service = AssetLibraryService(db_session)
        
        # 创建测试数据
        service.create_sound_effect(
            name="爆炸音效",
            category="打斗",
            audio_file_url="s3://test/explosion.mp3",
            duration_seconds=2.0
        )
        service.create_sound_effect(
            name="脚步声",
            category="对话",
            audio_file_url="s3://test/footstep.mp3",
            duration_seconds=0.5
        )
        
        # 搜索
        results, elapsed_time = service.search_sound_effects(query="爆炸")
        
        assert len(results) == 1
        assert results[0].name == "爆炸音效"
        assert elapsed_time < 1.0  # 搜索应在1秒内完成
    
    def test_search_by_category(self, db_session: Session):
        """测试按分类搜索"""
        service = AssetLibraryService(db_session)
        
        # 创建测试数据
        service.create_sound_effect(
            name="音效1",
            category="打斗",
            audio_file_url="s3://test/test1.mp3",
            duration_seconds=1.0
        )
        service.create_sound_effect(
            name="音效2",
            category="对话",
            audio_file_url="s3://test/test2.mp3",
            duration_seconds=1.0
        )
        
        # 搜索
        results, elapsed_time = service.search_sound_effects(query="打")
        
        assert len(results) == 1
        assert results[0].category == "打斗"
    
    def test_search_by_tags(self, db_session: Session):
        """测试按标签搜索"""
        service = AssetLibraryService(db_session)
        
        # 创建测试数据
        service.create_sound_effect(
            name="音效1",
            category="测试",
            audio_file_url="s3://test/test1.mp3",
            duration_seconds=1.0,
            tags=["爆炸", "武器"]
        )
        service.create_sound_effect(
            name="音效2",
            category="测试",
            audio_file_url="s3://test/test2.mp3",
            duration_seconds=1.0,
            tags=["脚步", "走路"]
        )
        
        # 搜索
        results, elapsed_time = service.search_sound_effects(query="爆炸")
        
        assert len(results) == 1
        assert "爆炸" in results[0].tags
    
    def test_search_with_category_filter(self, db_session: Session):
        """测试带分类过滤的搜索"""
        service = AssetLibraryService(db_session)
        
        # 创建测试数据
        service.create_sound_effect(
            name="爆炸音效",
            category="打斗",
            audio_file_url="s3://test/explosion.mp3",
            duration_seconds=2.0
        )
        service.create_sound_effect(
            name="爆炸声",
            category="环境",
            audio_file_url="s3://test/explosion2.mp3",
            duration_seconds=1.5
        )
        
        # 搜索（只在打斗分类中）
        results, elapsed_time = service.search_sound_effects(
            query="爆炸",
            category="打斗"
        )
        
        assert len(results) == 1
        assert results[0].category == "打斗"
    
    def test_search_with_tags_filter(self, db_session: Session):
        """测试带标签过滤的搜索"""
        service = AssetLibraryService(db_session)
        
        # 创建测试数据
        service.create_sound_effect(
            name="音效1",
            category="测试",
            audio_file_url="s3://test/test1.mp3",
            duration_seconds=1.0,
            tags=["标签A", "标签B"]
        )
        service.create_sound_effect(
            name="音效2",
            category="测试",
            audio_file_url="s3://test/test2.mp3",
            duration_seconds=1.0,
            tags=["标签C"]
        )
        
        # 搜索（只包含标签A的）
        results, elapsed_time = service.search_sound_effects(
            query="音效",
            tags=["标签A"]
        )
        
        assert len(results) == 1
        assert "标签A" in results[0].tags
    
    def test_search_performance(self, db_session: Session):
        """测试搜索性能（应在1秒内完成）"""
        service = AssetLibraryService(db_session)
        
        # 创建大量测试数据
        data = [
            {
                "name": f"音效{i}",
                "category": f"分类{i % 5}",
                "audio_file_url": f"s3://test/test{i}.mp3",
                "duration_seconds": 1.0,
                "tags": [f"标签{i % 10}"]
            }
            for i in range(100)
        ]
        service.bulk_create_sound_effects(data)
        
        # 搜索
        results, elapsed_time = service.search_sound_effects(query="音效")
        
        # 验证性能（需求10.2：搜索应在1秒内完成）
        assert elapsed_time < 1.0
        assert len(results) > 0
    
    def test_count_search_results(self, db_session: Session):
        """测试统计搜索结果数量"""
        service = AssetLibraryService(db_session)
        
        # 创建测试数据
        for i in range(10):
            service.create_sound_effect(
                name=f"爆炸音效{i}",
                category="打斗",
                audio_file_url=f"s3://test/explosion{i}.mp3",
                duration_seconds=1.0
            )
        
        # 统计搜索结果
        count = service.count_search_results(query="爆炸")
        
        assert count == 10
    
    def test_search_by_similarity(self, db_session: Session):
        """测试基于相似度的搜索"""
        service = AssetLibraryService(db_session)
        
        # 创建测试数据
        service.create_sound_effect(
            name="音效1",
            category="打斗",
            audio_file_url="s3://test/test1.mp3",
            duration_seconds=1.0,
            tags=["爆炸", "武器", "战斗"]
        )
        service.create_sound_effect(
            name="音效2",
            category="打斗",
            audio_file_url="s3://test/test2.mp3",
            duration_seconds=1.0,
            tags=["爆炸", "火焰"]
        )
        service.create_sound_effect(
            name="音效3",
            category="环境",
            audio_file_url="s3://test/test3.mp3",
            duration_seconds=1.0,
            tags=["风声", "自然"]
        )
        
        # 基于标签相似度搜索
        results = service.search_sound_effects_by_similarity(
            reference_tags=["爆炸", "战斗"],
            top_k=2
        )
        
        assert len(results) <= 2
        # 第一个结果应该是音效1（有2个匹配标签）
        assert results[0].name == "音效1"
    
    def test_search_by_similarity_with_category_filter(self, db_session: Session):
        """测试带分类过滤的相似度搜索"""
        service = AssetLibraryService(db_session)
        
        # 创建测试数据
        service.create_sound_effect(
            name="音效1",
            category="打斗",
            audio_file_url="s3://test/test1.mp3",
            duration_seconds=1.0,
            tags=["爆炸", "武器"]
        )
        service.create_sound_effect(
            name="音效2",
            category="环境",
            audio_file_url="s3://test/test2.mp3",
            duration_seconds=1.0,
            tags=["爆炸", "自然"]
        )
        
        # 只在打斗分类中搜索
        results = service.search_sound_effects_by_similarity(
            reference_tags=["爆炸"],
            category="打斗",
            top_k=10
        )
        
        assert len(results) == 1
        assert results[0].category == "打斗"



# ==================== 素材管理测试 ====================

class TestAssetManagement:
    """素材管理测试"""
    
    def test_upload_asset(self, db_session):
        """测试上传素材"""
        from io import BytesIO
        from app.models.asset import AssetType
        
        service = AssetLibraryService(db_session)
        
        # 创建模拟文件
        file_content = b"test image content"
        file = BytesIO(file_content)
        
        # 上传素材
        asset = service.upload_asset(
            file=file,
            filename="test_image.jpg",
            asset_type=AssetType.IMAGE,
            category="测试分类",
            tags=["标签1", "标签2"],
            description="测试描述",
            metadata={"width": 1920, "height": 1080}
        )
        
        # 验证
        assert asset.id is not None
        assert asset.name == "test_image.jpg"
        assert asset.asset_type == AssetType.IMAGE
        assert asset.file_size == len(file_content)
        assert asset.category == "测试分类"
        assert asset.width == 1920
        assert asset.height == 1080
        assert asset.description == "测试描述"
    
    def test_get_asset(self, db_session):
        """测试获取素材"""
        from io import BytesIO
        from app.models.asset import AssetType
        
        service = AssetLibraryService(db_session)
        
        # 创建素材
        file = BytesIO(b"test content")
        created = service.upload_asset(
            file=file,
            filename="test.jpg",
            asset_type=AssetType.IMAGE
        )
        
        # 获取素材
        retrieved = service.get_asset(created.id)
        
        # 验证
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.name == "test.jpg"
    
    def test_list_assets(self, db_session):
        """测试列出素材"""
        from io import BytesIO
        from app.models.asset import AssetType
        
        service = AssetLibraryService(db_session)
        
        # 创建多个素材
        for i in range(5):
            file = BytesIO(b"test content")
            service.upload_asset(
                file=file,
                filename=f"test_{i}.jpg",
                asset_type=AssetType.IMAGE,
                category="测试"
            )
        
        # 列出素材
        assets = service.list_assets()
        
        # 验证
        assert len(assets) == 5
    
    def test_list_assets_with_type_filter(self, db_session):
        """测试按类型过滤列出素材"""
        from io import BytesIO
        from app.models.asset import AssetType
        
        service = AssetLibraryService(db_session)
        
        # 创建不同类型的素材
        for asset_type in [AssetType.IMAGE, AssetType.AUDIO, AssetType.VIDEO]:
            file = BytesIO(b"test content")
            service.upload_asset(
                file=file,
                filename=f"test.{asset_type.value}",
                asset_type=asset_type
            )
        
        # 按类型过滤
        images = service.list_assets(asset_type=AssetType.IMAGE)
        audios = service.list_assets(asset_type=AssetType.AUDIO)
        
        # 验证
        assert len(images) == 1
        assert len(audios) == 1
        assert images[0].asset_type == AssetType.IMAGE
        assert audios[0].asset_type == AssetType.AUDIO
    
    def test_list_assets_with_category_filter(self, db_session):
        """测试按分类过滤列出素材"""
        from io import BytesIO
        from app.models.asset import AssetType
        
        service = AssetLibraryService(db_session)
        
        # 创建不同分类的素材
        for category in ["分类A", "分类B"]:
            file = BytesIO(b"test content")
            service.upload_asset(
                file=file,
                filename=f"test_{category}.jpg",
                asset_type=AssetType.IMAGE,
                category=category
            )
        
        # 按分类过滤
        assets_a = service.list_assets(category="分类A")
        assets_b = service.list_assets(category="分类B")
        
        # 验证
        assert len(assets_a) == 1
        assert len(assets_b) == 1
        assert assets_a[0].category == "分类A"
        assert assets_b[0].category == "分类B"
    
    def test_list_assets_with_tags_filter(self, db_session):
        """测试按标签过滤列出素材"""
        from io import BytesIO
        from app.models.asset import AssetType
        
        service = AssetLibraryService(db_session)
        
        # 创建带标签的素材
        file1 = BytesIO(b"test content 1")
        service.upload_asset(
            file=file1,
            filename="test1.jpg",
            asset_type=AssetType.IMAGE,
            tags=["标签A", "标签B"]
        )
        
        file2 = BytesIO(b"test content 2")
        service.upload_asset(
            file=file2,
            filename="test2.jpg",
            asset_type=AssetType.IMAGE,
            tags=["标签C"]
        )
        
        # 按标签过滤
        assets_a = service.list_assets(tags=["标签A"])
        assets_c = service.list_assets(tags=["标签C"])
        
        # 验证
        assert len(assets_a) == 1
        assert len(assets_c) == 1
    
    def test_update_asset(self, db_session):
        """测试更新素材"""
        from io import BytesIO
        from app.models.asset import AssetType
        
        service = AssetLibraryService(db_session)
        
        # 创建素材
        file = BytesIO(b"test content")
        created = service.upload_asset(
            file=file,
            filename="test.jpg",
            asset_type=AssetType.IMAGE,
            category="旧分类"
        )
        
        # 更新素材
        updated = service.update_asset(
            asset_id=created.id,
            name="新名称.jpg",
            category="新分类",
            tags=["新标签"],
            description="新描述"
        )
        
        # 验证
        assert updated is not None
        assert updated.name == "新名称.jpg"
        assert updated.category == "新分类"
        assert updated.description == "新描述"
    
    def test_delete_asset(self, db_session):
        """测试删除素材"""
        from io import BytesIO
        from app.models.asset import AssetType
        
        service = AssetLibraryService(db_session)
        
        # 创建素材
        file = BytesIO(b"test content")
        created = service.upload_asset(
            file=file,
            filename="test.jpg",
            asset_type=AssetType.IMAGE
        )
        
        # 删除素材
        success = service.delete_asset(created.id)
        
        # 验证
        assert success is True
        
        # 确认已删除
        retrieved = service.get_asset(created.id)
        assert retrieved is None
    
    def test_generate_preview(self, db_session):
        """测试生成预览"""
        from io import BytesIO
        from app.models.asset import AssetType
        
        service = AssetLibraryService(db_session)
        
        # 创建素材
        file = BytesIO(b"test content")
        created = service.upload_asset(
            file=file,
            filename="test.jpg",
            asset_type=AssetType.IMAGE
        )
        
        # 生成预览
        preview_url = service.generate_preview(created.id)
        
        # 验证
        assert preview_url is not None
        assert isinstance(preview_url, str)
    
    def test_count_assets(self, db_session):
        """测试统计素材数量"""
        from io import BytesIO
        from app.models.asset import AssetType
        
        service = AssetLibraryService(db_session)
        
        # 创建素材
        for i in range(3):
            file = BytesIO(b"test content")
            service.upload_asset(
                file=file,
                filename=f"test_{i}.jpg",
                asset_type=AssetType.IMAGE
            )
        
        # 统计
        count = service.count_assets()
        
        # 验证
        assert count == 3
    
    def test_search_assets(self, db_session):
        """测试搜索素材"""
        from io import BytesIO
        from app.models.asset import AssetType
        
        service = AssetLibraryService(db_session)
        
        # 创建素材
        file = BytesIO(b"test content")
        service.upload_asset(
            file=file,
            filename="搜索测试.jpg",
            asset_type=AssetType.IMAGE,
            description="这是一个测试素材"
        )
        
        # 搜索
        results, elapsed_time = service.search_assets(query="搜索")
        
        # 验证
        assert len(results) == 1
        assert results[0].name == "搜索测试.jpg"
        assert elapsed_time < 1.0
    
    def test_search_assets_performance(self, db_session):
        """测试搜索性能"""
        from io import BytesIO
        from app.models.asset import AssetType
        
        service = AssetLibraryService(db_session)
        
        # 创建多个素材
        for i in range(20):
            file = BytesIO(b"test content")
            service.upload_asset(
                file=file,
                filename=f"test_{i}.jpg",
                asset_type=AssetType.IMAGE
            )
        
        # 搜索
        results, elapsed_time = service.search_assets(query="test")
        
        # 验证性能
        assert elapsed_time < 1.0



class TestAssetAccessPermission:
    """素材访问权限控制测试"""
    
    def test_free_user_can_access_basic_asset(self, db_session: Session):
        """测试免费用户可以访问基础素材"""
        from app.models.user import SubscriptionTier
        from app.models.asset import Asset, AssetType
        from tests.factories import UserFactory
        
        service = AssetLibraryService(db_session)
        
        # 创建免费用户
        user = UserFactory.create(db_session, subscription_tier=SubscriptionTier.FREE)
        
        # 创建基础素材
        asset = Asset(
            name="基础素材",
            asset_type=AssetType.IMAGE,
            file_url="s3://test/basic.jpg",
            file_size=1024,
            mime_type="image/jpeg",
            category="basic"
        )
        db_session.add(asset)
        db_session.commit()
        
        # 检查权限
        has_permission = service.check_asset_access_permission(user, asset)
        assert has_permission is True
    
    def test_free_user_cannot_access_premium_asset(self, db_session: Session):
        """测试免费用户无法访问高级素材"""
        from app.models.user import SubscriptionTier
        from app.models.asset import Asset, AssetType
        from tests.factories import UserFactory
        
        service = AssetLibraryService(db_session)
        
        # 创建免费用户
        user = UserFactory.create(db_session, subscription_tier=SubscriptionTier.FREE)
        
        # 创建高级素材
        asset = Asset(
            name="高级素材",
            asset_type=AssetType.IMAGE,
            file_url="s3://test/premium.jpg",
            file_size=1024,
            mime_type="image/jpeg",
            category="premium"
        )
        db_session.add(asset)
        db_session.commit()
        
        # 检查权限
        has_permission = service.check_asset_access_permission(user, asset)
        assert has_permission is False
    
    def test_professional_user_can_access_premium_asset(self, db_session: Session):
        """测试专业版用户可以访问高级素材"""
        from app.models.user import SubscriptionTier
        from app.models.asset import Asset, AssetType
        from tests.factories import UserFactory
        
        service = AssetLibraryService(db_session)
        
        # 创建专业版用户
        user = UserFactory.create(db_session, subscription_tier=SubscriptionTier.PROFESSIONAL)
        
        # 创建高级素材
        asset = Asset(
            name="高级素材",
            asset_type=AssetType.IMAGE,
            file_url="s3://test/premium.jpg",
            file_size=1024,
            mime_type="image/jpeg",
            category="premium"
        )
        db_session.add(asset)
        db_session.commit()
        
        # 检查权限
        has_permission = service.check_asset_access_permission(user, asset)
        assert has_permission is True
    
    def test_enterprise_user_can_access_premium_asset(self, db_session: Session):
        """测试企业版用户可以访问高级素材"""
        from app.models.user import SubscriptionTier
        from app.models.asset import Asset, AssetType
        from tests.factories import UserFactory
        
        service = AssetLibraryService(db_session)
        
        # 创建企业版用户
        user = UserFactory.create(db_session, subscription_tier=SubscriptionTier.ENTERPRISE)
        
        # 创建高级素材
        asset = Asset(
            name="高级素材",
            asset_type=AssetType.IMAGE,
            file_url="s3://test/premium.jpg",
            file_size=1024,
            mime_type="image/jpeg",
            category="premium"
        )
        db_session.add(asset)
        db_session.commit()
        
        # 检查权限
        has_permission = service.check_asset_access_permission(user, asset)
        assert has_permission is True
    
    def test_pay_per_use_user_cannot_access_premium_asset(self, db_session: Session):
        """测试按量付费用户无法访问高级素材"""
        from app.models.user import SubscriptionTier
        from app.models.asset import Asset, AssetType
        from tests.factories import UserFactory
        
        service = AssetLibraryService(db_session)
        
        # 创建按量付费用户
        user = UserFactory.create(db_session, subscription_tier=SubscriptionTier.PAY_PER_USE)
        
        # 创建高级素材
        asset = Asset(
            name="高级素材",
            asset_type=AssetType.IMAGE,
            file_url="s3://test/premium.jpg",
            file_size=1024,
            mime_type="image/jpeg",
            category="premium"
        )
        db_session.add(asset)
        db_session.commit()
        
        # 检查权限
        has_permission = service.check_asset_access_permission(user, asset)
        assert has_permission is False
    
    def test_filter_accessible_assets(self, db_session: Session):
        """测试过滤用户可访问的素材列表"""
        from app.models.user import SubscriptionTier
        from app.models.asset import Asset, AssetType
        from tests.factories import UserFactory
        
        service = AssetLibraryService(db_session)
        
        # 创建免费用户
        user = UserFactory.create(db_session, subscription_tier=SubscriptionTier.FREE)
        
        # 创建基础素材
        basic_asset = Asset(
            name="基础素材",
            asset_type=AssetType.IMAGE,
            file_url="s3://test/basic.jpg",
            file_size=1024,
            mime_type="image/jpeg",
            category="basic"
        )
        db_session.add(basic_asset)
        
        # 创建高级素材
        premium_asset = Asset(
            name="高级素材",
            asset_type=AssetType.IMAGE,
            file_url="s3://test/premium.jpg",
            file_size=1024,
            mime_type="image/jpeg",
            category="premium"
        )
        db_session.add(premium_asset)
        db_session.commit()
        
        # 过滤素材
        all_assets = [basic_asset, premium_asset]
        accessible_assets = service.filter_accessible_assets(user, all_assets)
        
        # 免费用户只能访问基础素材
        assert len(accessible_assets) == 1
        assert accessible_assets[0].id == basic_asset.id
    
    def test_free_user_can_access_basic_sound_effect(self, db_session: Session):
        """测试免费用户可以访问基础音效"""
        from app.models.user import SubscriptionTier
        from tests.factories import UserFactory
        
        service = AssetLibraryService(db_session)
        
        # 创建免费用户
        user = UserFactory.create(db_session, subscription_tier=SubscriptionTier.FREE)
        
        # 创建基础音效
        sound_effect = service.create_sound_effect(
            name="基础音效",
            category="basic",
            audio_file_url="s3://test/basic.mp3",
            duration_seconds=1.5
        )
        
        # 检查权限
        has_permission = service.check_sound_effect_access_permission(user, sound_effect)
        assert has_permission is True
    
    def test_free_user_cannot_access_premium_sound_effect(self, db_session: Session):
        """测试免费用户无法访问高级音效"""
        from app.models.user import SubscriptionTier
        from tests.factories import UserFactory
        
        service = AssetLibraryService(db_session)
        
        # 创建免费用户
        user = UserFactory.create(db_session, subscription_tier=SubscriptionTier.FREE)
        
        # 创建高级音效
        sound_effect = service.create_sound_effect(
            name="高级音效",
            category="premium",
            audio_file_url="s3://test/premium.mp3",
            duration_seconds=1.5
        )
        
        # 检查权限
        has_permission = service.check_sound_effect_access_permission(user, sound_effect)
        assert has_permission is False
    
    def test_professional_user_can_access_premium_sound_effect(self, db_session: Session):
        """测试专业版用户可以访问高级音效"""
        from app.models.user import SubscriptionTier
        from tests.factories import UserFactory
        
        service = AssetLibraryService(db_session)
        
        # 创建专业版用户
        user = UserFactory.create(db_session, subscription_tier=SubscriptionTier.PROFESSIONAL)
        
        # 创建高级音效
        sound_effect = service.create_sound_effect(
            name="高级音效",
            category="premium",
            audio_file_url="s3://test/premium.mp3",
            duration_seconds=1.5
        )
        
        # 检查权限
        has_permission = service.check_sound_effect_access_permission(user, sound_effect)
        assert has_permission is True
    
    def test_filter_accessible_sound_effects(self, db_session: Session):
        """测试过滤用户可访问的音效列表"""
        from app.models.user import SubscriptionTier
        from tests.factories import UserFactory
        
        service = AssetLibraryService(db_session)
        
        # 创建免费用户
        user = UserFactory.create(db_session, subscription_tier=SubscriptionTier.FREE)
        
        # 创建基础音效
        basic_se = service.create_sound_effect(
            name="基础音效",
            category="basic",
            audio_file_url="s3://test/basic.mp3",
            duration_seconds=1.5
        )
        
        # 创建高级音效
        premium_se = service.create_sound_effect(
            name="高级音效",
            category="premium",
            audio_file_url="s3://test/premium.mp3",
            duration_seconds=1.5
        )
        
        # 过滤音效
        all_sound_effects = [basic_se, premium_se]
        accessible_sound_effects = service.filter_accessible_sound_effects(user, all_sound_effects)
        
        # 免费用户只能访问基础音效
        assert len(accessible_sound_effects) == 1
        assert accessible_sound_effects[0].id == basic_se.id

