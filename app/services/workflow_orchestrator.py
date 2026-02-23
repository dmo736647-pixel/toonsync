"""
完整工作流编排器

协调剧本解析→角色生成→分镜生成→口型同步→音效匹配→视频渲染的完整流程。
"""
import json
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

from app.services.sound_effect_matcher import SoundEffectMatcher
from app.services.character_consistency import CharacterConsistencyEngine
from app.services.lip_sync import ChineseLipSyncEngine
from app.services.video_rendering import VideoRenderingEngine, AspectRatio, VideoQuality


class WorkflowStatus(str, Enum):
    """工作流状态"""
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class WorkflowStep(str, Enum):
    """工作流步骤"""
    SCRIPT_PARSING = "script_parsing"  # 剧本解析
    CHARACTER_CREATION = "character_creation"  # 角色创建
    STORYBOARD_GENERATION = "storyboard_generation"  # 分镜生成
    LIP_SYNC = "lip_sync"  # 口型同步
    SOUND_EFFECTS = "sound_effects"  # 音效匹配
    VIDEO_RENDERING = "video_rendering"  # 视频渲染


@dataclass
class WorkflowProgress:
    """工作流进度"""
    workflow_id: str
    current_step: WorkflowStep
    completed_steps: List[WorkflowStep]
    total_steps: int
    progress_percentage: float
    estimated_remaining_time: float  # 分钟
    status: WorkflowStatus
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "workflow_id": self.workflow_id,
            "current_step": self.current_step.value,
            "completed_steps": [s.value for s in self.completed_steps],
            "total_steps": self.total_steps,
            "progress_percentage": self.progress_percentage,
            "estimated_remaining_time": self.estimated_remaining_time,
            "status": self.status.value
        }


@dataclass
class WorkflowData:
    """工作流数据"""
    script: str
    character_images: List[bytes] = field(default_factory=list)
    audio_data: Optional[bytes] = None
    
    # 中间结果
    parsed_scenes: List[Dict] = field(default_factory=list)
    character_models: List[Dict] = field(default_factory=list)
    storyboard_frames: List[bytes] = field(default_factory=list)
    lip_sync_results: List[Dict] = field(default_factory=list)
    sound_effect_placements: List[Dict] = field(default_factory=list)
    final_video_url: Optional[str] = None


@dataclass
class Workflow:
    """工作流"""
    workflow_id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    status: WorkflowStatus
    current_step: WorkflowStep
    data: WorkflowData
    config: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "workflow_id": self.workflow_id,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "status": self.status.value,
            "current_step": self.current_step.value,
            "config": self.config,
            "error_message": self.error_message
        }


@dataclass
class WorkflowResult:
    """工作流执行结果"""
    workflow_id: str
    status: WorkflowStatus
    final_video_url: Optional[str]
    execution_time: float  # 秒
    steps_completed: List[WorkflowStep]
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "workflow_id": self.workflow_id,
            "status": self.status.value,
            "final_video_url": self.final_video_url,
            "execution_time": self.execution_time,
            "steps_completed": [s.value for s in self.steps_completed],
            "error_message": self.error_message
        }


