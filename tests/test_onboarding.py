"""新手引导服务测试"""
import pytest

from app.services.onboarding import (
    OnboardingStep,
    TutorialStep,
    OnboardingService
)


class TestTutorialStep:
    """教程步骤测试"""
    
    def test_create_tutorial_step(self):
        """测试创建教程步骤"""
        step = TutorialStep(
            "welcome",
            "欢迎",
            "欢迎使用",
            ["步骤1", "步骤2"],
            ["提示1"],
            "/video.mp4",
            5
        )
        
        assert step.step_id == "welcome"
        assert step.title == "欢迎"
        assert step.description == "欢迎使用"
        assert len(step.instructions) == 2
        assert len(step.tips) == 1
        assert step.video_url == "/video.mp4"
        assert step.estimated_time == 5
    
    def test_tutorial_step_to_dict(self):
        """测试教程步骤转换为字典"""
        step = TutorialStep(
            "welcome",
            "欢迎",
            "欢迎使用",
            ["步骤1"],
            ["提示1"],
            "/video.mp4",
            5
        )
        
        data = step.to_dict()
        
        assert data["step_id"] == "welcome"
        assert data["title"] == "欢迎"
        assert "instructions" in data
        assert "tips" in data
        assert "video_url" in data
        assert "estimated_time" in data


class TestOnboardingService:
    """新手引导服务测试"""
    
    def test_get_tutorial_step(self):
        """测试获取教程步骤"""
        step = OnboardingService.get_tutorial_step(OnboardingStep.WELCOME)
        
        assert step.step_id == "welcome"
        assert step.title is not None
        assert len(step.instructions) > 0
    
    def test_get_all_steps(self):
        """测试获取所有步骤"""
        steps = OnboardingService.get_all_steps()
        
        assert len(steps) == len(OnboardingStep)
        assert steps[0]["order"] == 1
        assert "step" in steps[0]
        assert "title" in steps[0]
    
    def test_get_next_step(self):
        """测试获取下一步"""
        next_step = OnboardingService.get_next_step(OnboardingStep.WELCOME)
        
        assert next_step == OnboardingStep.CREATE_PROJECT
    
    def test_get_next_step_at_end(self):
        """测试在最后一步获取下一步"""
        next_step = OnboardingService.get_next_step(OnboardingStep.COMPLETED)
        
        assert next_step is None
    
    def test_get_previous_step(self):
        """测试获取上一步"""
        prev_step = OnboardingService.get_previous_step(OnboardingStep.CREATE_PROJECT)
        
        assert prev_step == OnboardingStep.WELCOME
    
    def test_get_previous_step_at_start(self):
        """测试在第一步获取上一步"""
        prev_step = OnboardingService.get_previous_step(OnboardingStep.WELCOME)
        
        assert prev_step is None
    
    def test_get_progress_empty(self):
        """测试获取空进度"""
        progress = OnboardingService.get_progress([])
        
        assert progress["completed_steps"] == 0
        assert progress["percentage"] == 0
        assert not progress["is_completed"]
    
    def test_get_progress_partial(self):
        """测试获取部分进度"""
        completed = ["welcome", "create_project"]
        progress = OnboardingService.get_progress(completed)
        
        assert progress["completed_steps"] == 2
        assert progress["percentage"] > 0
        assert not progress["is_completed"]
    
    def test_get_progress_completed(self):
        """测试获取完成进度"""
        completed = [step.value for step in OnboardingStep if step != OnboardingStep.COMPLETED]
        progress = OnboardingService.get_progress(completed)
        
        assert progress["is_completed"]
        assert progress["percentage"] == 100
    
    def test_get_quick_start_guide(self):
        """测试获取快速入门指南"""
        guide = OnboardingService.get_quick_start_guide()
        
        assert "title" in guide
        assert "description" in guide
        assert "steps" in guide
        assert len(guide["steps"]) > 0
        assert "total_time" in guide
    
    def test_get_feature_highlights(self):
        """测试获取功能亮点"""
        features = OnboardingService.get_feature_highlights()
        
        assert len(features) > 0
        assert "title" in features[0]
        assert "description" in features[0]
        assert "icon" in features[0]
        assert "learn_more" in features[0]
    
    def test_all_steps_have_required_fields(self):
        """测试所有步骤都有必需字段"""
        for step_enum in OnboardingStep:
            step = OnboardingService.get_tutorial_step(step_enum)
            
            assert step.step_id is not None
            assert step.title is not None
            assert step.description is not None
            assert len(step.instructions) > 0
    
    def test_step_order_is_correct(self):
        """测试步骤顺序正确"""
        steps = list(OnboardingStep)
        
        assert steps[0] == OnboardingStep.WELCOME
        assert steps[-1] == OnboardingStep.COMPLETED
    
    def test_estimated_times_are_reasonable(self):
        """测试预计时间合理"""
        for step_enum in OnboardingStep:
            step = OnboardingService.get_tutorial_step(step_enum)
            
            if step.estimated_time is not None:
                assert step.estimated_time >= 0
                assert step.estimated_time <= 30  # 单个步骤不应超过30分钟
    
    def test_video_urls_are_provided_for_key_steps(self):
        """测试关键步骤提供视频"""
        key_steps = [
            OnboardingStep.WELCOME,
            OnboardingStep.UPLOAD_CHARACTER,
            OnboardingStep.CREATE_STORYBOARD,
            OnboardingStep.LIP_SYNC,
            OnboardingStep.EXPORT_VIDEO
        ]
        
        for step_enum in key_steps:
            step = OnboardingService.get_tutorial_step(step_enum)
            assert step.video_url is not None
    
    def test_tips_are_provided(self):
        """测试提供提示"""
        for step_enum in OnboardingStep:
            step = OnboardingService.get_tutorial_step(step_enum)
            
            # 大多数步骤应该有提示
            if step_enum != OnboardingStep.COMPLETED:
                assert len(step.tips) > 0
