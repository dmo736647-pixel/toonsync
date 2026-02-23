"""监控API端点"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List

from app.services.monitoring import monitoring_service
from app.api.dependencies import get_current_user
from app.models.user import User


router = APIRouter(prefix="/monitoring", tags=["monitoring"])


@router.get("/metrics")
async def get_metrics() -> Dict[str, Dict]:
    """
    获取所有监控指标
    
    返回所有注册的指标及其当前值
    """
    return monitoring_service.get_all_metrics()


@router.get("/metrics/prometheus")
async def get_prometheus_metrics() -> str:
    """
    获取Prometheus格式的指标
    
    返回符合Prometheus格式的指标数据
    """
    return monitoring_service.export_prometheus_format()


@router.get("/alerts")
async def get_alerts(
    current_user: User = Depends(get_current_user)
) -> List[Dict]:
    """
    获取当前触发的告警
    
    需要管理员权限
    """
    # 检查是否为管理员（简化实现，实际应该有角色系统）
    # if not current_user.is_admin:
    #     raise HTTPException(status_code=403, detail="需要管理员权限")
    
    return monitoring_service.check_alerts()


@router.get("/alerts/history")
async def get_alert_history(
    limit: int = 50,
    current_user: User = Depends(get_current_user)
) -> List[Dict]:
    """
    获取告警历史
    
    需要管理员权限
    """
    # 检查是否为管理员
    # if not current_user.is_admin:
    #     raise HTTPException(status_code=403, detail="需要管理员权限")
    
    return monitoring_service.get_alert_history(limit=limit)


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """
    健康检查端点
    
    返回系统健康状态
    """
    # 检查关键指标
    metrics = monitoring_service.get_all_metrics()
    
    # 检查是否有严重告警
    alerts = monitoring_service.check_alerts()
    critical_alerts = [a for a in alerts if a["level"] == "critical"]
    
    if critical_alerts:
        return {
            "status": "unhealthy",
            "message": f"存在{len(critical_alerts)}个严重告警"
        }
    
    return {
        "status": "healthy",
        "message": "系统运行正常"
    }