class WorkflowOrchestrator:
    """
    完整工作流编排器
    
    核心功能：
    1. 创建和管理工作流
    2. 执行完整流程（剧本→角色→分镜→口型→音效→视频）
    3. 支持暂停和继续
    4. 进度追踪
    """
    
    _instance = None
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """初始化工作流编排器"""
        if self._initialized:
            return
        
        # 初始化各个引擎
        self.sound_matcher = SoundEffectMatcher()
        self.character_engine = CharacterConsistencyEngine()
        self.lip_sync_engine = ChineseLipSyncEngine()
        self.video_engine = VideoRenderingEngine()
        
        # 工作流存储（实际应使用数据库）
        self.workflows: Dict[str, Workflow] = {}
        
        self._initialized = True
    
    def create_workflow(
        self,
        user_id: str,
        script: str,
        character_images: List[bytes],
        audio_data: Optional[bytes] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> Workflow:
        """
        创建完整工作流
        
        参数:
            user_id: 用户ID
            script: 剧本文本
            character_images: 角色参考图像列表
            audio_data: 音频数据（可选）
            config: 配置参数
        
        返回:
            Workflow: 工作流对象
        """
        # 生成工作流ID
        workflow_id = f"wf_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # 创建工作流数据
        data = WorkflowData(
            script=script,
            character_images=character_images,
            audio_data=audio_data
        )
        
        # 创建工作流
        workflow = Workflow(
            workflow_id=workflow_id,
            user_id=user_id,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            status=WorkflowStatus.CREATED,
            current_step=WorkflowStep.SCRIPT_PARSING,
            data=data,
            config=config or {}
        )
        
        # 存储工作流
        self.workflows[workflow_id] = workflow
        
        return workflow
    
    def execute_workflow(
        self,
        workflow_id: str,
        auto_mode: bool = True
    ) -> WorkflowResult:
        """
        执行工作流
        
        参数:
            workflow_id: 工作流ID
            auto_mode: 是否自动执行所有步骤
        
        返回:
            WorkflowResult: 工作流执行结果
        """
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"工作流不存在: {workflow_id}")
        
        start_time = datetime.now()
        workflow.status = WorkflowStatus.RUNNING
        workflow.updated_at = datetime.now()
        
        steps_completed = []
        
        try:
            # 步骤1: 剧本解析
            if workflow.current_step == WorkflowStep.SCRIPT_PARSING:
                self._execute_script_parsing(workflow)
                steps_completed.append(WorkflowStep.SCRIPT_PARSING)
                workflow.current_step = WorkflowStep.CHARACTER_CREATION
                
                if not auto_mode:
                    workflow.status = WorkflowStatus.PAUSED
                    return self._create_result(workflow, start_time, steps_completed)
            
            # 步骤2: 角色创建
            if workflow.current_step == WorkflowStep.CHARACTER_CREATION:
                self._execute_character_creation(workflow)
                steps_completed.append(WorkflowStep.CHARACTER_CREATION)
                workflow.current_step = WorkflowStep.STORYBOARD_GENERATION
                
                if not auto_mode:
                    workflow.status = WorkflowStatus.PAUSED
                    return self._create_result(workflow, start_time, steps_completed)
            
            # 步骤3: 分镜生成
            if workflow.current_step == WorkflowStep.STORYBOARD_GENERATION:
                self._execute_storyboard_generation(workflow)
                steps_completed.append(WorkflowStep.STORYBOARD_GENERATION)
                workflow.current_step = WorkflowStep.LIP_SYNC
                
                if not auto_mode:
                    workflow.status = WorkflowStatus.PAUSED
                    return self._create_result(workflow, start_time, steps_completed)
            
            # 步骤4: 口型同步
            if workflow.current_step == WorkflowStep.LIP_SYNC:
                self._execute_lip_sync(workflow)
                steps_completed.append(WorkflowStep.LIP_SYNC)
                workflow.current_step = WorkflowStep.SOUND_EFFECTS
                
                if not auto_mode:
                    workflow.status = WorkflowStatus.PAUSED
                    return self._create_result(workflow, start_time, steps_completed)
            
            # 步骤5: 音效匹配
            if workflow.current_step == WorkflowStep.SOUND_EFFECTS:
                self._execute_sound_effects(workflow)
                steps_completed.append(WorkflowStep.SOUND_EFFECTS)
                workflow.current_step = WorkflowStep.VIDEO_RENDERING
                
                if not auto_mode:
                    workflow.status = WorkflowStatus.PAUSED
                    return self._create_result(workflow, start_time, steps_completed)
            
            # 步骤6: 视频渲染
            if workflow.current_step == WorkflowStep.VIDEO_RENDERING:
                self._execute_video_rendering(workflow)
                steps_completed.append(WorkflowStep.VIDEO_RENDERING)
                workflow.status = WorkflowStatus.COMPLETED
            
            return self._create_result(workflow, start_time, steps_completed)
        
        except Exception as e:
            workflow.status = WorkflowStatus.FAILED
            workflow.error_message = str(e)
            workflow.updated_at = datetime.now()
            
            return WorkflowResult(
                workflow_id=workflow_id,
                status=WorkflowStatus.FAILED,
                final_video_url=None,
                execution_time=(datetime.now() - start_time).total_seconds(),
                steps_completed=steps_completed,
                error_message=str(e)
            )
    
    def _execute_script_parsing(self, workflow: Workflow):
        """执行剧本解析"""
        segments = self.sound_matcher.parse_script(workflow.data.script)
        workflow.data.parsed_scenes = [seg.to_dict() for seg in segments]
        workflow.updated_at = datetime.now()
    
    def _execute_character_creation(self, workflow: Workflow):
        """执行角色创建"""
        character_models = []
        
        for i, image_data in enumerate(workflow.data.character_images):
            model = self.character_engine.extract_character_features(image_data)
            character_models.append({
                "character_id": f"char_{i+1}",
                "model_data": model.to_dict()
            })
        
        workflow.data.character_models = character_models
        workflow.updated_at = datetime.now()
    
    def _execute_storyboard_generation(self, workflow: Workflow):
        """执行分镜生成"""
        import requests
        import os
        
        storyboard_frames = []
        
        # 为每个场景生成分镜
        for scene in workflow.data.parsed_scenes[:5]:  # 限制前5个场景
            if workflow.data.character_models:
                # 使用第一个角色模型
                model_data = workflow.data.character_models[0]["model_data"]
                from app.services.character_consistency import ConsistencyModel
                model = ConsistencyModel.from_dict(model_data)
                
                # 生成分镜
                frame_result = self.character_engine.generate_storyboard(
                    model,
                    scene["text"][:100],  # 限制描述长度
                    style="anime"
                )
                
                # 处理生成结果（URL或本地路径）转为bytes
                frame_bytes = None
                if frame_result.startswith("http"):
                    try:
                        resp = requests.get(frame_result)
                        if resp.status_code == 200:
                            frame_bytes = resp.content
                    except Exception as e:
                        print(f"Failed to download frame from {frame_result}: {e}")
                else:
                    # Assume local path
                    if os.path.exists(frame_result):
                        with open(frame_result, "rb") as f:
                            frame_bytes = f.read()
                
                if frame_bytes:
                    storyboard_frames.append(frame_bytes)
        
        workflow.data.storyboard_frames = storyboard_frames
        workflow.updated_at = datetime.now()
    
    def _execute_lip_sync(self, workflow: Workflow):
        """执行口型同步"""
        lip_sync_results = []
        
        if workflow.data.audio_data:
            # 分析音频
            analysis = self.lip_sync_engine.analyze_audio(workflow.data.audio_data)
            
            # 为每个分镜生成口型
            for i, frame in enumerate(workflow.data.storyboard_frames[:3]):  # 限制前3个
                keyframes = self.lip_sync_engine.generate_lip_sync_keyframes(
                    analysis,
                    frame,
                    style="anime"
                )
                
                lip_sync_results.append({
                    "frame_index": i,
                    "keyframe_count": len(keyframes),
                    "duration": analysis.duration
                })
        
        workflow.data.lip_sync_results = lip_sync_results
        workflow.updated_at = datetime.now()
    
    def _execute_sound_effects(self, workflow: Workflow):
        """执行音效匹配"""
        # 为每个场景推荐音效
        placements = []
        
        for scene_dict in workflow.data.parsed_scenes[:5]:  # 限制前5个
            from app.services.sound_effect_matcher import SceneSegment
            scene = SceneSegment.from_dict(scene_dict)
            
            # 推荐音效
            recommendations = self.sound_matcher.recommend_sound_effects(scene, top_k=1)
            
            if recommendations:
                effect, score = recommendations[0]
                placements.append({
                    "scene_id": scene.scene_id,
                    "effect_id": effect.effect_id,
                    "effect_name": effect.name,
                    "score": score
                })
        
        workflow.data.sound_effect_placements = placements
        workflow.updated_at = datetime.now()
    
    def _execute_video_rendering(self, workflow: Workflow):
        """执行视频渲染"""
        # 获取配置
        aspect_ratio = workflow.config.get("aspect_ratio", "9:16")
        quality = workflow.config.get("quality", "1080p")
        
        # 创建视频配置
        config = self.video_engine.create_project_config(
            aspect_ratio=AspectRatio(aspect_ratio),
            duration_minutes=2.0,
            quality=VideoQuality(quality)
        )
        
        # 渲染视频
        if workflow.data.storyboard_frames:
            video_url = self.video_engine.render_video(
                frames=workflow.data.storyboard_frames,
                config=config
            )
            workflow.data.final_video_url = video_url
        
        workflow.updated_at = datetime.now()
    
    def _create_result(
        self,
        workflow: Workflow,
        start_time: datetime,
        steps_completed: List[WorkflowStep]
    ) -> WorkflowResult:
        """创建工作流结果"""
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return WorkflowResult(
            workflow_id=workflow.workflow_id,
            status=workflow.status,
            final_video_url=workflow.data.final_video_url,
            execution_time=execution_time,
            steps_completed=steps_completed,
            error_message=workflow.error_message
        )
    
    def pause_workflow(self, workflow_id: str):
        """
        暂停工作流执行
        
        参数:
            workflow_id: 工作流ID
        """
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"工作流不存在: {workflow_id}")
        
        if workflow.status == WorkflowStatus.RUNNING:
            workflow.status = WorkflowStatus.PAUSED
            workflow.updated_at = datetime.now()
    
    def resume_workflow(self, workflow_id: str) -> WorkflowResult:
        """
        恢复工作流执行
        
        参数:
            workflow_id: 工作流ID
        
        返回:
            WorkflowResult: 工作流执行结果
        """
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"工作流不存在: {workflow_id}")
        
        if workflow.status != WorkflowStatus.PAUSED:
            raise ValueError(f"工作流状态不是暂停: {workflow.status}")
        
        # 继续执行
        return self.execute_workflow(workflow_id, auto_mode=True)
    
    def get_workflow_progress(self, workflow_id: str) -> WorkflowProgress:
        """
        获取工作流进度
        
        参数:
            workflow_id: 工作流ID
        
        返回:
            WorkflowProgress: 工作流进度
        """
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"工作流不存在: {workflow_id}")
        
        # 定义步骤顺序
        all_steps = [
            WorkflowStep.SCRIPT_PARSING,
            WorkflowStep.CHARACTER_CREATION,
            WorkflowStep.STORYBOARD_GENERATION,
            WorkflowStep.LIP_SYNC,
            WorkflowStep.SOUND_EFFECTS,
            WorkflowStep.VIDEO_RENDERING
        ]
        
        # 计算已完成的步骤
        current_index = all_steps.index(workflow.current_step)
        completed_steps = all_steps[:current_index]
        
        # 计算进度百分比
        if workflow.status == WorkflowStatus.COMPLETED:
            progress_percentage = 100.0
        else:
            progress_percentage = (current_index / len(all_steps)) * 100
        
        # 估算剩余时间（简化：每步骤1分钟）
        remaining_steps = len(all_steps) - current_index
        estimated_remaining_time = remaining_steps * 1.0
        
        return WorkflowProgress(
            workflow_id=workflow_id,
            current_step=workflow.current_step,
            completed_steps=completed_steps,
            total_steps=len(all_steps),
            progress_percentage=progress_percentage,
            estimated_remaining_time=estimated_remaining_time,
            status=workflow.status
        )
    
    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """获取工作流"""
        return self.workflows.get(workflow_id)
    
    def list_workflows(self, user_id: str) -> List[Workflow]:
        """列出用户的所有工作流"""
        return [
            wf for wf in self.workflows.values()
            if wf.user_id == user_id
        ]
