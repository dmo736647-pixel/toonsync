"""新手引导服务"""
from typing import Dict, List, Optional
from enum import Enum


class OnboardingStep(Enum):
    """引导步骤"""
    WELCOME = "welcome"
    CREATE_PROJECT = "create_project"
    UPLOAD_CHARACTER = "upload_character"
    CREATE_STORYBOARD = "create_storyboard"
    ADD_AUDIO = "add_audio"
    LIP_SYNC = "lip_sync"
    ADD_SOUND_EFFECTS = "add_sound_effects"
    EXPORT_VIDEO = "export_video"
    COMPLETED = "completed"


class TutorialStep:
    """教程步骤"""
    
    def __init__(
        self,
        step_id: str,
        title: str,
        description: str,
        instructions: List[str],
        tips: Optional[List[str]] = None,
        video_url: Optional[str] = None,
        estimated_time: Optional[int] = None
    ):
        self.step_id = step_id
        self.title = title
        self.description = description
        self.instructions = instructions
        self.tips = tips or []
        self.video_url = video_url
        self.estimated_time = estimated_time  # 预计完成时间（分钟）
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        result = {
            "step_id": self.step_id,
            "title": self.title,
            "description": self.description,
            "instructions": self.instructions
        }
        
        if self.tips:
            result["tips"] = self.tips
        if self.video_url:
            result["video_url"] = self.video_url
        if self.estimated_time:
            result["estimated_time"] = self.estimated_time
        
        return result


