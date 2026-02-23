"""备份管理API端点"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from pydantic import BaseModel
from datetime import datetime

from app.services.backup import backup_service
from app.api.dependencies import get_current_user
from app.models.user import User


router = APIRouter(prefix="/backup", tags=["backup"])


class BackupInfo(BaseModel):
    """备份信息"""
    name: str
    file: str
    size_bytes: int
    created_at: datetime


class BackupCreateResponse(BaseModel):
    """备份创建响应"""
    success: bool
    backup_file: str
    message: str


class BackupRestoreRequest(BaseModel):
    """备份恢复请求"""
    backup_file: str


class BackupRestoreResponse(BaseModel):
    """备份恢复响应"""
    success: bool
    message: str


@router.post("/create", response_model=BackupCreateResponse)
async def create_backup(
    current_user: User = Depends(get_current_user)
):
    """
    创建数据库备份
    
    需求：11.2
    """
    try:
        backup_file = backup_service.create_backup()
        
        return BackupCreateResponse(
            success=True,
            backup_file=backup_file,
            message="备份创建成功"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"创建备份失败: {str(e)}"
        )


@router.post("/restore", response_model=BackupRestoreResponse)
async def restore_backup(
    request: BackupRestoreRequest,
    current_user: User = Depends(get_current_user)
):
    """
    从备份恢复数据库
    
    需求：11.3
    """
    try:
        success = backup_service.restore_backup(request.backup_file)
        
        return BackupRestoreResponse(
            success=success,
            message="数据恢复成功"
        )
    
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"恢复备份失败: {str(e)}"
        )


@router.get("/list", response_model=List[BackupInfo])
async def list_backups(
    current_user: User = Depends(get_current_user)
):
    """
    列出所有备份
    """
    try:
        backups = backup_service.list_backups()
        return [BackupInfo(**backup) for backup in backups]
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取备份列表失败: {str(e)}"
        )


@router.get("/latest")
async def get_latest_backup(
    current_user: User = Depends(get_current_user)
):
    """
    获取最新的备份
    """
    try:
        latest_backup = backup_service.get_latest_backup()
        
        if latest_backup is None:
            raise HTTPException(
                status_code=404,
                detail="没有可用的备份"
            )
        
        return {"backup_file": latest_backup}
    
    except HTTPException:
        raise
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取最新备份失败: {str(e)}"
        )


@router.delete("/cleanup")
async def cleanup_old_backups(
    current_user: User = Depends(get_current_user)
):
    """
    清理超过保留期的备份
    
    需求：11.4
    """
    try:
        deleted_count = backup_service.cleanup_old_backups()
        
        return {
            "success": True,
            "deleted_count": deleted_count,
            "message": f"已删除{deleted_count}个过期备份"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"清理备份失败: {str(e)}"
        )
