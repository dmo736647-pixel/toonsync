"""测试数据工厂"""
from datetime import datetime, timedelta
import uuid
from typing import Optional

from app.models import (
    User,
    Project,
    Character,
    StoryboardFrame,
    AudioTrack,
    SoundEffect,
    Subscription,
    SubscriptionTier,
    AspectRatio,
    RenderStyle,
)


class UserFactory:
    """用户工厂"""
    
    @staticmethod
    def build(
        email: Optional[str] = None,
        password_hash: str = "hashed_password",
        subscription_tier: SubscriptionTier = SubscriptionTier.FREE,
        remaining_quota_minutes: float = 5.0,
    ) -> User:
        """创建用户实例（不保存到数据库）"""
        return User(
            email=email or f"user_{uuid.uuid4().hex[:8]}@example.com",
            password_hash=password_hash,
            subscription_tier=subscription_tier,
            remaining_quota_minutes=remaining_quota_minutes,
        )
    
    @staticmethod
    def create(
        db_session,
        email: Optional[str] = None,
        password_hash: str = "hashed_password",
        subscription_tier: SubscriptionTier = SubscriptionTier.FREE,
        remaining_quota_minutes: float = 5.0,
    ) -> User:
        """创建用户实例并保存到数据库"""
        user = User(
            id=uuid.uuid4(),
            email=email or f"user_{uuid.uuid4().hex[:8]}@example.com",
            password_hash=password_hash,
            subscription_tier=subscription_tier,
            remaining_quota_minutes=remaining_quota_minutes,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user


class ProjectFactory:
    """项目工厂"""
    
    @staticmethod
    def build(
        user_id: Optional[uuid.UUID] = None,
        name: Optional[str] = None,
        aspect_ratio: AspectRatio = AspectRatio.VERTICAL_9_16,
        duration_minutes: Optional[float] = None,
        script: Optional[str] = None,
    ) -> Project:
        """创建项目实例（不保存到数据库）"""
        return Project(
            user_id=user_id or uuid.uuid4(),
            name=name or f"项目_{uuid.uuid4().hex[:8]}",
            aspect_ratio=aspect_ratio,
            duration_minutes=duration_minutes,
            script=script,
        )
    
    @staticmethod
    def create(
        user_id: uuid.UUID,
        name: Optional[str] = None,
        aspect_ratio: AspectRatio = AspectRatio.VERTICAL_9_16,
        duration_minutes: Optional[float] = None,
        script: Optional[str] = None,
    ) -> Project:
        """创建项目实例"""
        return Project(
            id=uuid.uuid4(),
            user_id=user_id,
            name=name or f"项目_{uuid.uuid4().hex[:8]}",
            aspect_ratio=aspect_ratio,
            duration_minutes=duration_minutes,
            script=script,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )


class CharacterFactory:
    """角色工厂"""
    
    @staticmethod
    def create(
        project_id: uuid.UUID,
        name: Optional[str] = None,
        reference_image_url: str = "/storage/test/character.jpg",
        consistency_model_url: Optional[str] = None,
        style: RenderStyle = RenderStyle.ANIME,
    ) -> Character:
        """创建角色实例"""
        return Character(
            id=uuid.uuid4(),
            project_id=project_id,
            name=name or f"角色_{uuid.uuid4().hex[:8]}",
            reference_image_url=reference_image_url,
            consistency_model_url=consistency_model_url,
            style=style,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )


class StoryboardFrameFactory:
    """分镜工厂"""
    
    @staticmethod
    def create(
        project_id: uuid.UUID,
        sequence_number: int,
        character_id: Optional[uuid.UUID] = None,
        scene_description: Optional[str] = None,
        image_url: Optional[str] = None,
        duration_seconds: Optional[float] = None,
        lip_sync_keyframes: Optional[dict] = None,
    ) -> StoryboardFrame:
        """创建分镜实例"""
        return StoryboardFrame(
            id=uuid.uuid4(),
            project_id=project_id,
            sequence_number=sequence_number,
            character_id=character_id,
            scene_description=scene_description,
            image_url=image_url,
            duration_seconds=duration_seconds,
            lip_sync_keyframes=lip_sync_keyframes,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )


class AudioTrackFactory:
    """音频轨道工厂"""
    
    @staticmethod
    def create(
        project_id: uuid.UUID,
        audio_file_url: str = "/storage/test/audio.mp3",
        duration_seconds: float = 60.0,
        transcript: Optional[str] = None,
        audio_analysis: Optional[dict] = None,
    ) -> AudioTrack:
        """创建音频轨道实例"""
        return AudioTrack(
            id=uuid.uuid4(),
            project_id=project_id,
            audio_file_url=audio_file_url,
            duration_seconds=duration_seconds,
            transcript=transcript,
            audio_analysis=audio_analysis,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )


class SoundEffectFactory:
    """音效工厂"""
    
    @staticmethod
    def create(
        name: Optional[str] = None,
        category: str = "环境",
        audio_file_url: str = "/storage/sound_effects/test.mp3",
        duration_seconds: float = 5.0,
        tags: Optional[list] = None,
    ) -> SoundEffect:
        """创建音效实例"""
        return SoundEffect(
            id=uuid.uuid4(),
            name=name or f"音效_{uuid.uuid4().hex[:8]}",
            category=category,
            audio_file_url=audio_file_url,
            duration_seconds=duration_seconds,
            tags=tags or ["测试"],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )


class SubscriptionFactory:
    """订阅工厂"""
    
    @staticmethod
    def create(
        user_id: uuid.UUID,
        plan: SubscriptionTier = SubscriptionTier.PROFESSIONAL,
        quota_minutes: float = 50.0,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        auto_renew: bool = True,
    ) -> Subscription:
        """创建订阅实例"""
        now = datetime.utcnow()
        return Subscription(
            id=uuid.uuid4(),
            user_id=user_id,
            plan=plan,
            quota_minutes=quota_minutes,
            start_date=start_date or now,
            end_date=end_date or (now + timedelta(days=30)),
            auto_renew=auto_renew,
            created_at=now,
            updated_at=now,
        )
