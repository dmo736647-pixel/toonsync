"""Hypothesis测试策略"""
from hypothesis import strategies as st
from datetime import datetime, timedelta
import uuid

from app.models import SubscriptionTier, AspectRatio, RenderStyle


# 基础策略
email_strategy = st.emails()
password_strategy = st.text(min_size=8, max_size=50)
uuid_strategy = st.uuids()
positive_float_strategy = st.floats(min_value=0.1, max_value=1000.0)
duration_strategy = st.floats(min_value=1.0, max_value=180.0)
project_name_strategy = lambda: st.text(
    min_size=1, 
    max_size=50, 
    alphabet=st.characters(whitelist_categories=('L', 'N', 'P', 'Z'))
)
duration_minutes_strategy = lambda: st.floats(min_value=0.5, max_value=180.0)


# 枚举策略
subscription_tier_strategy = st.sampled_from(list(SubscriptionTier))
aspect_ratio_strategy = st.sampled_from(list(AspectRatio))
render_style_strategy = st.sampled_from(list(RenderStyle))


# 日期时间策略
@st.composite
def datetime_strategy(draw):
    """生成日期时间"""
    days_offset = draw(st.integers(min_value=-365, max_value=365))
    return datetime.utcnow() + timedelta(days=days_offset)


# 用户数据策略
@st.composite
def user_data_strategy(draw):
    """生成用户数据"""
    return {
        "email": draw(email_strategy),
        "password": draw(password_strategy),
        "subscription_tier": draw(subscription_tier_strategy),
        "remaining_quota_minutes": draw(positive_float_strategy),
    }


# 项目数据策略
@st.composite
def project_data_strategy(draw):
    """生成项目数据"""
    return {
        "name": draw(st.text(min_size=1, max_size=255)),
        "aspect_ratio": draw(aspect_ratio_strategy),
        "duration_minutes": draw(st.one_of(st.none(), duration_strategy)),
        "script": draw(st.one_of(st.none(), st.text(min_size=10, max_size=5000))),
    }


# 角色数据策略
@st.composite
def character_data_strategy(draw):
    """生成角色数据"""
    return {
        "name": draw(st.text(min_size=1, max_size=255)),
        "reference_image_url": f"/storage/test/{draw(uuid_strategy)}.jpg",
        "style": draw(render_style_strategy),
    }


# 音频数据策略
@st.composite
def audio_data_strategy(draw):
    """生成音频数据"""
    return {
        "audio_file_url": f"/storage/test/{draw(uuid_strategy)}.mp3",
        "duration_seconds": draw(positive_float_strategy),
        "transcript": draw(st.one_of(st.none(), st.text(min_size=10, max_size=1000))),
    }


# 音效数据策略
@st.composite
def sound_effect_data_strategy(draw):
    """生成音效数据"""
    categories = ["打斗", "对话", "环境", "情感转折"]
    return {
        "name": draw(st.text(min_size=1, max_size=255)),
        "category": draw(st.sampled_from(categories)),
        "audio_file_url": f"/storage/sound_effects/{draw(uuid_strategy)}.mp3",
        "duration_seconds": draw(st.floats(min_value=0.1, max_value=60.0)),
        "tags": draw(st.lists(st.text(min_size=1, max_size=50), min_size=0, max_size=10)),
    }


# 订阅数据策略
@st.composite
def subscription_data_strategy(draw):
    """生成订阅数据"""
    start_date = draw(datetime_strategy())
    duration_days = draw(st.integers(min_value=1, max_value=365))
    end_date = start_date + timedelta(days=duration_days)
    
    return {
        "plan": draw(subscription_tier_strategy),
        "quota_minutes": draw(positive_float_strategy),
        "start_date": start_date,
        "end_date": end_date,
        "auto_renew": draw(st.booleans()),
    }
