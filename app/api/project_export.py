"""项目导出API端点"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.models.user import User
from app.services.project_export import ProjectExportService


router = APIRouter(prefix="/projects", tags=["project-export"])


@router.get("/{project_id}/export")
async def export_project(
    project_id: str,
    include_media: bool = True,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    导出项目源文件
    
    参数:
        project_id: 项目ID
        include_media: 是否包含媒体文件（默认True）
    
    返回:
        ZIP文件流
    
    需求：11.6
    """
    try:
        # 创建导出服务
        export_service = ProjectExportService(db)
        
        # 导出项目
        zip_buffer = export_service.export_project(project_id, include_media)
        
        # 获取文件名
        filename = export_service.get_export_filename(project_id)
        
        # 返回文件流
        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"导出项目失败: {str(e)}"
        )


@router.get("/{project_id}/export/metadata-only")
async def export_project_metadata_only(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    仅导出项目元数据（不包含媒体文件）
    
    参数:
        project_id: 项目ID
    
    返回:
        ZIP文件流（仅包含JSON文件）
    
    需求：11.6
    """
    try:
        # 创建导出服务
        export_service = ProjectExportService(db)
        
        # 导出项目（不包含媒体）
        zip_buffer = export_service.export_project(project_id, include_media=False)
        
        # 获取文件名
        filename = export_service.get_export_filename(project_id).replace(".zip", "_metadata.zip")
        
        # 返回文件流
        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"导出项目元数据失败: {str(e)}"
        )
