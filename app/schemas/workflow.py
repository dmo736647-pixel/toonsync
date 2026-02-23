"""
工作流数据模式
"""
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class CreateWorkflowRequest(BaseModel):
    """创建工作流请求"""
    script: str = Field(..., min_length=1, description="剧本文本")
    character_image_urls: List[str] = Field(..., min_items=1, description="角色图像URL列表")
    audio_url: Optional[str] = Field(None, description="音频URL（可选）")
    config: Optional[Dict[str, Any]] = Field(None, description="配置参数")


class WorkflowResponse(BaseModel):
    """工作流响应"""
    workflow_id: str
    user_id: str
    created_at: str
    updated_at: str
    status: str
    current_step: str
    config: Dict[str, Any]
    error_message: Optional[str]


class ExecuteWorkflowRequest(BaseModel):
    """执行工作流请求"""
    workflow_id: str = Field(..., description="工作流ID")
    auto_mode: bool = Field(default=True, description="是否自动执行所有步骤")


class WorkflowResultResponse(BaseModel):
    """工作流结果响应"""
    workflow_id: str
    status: str
    final_video_url: Optional[str]
    execution_time: float
    steps_completed: List[str]
    error_message: Optional[str]


class WorkflowProgressResponse(BaseModel):
    """工作流进度响应"""
    workflow_id: str
    current_step: str
    completed_steps: List[str]
    total_steps: int
    progress_percentage: float
    estimated_remaining_time: float
    status: str


class PauseWorkflowRequest(BaseModel):
    """暂停工作流请求"""
    workflow_id: str = Field(..., description="工作流ID")


class ResumeWorkflowRequest(BaseModel):
    """恢复工作流请求"""
    workflow_id: str = Field(..., description="工作流ID")
