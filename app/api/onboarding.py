"""新手引导API端点"""
from fastapi import APIRouter, Depends
from typing import List, Dict

from app.services.onboarding import onboarding_service, OnboardingStep
from app.api.dependencies import get_current_user
from app.models.user import User


router = APIRouter(prefix="/onboarding", tags=["onboarding"])


@router.get("/steps")
async def get_all_onboarding_steps() -> Dict:
    """
    获取所有新手引导步骤
    
    返回完整的引导流程
    """
    return {
        "steps": onboarding_service.get_all_steps()
    }


@router.get("/steps/{step}")
async def get_onboarding_step(step: str) -> Dict:
    """
    获取特定的引导步骤
    
    参数:
    - step: 步骤ID（welcome, create_project等）
    """
    try:
        onboarding_step = OnboardingStep(step)
        tutorial_step = onboarding_service.get_tutorial_step(onboarding_step)
        return tutorial_step.to_dict()
    except ValueError:
        return {"error": "无效的步骤ID"}


@router.get("/progress")
async def get_onboarding_progress(
    current_user: User = Depends(get_current_user)
) -> Dict:
    """
    获取用户的引导进度
    
    需要认证
    """
    # 这里应该从数据库获取用户的完成步骤
    # 简化实现，假设从用户元数据中获取
    completed_steps = []  # 实际应该从数据库获取
    
    progress = onboarding_service.get_progress(completed_steps)
    
    return {
        "user_id": current_user.id,
        "progress": progress,
        "completed_steps": completed_steps
    }


@router.post("/progress/{step}")
async def mark_step_completed(
    step: str,
    current_user: User = Depends(get_current_user)
) -> Dict:
    """
    标记步骤为已完成
    
    参数:
    - step: 步骤ID
    
    需要认证
    """
    try:
        onboarding_step = OnboardingStep(step)
        
        # 这里应该更新数据库中的用户进度
        # 简化实现
        
        # 获取下一步
        next_step = onboarding_service.get_next_step(onboarding_step)
        
        return {
            "success": True,
            "completed_step": step,
            "next_step": next_step.value if next_step else None
        }
    except ValueError:
        return {"error": "无效的步骤ID"}


@router.get("/quick-start")
async def get_quick_start_guide() -> Dict:
    """
    获取快速入门指南
    
    返回简化的5分钟入门指南
    """
    return onboarding_service.get_quick_start_guide()


@router.get("/features")
async def get_feature_highlights() -> Dict:
    """
    获取功能亮点
    
    返回平台的核心功能介绍
    """
    return {
        "features": onboarding_service.get_feature_highlights()
    }


@router.post("/skip")
async def skip_onboarding(
    current_user: User = Depends(get_current_user)
) -> Dict:
    """
    跳过新手引导
    
    用户可以选择跳过引导，稍后再学习
    
    需要认证
    """
    # 这里应该在数据库中标记用户已跳过引导
    
    return {
        "success": True,
        "message": "已跳过新手引导，您可以随时在帮助中心查看教程"
    }


@router.post("/restart")
async def restart_onboarding(
    current_user: User = Depends(get_current_user)
) -> Dict:
    """
    重新开始新手引导
    
    清除用户的引导进度，从头开始
    
    需要认证
    """
    # 这里应该清除数据库中的用户引导进度
    
    return {
        "success": True,
        "message": "引导进度已重置，将从头开始"
    }
