"""
工作流编排API端点
"""
import io
from typing import List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from PIL import Image

from app.api.dependencies import get_current_user, get_db
from app.core.storage import StorageManager
from app.models.user import User
from app.schemas.workflow import (
    CreateWorkflowRequest,
    WorkflowResponse,
    ExecuteWorkflowRequest,
    WorkflowResultResponse,
    WorkflowProgressResponse,
    PauseWorkflowRequest,
    ResumeWorkflowRequest
)
from app.services.workflow_orchestrator import WorkflowOrchestrator
from app.models.project import Project
from app.models.character import Character
from pydantic import BaseModel, Field


class StartWorkflowFromProjectRequest(BaseModel):
    """从项目启动工作流请求"""
    project_id: str = Field(..., description="项目ID")
    auto_mode: bool = Field(default=True, description="是否自动执行所有步骤")


router = APIRouter(prefix="/workflows", tags=["workflows"])


@router.post("/start_from_project", response_model=WorkflowResponse)
async def start_workflow_from_project(
    request: StartWorkflowFromProjectRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    从现有项目启动工作流
    """
    try:
        # 1. 获取项目
        project = db.query(Project).filter(Project.id == request.project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="项目不存在")
        
        if str(project.user_id) != str(current_user.id):
            raise HTTPException(status_code=403, detail="无权访问此项目")
            
        if not project.script:
            raise HTTPException(status_code=400, detail="项目缺少剧本")
            
        # 2. 获取角色
        characters = db.query(Character).filter(Character.project_id == project.id).all()
        if not characters:
            raise HTTPException(status_code=400, detail="项目缺少角色")
            
        # 3. 准备数据
        orchestrator = WorkflowOrchestrator()
        storage = StorageManager() # Changed from StorageService to StorageManager as imported
        
        character_images = []
        # 下载角色参考图
        import requests
        for char in characters:
            if char.reference_image_url:
                try:
                    # 如果是本地存储的URL (e.g. /storage/...), 需要转换或读取
                    # 这里假设是完整的URL
                    if char.reference_image_url.startswith("http"):
                        resp = requests.get(char.reference_image_url)
                        if resp.status_code == 200:
                            character_images.append(resp.content)
                        else:
                            print(f"Failed to download image for char {char.name}")
                    else:
                        # 尝试作为本地文件读取
                        # 假设 storage path mapping
                        pass 
                except Exception as e:
                    print(f"Error downloading image for char {char.name}: {e}")
        
        if not character_images:
             # 如果没有下载到图片，可能需要处理，或者允许无图（但Storyboard生成需要）
             pass

        # 4. 创建工作流
        workflow = orchestrator.create_workflow(
            user_id=str(current_user.id),
            script=project.script,
            character_images=character_images,
            audio_data=None, # 暂不支持从项目自动获取音频
            config={
                "project_id": str(project.id),
                "aspect_ratio": project.aspect_ratio.value
            }
        )
        
        # 5. 如果自动模式，开始执行
        if request.auto_mode:
            background_tasks.add_task(orchestrator.execute_workflow, workflow.workflow_id, auto_mode=True)
        
        return WorkflowResponse(**workflow.to_dict())

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"启动工作流失败: {str(e)}")




@router.post("/create", response_model=WorkflowResponse)
async def create_workflow(
    request: CreateWorkflowRequest,
    current_user: User = Depends(get_current_user)
):
    """
    创建完整工作流
    
    工作流步骤：
    1. 剧本解析
    2. 角色创建
    3. 分镜生成
    4. 口型同步
    5. 音效匹配
    6. 视频渲染
    """
    try:
        orchestrator = WorkflowOrchestrator()
        storage = StorageService()
        
        # 下载角色图像
        character_images = []
        for url in request.character_image_urls:
            image_data = storage.download_file(url)
            character_images.append(image_data)
        
        # 下载音频（如果提供）
        audio_data = None
        if request.audio_url:
            audio_data = storage.download_file(request.audio_url)
        
        # 创建工作流
        workflow = orchestrator.create_workflow(
            user_id=str(current_user.id),
            script=request.script,
            character_images=character_images,
            audio_data=audio_data,
            config=request.config
        )
        
        return WorkflowResponse(**workflow.to_dict())
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建工作流失败: {str(e)}")


@router.post("/execute", response_model=WorkflowResultResponse)
async def execute_workflow(
    request: ExecuteWorkflowRequest,
    current_user: User = Depends(get_current_user)
):
    """
    执行工作流
    
    支持自动模式（一次执行所有步骤）和手动模式（逐步执行）
    """
    try:
        orchestrator = WorkflowOrchestrator()
        
        # 验证工作流所有权
        workflow = orchestrator.get_workflow(request.workflow_id)
        if not workflow:
            raise HTTPException(status_code=404, detail="工作流不存在")
        
        if workflow.user_id != str(current_user.id):
            raise HTTPException(status_code=403, detail="无权访问此工作流")
        
        # 执行工作流
        result = orchestrator.execute_workflow(
            workflow_id=request.workflow_id,
            auto_mode=request.auto_mode
        )
        
        return WorkflowResultResponse(**result.to_dict())
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"执行工作流失败: {str(e)}")


@router.post("/pause")
async def pause_workflow(
    request: PauseWorkflowRequest,
    current_user: User = Depends(get_current_user)
):
    """
    暂停工作流执行
    
    支持在任意环节暂停
    """
    try:
        orchestrator = WorkflowOrchestrator()
        
        # 验证工作流所有权
        workflow = orchestrator.get_workflow(request.workflow_id)
        if not workflow:
            raise HTTPException(status_code=404, detail="工作流不存在")
        
        if workflow.user_id != str(current_user.id):
            raise HTTPException(status_code=403, detail="无权访问此工作流")
        
        # 暂停工作流
        orchestrator.pause_workflow(request.workflow_id)
        
        return {"message": "工作流已暂停", "workflow_id": request.workflow_id}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"暂停工作流失败: {str(e)}")


@router.post("/resume", response_model=WorkflowResultResponse)
async def resume_workflow(
    request: ResumeWorkflowRequest,
    current_user: User = Depends(get_current_user)
):
    """
    恢复工作流执行
    
    从暂停点继续执行
    """
    try:
        orchestrator = WorkflowOrchestrator()
        
        # 验证工作流所有权
        workflow = orchestrator.get_workflow(request.workflow_id)
        if not workflow:
            raise HTTPException(status_code=404, detail="工作流不存在")
        
        if workflow.user_id != str(current_user.id):
            raise HTTPException(status_code=403, detail="无权访问此工作流")
        
        # 恢复工作流
        result = orchestrator.resume_workflow(request.workflow_id)
        
        return WorkflowResultResponse(**result.to_dict())
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"恢复工作流失败: {str(e)}")


@router.get("/progress/{workflow_id}", response_model=WorkflowProgressResponse)
async def get_workflow_progress(
    workflow_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    获取工作流进度
    
    返回当前步骤、完成百分比和预估剩余时间
    """
    try:
        orchestrator = WorkflowOrchestrator()
        
        # 验证工作流所有权
        workflow = orchestrator.get_workflow(workflow_id)
        if not workflow:
            raise HTTPException(status_code=404, detail="工作流不存在")
        
        if workflow.user_id != str(current_user.id):
            raise HTTPException(status_code=403, detail="无权访问此工作流")
        
        # 获取进度
        progress = orchestrator.get_workflow_progress(workflow_id)
        
        return WorkflowProgressResponse(**progress.to_dict())
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取进度失败: {str(e)}")


@router.get("/list", response_model=List[WorkflowResponse])
async def list_workflows(
    current_user: User = Depends(get_current_user)
):
    """
    列出用户的所有工作流
    """
    try:
        orchestrator = WorkflowOrchestrator()
        
        workflows = orchestrator.list_workflows(str(current_user.id))
        
        return [WorkflowResponse(**wf.to_dict()) for wf in workflows]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取工作流列表失败: {str(e)}")


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    获取工作流详情
    """
    try:
        orchestrator = WorkflowOrchestrator()
        
        workflow = orchestrator.get_workflow(workflow_id)
        if not workflow:
            raise HTTPException(status_code=404, detail="工作流不存在")
        
        if workflow.user_id != str(current_user.id):
            raise HTTPException(status_code=403, detail="无权访问此工作流")
        
        return WorkflowResponse(**workflow.to_dict())
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取工作流失败: {str(e)}")