class OnboardingService:
    """新手引导服务"""
    
    # 定义完整的引导流程
    TUTORIAL_STEPS: Dict[OnboardingStep, TutorialStep] = {
        OnboardingStep.WELCOME: TutorialStep(
            step_id="welcome",
            title="欢迎使用短剧生产力工具",
            description="让我们开始创作您的第一个微短剧！",
            instructions=[
                "本工具专为中文微短剧优化",
                "支持动态漫和真人短剧两种风格",
                "提供完整的创作工作流：剧本 → 角色 → 分镜 → 口型同步 → 音效 → 导出"
            ],
            tips=[
                "建议先观看快速入门视频",
                "可以随时暂停引导，稍后继续"
            ],
            video_url="/tutorials/welcome.mp4",
            estimated_time=2
        ),
        
        OnboardingStep.CREATE_PROJECT: TutorialStep(
            step_id="create_project",
            title="创建您的第一个项目",
            description="项目是您创作的工作空间",
            instructions=[
                "点击「新建项目」按钮",
                "输入项目名称（例如：我的第一个短剧）",
                "选择视频比例（推荐9:16竖屏）",
                "点击「创建」完成"
            ],
            tips=[
                "项目名称可以随时修改",
                "竖屏格式最适合抖音、快手等平台"
            ],
            estimated_time=1
        ),
        
        OnboardingStep.UPLOAD_CHARACTER: TutorialStep(
            step_id="upload_character",
            title="上传角色图像",
            description="上传一张角色图片，系统会自动生成一致性模型",
            instructions=[
                "进入「角色管理」页面",
                "点击「上传角色」",
                "选择一张清晰的角色正面照",
                "输入角色名称",
                "等待系统提取特征（约2秒）"
            ],
            tips=[
                "建议使用高清图片（至少512x512）",
                "正面照效果最好",
                "系统会自动保持角色在不同分镜中的一致性"
            ],
            video_url="/tutorials/upload_character.mp4",
            estimated_time=3
        ),
        
        OnboardingStep.CREATE_STORYBOARD: TutorialStep(
            step_id="create_storyboard",
            title="创建分镜",
            description="使用角色一致性引擎生成分镜图像",
            instructions=[
                "进入「分镜编辑」页面",
                "点击「添加分镜」",
                "选择角色",
                "输入场景描述（例如：角色在公园里微笑）",
                "点击「生成」，等待AI生成图像"
            ],
            tips=[
                "场景描述越详细，生成效果越好",
                "可以生成多个分镜组成完整故事",
                "支持调整角色姿态和表情"
            ],
            video_url="/tutorials/create_storyboard.mp4",
            estimated_time=5
        ),
        
        OnboardingStep.ADD_AUDIO: TutorialStep(
            step_id="add_audio",
            title="添加音频对白",
            description="上传或录制角色的对白音频",
            instructions=[
                "选择一个分镜",
                "点击「添加音频」",
                "上传音频文件或使用在线录音",
                "系统会自动识别中文音素"
            ],
            tips=[
                "支持中文普通话、英语等多种语言",
                "音频质量越好，口型同步效果越好",
                "建议使用清晰的录音环境"
            ],
            estimated_time=3
        ),
        
        OnboardingStep.LIP_SYNC: TutorialStep(
            step_id="lip_sync",
            title="生成口型同步",
            description="让角色的口型与音频精确同步",
            instructions=[
                "选择已添加音频的分镜",
                "点击「生成口型同步」",
                "等待AI处理（处理时间约为音频时长的1.5倍）",
                "预览效果，确认口型同步精度"
            ],
            tips=[
                "系统针对中文普通话优化，时间误差<50ms",
                "支持动态漫和真人两种风格",
                "可以调整口型强度"
            ],
            video_url="/tutorials/lip_sync.mp4",
            estimated_time=5
        ),
        
        OnboardingStep.ADD_SOUND_EFFECTS: TutorialStep(
            step_id="add_sound_effects",
            title="添加音效",
            description="使用智能音效匹配器为场景添加音效",
            instructions=[
                "进入「音效」页面",
                "系统会根据场景自动推荐音效",
                "试听并选择合适的音效",
                "点击「应用」将音效添加到时间轴"
            ],
            tips=[
                "音效库包含1000+专业音效",
                "可以上传自定义音效",
                "支持调整音效音量和时长"
            ],
            estimated_time=3
        ),
        
        OnboardingStep.EXPORT_VIDEO: TutorialStep(
            step_id="export_video",
            title="导出视频",
            description="将项目导出为最终视频文件",
            instructions=[
                "点击「导出」按钮",
                "选择分辨率（720p/1080p/4K）",
                "选择格式（MP4/MOV）",
                "查看预估费用和渲染时间",
                "确认后开始导出"
            ],
            tips=[
                "1-3分钟视频渲染时间约5分钟",
                "可以在导出前预览效果",
                "导出完成后会收到通知"
            ],
            video_url="/tutorials/export_video.mp4",
            estimated_time=10
        ),
        
        OnboardingStep.COMPLETED: TutorialStep(
            step_id="completed",
            title="恭喜完成！",
            description="您已掌握基本工作流程",
            instructions=[
                "您现在可以开始创作自己的微短剧了",
                "探索更多高级功能",
                "查看帮助文档了解详细信息"
            ],
            tips=[
                "可以保存项目为模板，方便复用",
                "加入社区与其他创作者交流",
                "关注我们的教程获取更多技巧"
            ],
            estimated_time=0
        )
    }
    
    @classmethod
    def get_tutorial_step(cls, step: OnboardingStep) -> TutorialStep:
        """获取教程步骤"""
        return cls.TUTORIAL_STEPS[step]
    
    @classmethod
    def get_all_steps(cls) -> List[Dict]:
        """获取所有教程步骤"""
        return [
            {
                "order": i,
                "step": step.value,
                **cls.TUTORIAL_STEPS[step].to_dict()
            }
            for i, step in enumerate(OnboardingStep, 1)
        ]
    
    @classmethod
    def get_next_step(cls, current_step: OnboardingStep) -> Optional[OnboardingStep]:
        """获取下一步"""
        steps = list(OnboardingStep)
        try:
            current_index = steps.index(current_step)
            if current_index < len(steps) - 1:
                return steps[current_index + 1]
        except ValueError:
            pass
        return None
    
    @classmethod
    def get_previous_step(cls, current_step: OnboardingStep) -> Optional[OnboardingStep]:
        """获取上一步"""
        steps = list(OnboardingStep)
        try:
            current_index = steps.index(current_step)
            if current_index > 0:
                return steps[current_index - 1]
        except ValueError:
            pass
        return None
    
    @classmethod
    def get_progress(cls, completed_steps: List[str]) -> Dict:
        """获取引导进度"""
        total_steps = len(OnboardingStep) - 1  # 不包括COMPLETED
        completed_count = len([s for s in completed_steps if s != OnboardingStep.COMPLETED.value])
        
        return {
            "total_steps": total_steps,
            "completed_steps": completed_count,
            "percentage": (completed_count / total_steps * 100) if total_steps > 0 else 0,
            "is_completed": completed_count >= total_steps
        }
    
    @classmethod
    def get_quick_start_guide(cls) -> Dict:
        """获取快速入门指南"""
        return {
            "title": "快速入门指南",
            "description": "5分钟了解核心工作流",
            "steps": [
                {
                    "title": "创建项目",
                    "description": "新建一个竖屏项目",
                    "time": "1分钟"
                },
                {
                    "title": "上传角色",
                    "description": "上传角色图片，生成一致性模型",
                    "time": "3分钟"
                },
                {
                    "title": "生成分镜",
                    "description": "使用AI生成分镜图像",
                    "time": "5分钟"
                },
                {
                    "title": "口型同步",
                    "description": "添加音频并生成口型动画",
                    "time": "5分钟"
                },
                {
                    "title": "导出视频",
                    "description": "渲染并导出最终视频",
                    "time": "5-10分钟"
                }
            ],
            "total_time": "约20分钟",
            "video_url": "/tutorials/quick_start.mp4"
        }
    
    @classmethod
    def get_feature_highlights(cls) -> List[Dict]:
        """获取功能亮点"""
        return [
            {
                "title": "中文口型同步",
                "description": "针对中文普通话优化，时间误差<50ms",
                "icon": "🎤",
                "learn_more": "/docs/lip-sync"
            },
            {
                "title": "角色一致性",
                "description": "一张图生成全套分镜，保持视觉统一",
                "icon": "👤",
                "learn_more": "/docs/character-consistency"
            },
            {
                "title": "竖屏优化",
                "description": "专为抖音、快手等平台优化",
                "icon": "📱",
                "learn_more": "/docs/vertical-video"
            },
            {
                "title": "智能音效",
                "description": "AI自动推荐匹配的音效",
                "icon": "🔊",
                "learn_more": "/docs/sound-effects"
            },
            {
                "title": "完整工作流",
                "description": "从剧本到成片，一站式完成",
                "icon": "⚡",
                "learn_more": "/docs/workflow"
            }
        ]


# 全局新手引导服务实例
onboarding_service = OnboardingService()
