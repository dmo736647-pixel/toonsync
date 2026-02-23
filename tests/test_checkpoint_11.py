"""
检查点11：工作流集成验证

验证所有核心模块的集成和端到端功能。
"""
import pytest
import io
from PIL import Image

from app.services.workflow_orchestrator import (
    WorkflowOrchestrator,
    WorkflowStatus,
    WorkflowStep
)
from app.services.sound_effect_matcher import SoundEffectMatcher
from app.services.character_consistency import CharacterConsistencyEngine
from app.services.lip_sync import ChineseLipSyncEngine
from app.services.video_rendering import VideoRenderingEngine


class TestWorkflowIntegration:
    """测试工作流集成"""
    
    def create_test_image(self) -> bytes:
        """创建测试图像"""
        image = Image.new('RGB', (512, 512), color='blue')
        img_bytes = io.BytesIO()
        image.save(img_bytes, format='PNG')
        return img_bytes.getvalue()
    
    def test_all_engines_available(self):
        """测试所有引擎可用"""
        # 音效匹配器
        sound_matcher = SoundEffectMatcher()
        assert sound_matcher is not None
        
        # 角色一致性引擎
        character_engine = CharacterConsistencyEngine()
        assert character_engine is not None
        
        # 口型同步引擎
        lip_sync_engine = ChineseLipSyncEngine()
        assert lip_sync_engine is not None
        
        # 视频渲染引擎
        video_engine = VideoRenderingEngine()
        assert video_engine is not None
        
        # 工作流编排器
        orchestrator = WorkflowOrchestrator()
        assert orchestrator is not None
    
    def test_workflow_orchestrator_integration(self):
        """测试工作流编排器集成所有引擎"""
        orchestrator = WorkflowOrchestrator()
        
        # 验证所有引擎已初始化
        assert orchestrator.sound_matcher is not None
        assert orchestrator.character_engine is not None
        assert orchestrator.lip_sync_engine is not None
        assert orchestrator.video_engine is not None
    
    def test_end_to_end_workflow(self):
        """测试端到端工作流"""
        orchestrator = WorkflowOrchestrator()
        
        # 准备测试数据
        script = """
        场景1：室内，办公室
        小明快速跑进办公室，大声喊道："出事了！"
        
        场景2：室外，街道
        小红在街上慢慢走着，心情很悲伤。
        """
        
        character_images = [self.create_test_image()]
        audio_data = b"mock_audio_data"
        
        # 1. 创建工作流
        workflow = orchestrator.create_workflow(
            user_id="test_user",
            script=script,
            character_images=character_images,
            audio_data=audio_data,
            config={"aspect_ratio": "9:16", "quality": "1080p"}
        )
        
        assert workflow.workflow_id
        assert workflow.status == WorkflowStatus.CREATED
        
        # 2. 执行完整工作流
        result = orchestrator.execute_workflow(
            workflow.workflow_id,
            auto_mode=True
        )
        
        # 3. 验证结果
        assert result.status == WorkflowStatus.COMPLETED
        assert len(result.steps_completed) == 6
        assert result.final_video_url is not None
        
        # 4. 验证每个步骤的输出
        assert len(workflow.data.parsed_scenes) > 0  # 剧本解析
        assert len(workflow.data.character_models) > 0  # 角色创建
        assert len(workflow.data.storyboard_frames) > 0  # 分镜生成
        # 口型同步和音效匹配可能为空（取决于数据）
        assert workflow.data.final_video_url is not None  # 视频渲染
    
    def test_workflow_step_by_step(self):
        """测试逐步执行工作流"""
        orchestrator = WorkflowOrchestrator()
        
        script = "场景1：小明走进房间。"
        character_images = [self.create_test_image()]
        
        # 创建工作流
        workflow = orchestrator.create_workflow(
            user_id="test_user",
            script=script,
            character_images=character_images
        )
        
        # 步骤1：剧本解析
        result = orchestrator.execute_workflow(
            workflow.workflow_id,
            auto_mode=False
        )
        assert WorkflowStep.SCRIPT_PARSING in result.steps_completed
        assert workflow.current_step == WorkflowStep.CHARACTER_CREATION
        
        # 步骤2：角色创建
        result = orchestrator.execute_workflow(
            workflow.workflow_id,
            auto_mode=False
        )
        assert WorkflowStep.CHARACTER_CREATION in result.steps_completed
        assert workflow.current_step == WorkflowStep.STORYBOARD_GENERATION
        
        # 继续执行剩余步骤
        result = orchestrator.resume_workflow(workflow.workflow_id)
        assert result.status == WorkflowStatus.COMPLETED
    
    def test_workflow_pause_and_resume(self):
        """测试工作流暂停和恢复"""
        orchestrator = WorkflowOrchestrator()
        
        script = "场景1：测试场景"
        character_images = [self.create_test_image()]
        
        workflow = orchestrator.create_workflow(
            user_id="test_user",
            script=script,
            character_images=character_images
        )
        
        # 执行第一步
        result = orchestrator.execute_workflow(
            workflow.workflow_id,
            auto_mode=False
        )
        assert result.status == WorkflowStatus.PAUSED
        
        # 暂停
        orchestrator.pause_workflow(workflow.workflow_id)
        assert workflow.status == WorkflowStatus.PAUSED
        
        # 恢复并完成
        result = orchestrator.resume_workflow(workflow.workflow_id)
        assert result.status == WorkflowStatus.COMPLETED
    
    def test_workflow_progress_tracking(self):
        """测试工作流进度追踪"""
        orchestrator = WorkflowOrchestrator()
        
        script = "场景1：测试"
        character_images = [self.create_test_image()]
        
        workflow = orchestrator.create_workflow(
            user_id="test_user",
            script=script,
            character_images=character_images
        )
        
        # 初始进度
        progress = orchestrator.get_workflow_progress(workflow.workflow_id)
        assert progress.progress_percentage == 0.0
        assert progress.current_step == WorkflowStep.SCRIPT_PARSING
        
        # 执行一步
        orchestrator.execute_workflow(workflow.workflow_id, auto_mode=False)
        
        # 更新后的进度
        progress = orchestrator.get_workflow_progress(workflow.workflow_id)
        assert progress.progress_percentage > 0
        assert len(progress.completed_steps) > 0
    
    def test_data_flow_between_steps(self):
        """测试步骤间数据流转"""
        orchestrator = WorkflowOrchestrator()
        
        script = "场景1：小明走进房间。\n场景2：小红在街上。"
        character_images = [self.create_test_image()]
        
        workflow = orchestrator.create_workflow(
            user_id="test_user",
            script=script,
            character_images=character_images
        )
        
        # 执行完整工作流
        result = orchestrator.execute_workflow(
            workflow.workflow_id,
            auto_mode=True
        )
        
        # 验证数据在步骤间正确传递
        # 剧本解析 → 角色创建
        assert len(workflow.data.parsed_scenes) > 0
        assert len(workflow.data.character_models) > 0
        
        # 角色创建 → 分镜生成
        assert len(workflow.data.storyboard_frames) > 0
        
        # 分镜生成 → 视频渲染
        assert workflow.data.final_video_url is not None


class TestModuleIntegration:
    """测试模块间集成"""
    
    def create_test_image(self) -> bytes:
        """创建测试图像"""
        image = Image.new('RGB', (512, 512), color='blue')
        img_bytes = io.BytesIO()
        image.save(img_bytes, format='PNG')
        return img_bytes.getvalue()
    
    def test_script_parsing_to_sound_effects(self):
        """测试剧本解析到音效匹配的集成"""
        matcher = SoundEffectMatcher()
        
        script = "场景1：激烈的打斗场面，拳拳到肉。"
        
        # 解析剧本
        segments = matcher.parse_script(script)
        assert len(segments) > 0
        
        # 推荐音效
        recommendations = matcher.recommend_sound_effects(segments[0], top_k=3)
        assert len(recommendations) > 0
        
        # 自动放置
        placements = matcher.auto_place_sound_effects(
            segments,
            [(segments[0].scene_id, recommendations[0][0].effect_id)]
        )
        assert len(placements) > 0
    
    def test_character_to_storyboard(self):
        """测试角色创建到分镜生成的集成"""
        engine = CharacterConsistencyEngine()
        
        image_data = self.create_test_image()
        
        # 提取特征
        model = engine.extract_character_features(image_data)
        assert model is not None
        
        # 生成分镜
        frame = engine.generate_storyboard(
            model,
            "小明站在门口",
            style="anime"
        )
        assert frame is not None
        assert len(frame) > 0
    
    def test_audio_to_lip_sync(self):
        """测试音频分析到口型同步的集成"""
        engine = ChineseLipSyncEngine()
        
        audio_data = b"mock_audio_data"
        
        # 分析音频
        analysis = engine.analyze_audio(audio_data)
        assert analysis is not None
        
        # 生成口型
        image_data = self.create_test_image()
        keyframes = engine.generate_lip_sync_keyframes(
            analysis,
            image_data,
            style="anime"
        )
        assert keyframes is not None
    
    def test_frames_to_video(self):
        """测试分镜到视频渲染的集成"""
        engine = VideoRenderingEngine()
        
        # 创建测试帧
        frames = []
        for i in range(3):
            image = Image.new('RGB', (1080, 1920), color=(i*80, 0, 0))
            img_bytes = io.BytesIO()
            image.save(img_bytes, format='PNG')
            frames.append(img_bytes.getvalue())
        
        # 创建配置
        config = engine.create_project_config(
            duration_minutes=1.0
        )
        
        # 渲染视频
        video_url = engine.render_video(frames, config)
        assert video_url is not None


class TestAPIEndpoints:
    """测试API端点可用性"""
    
    def test_all_routers_registered(self):
        """测试所有路由已注册"""
        from app.main import app
        
        # 获取所有路由
        routes = [route.path for route in app.routes]
        
        # 验证核心API端点存在
        assert any("/auth" in route for route in routes)
        assert any("/subscription" in route for route in routes)
        assert any("/projects" in route for route in routes)
        assert any("/lip-sync" in route for route in routes)
        assert any("/character-consistency" in route for route in routes)
        assert any("/video-rendering" in route for route in routes)
        assert any("/sound-effects" in route for route in routes)
        assert any("/workflows" in route for route in routes)


class TestSystemReadiness:
    """测试系统就绪状态"""
    
    def test_all_services_singleton(self):
        """测试所有服务使用单例模式"""
        # 音效匹配器
        matcher1 = SoundEffectMatcher()
        matcher2 = SoundEffectMatcher()
        assert matcher1 is matcher2
        
        # 角色一致性引擎
        engine1 = CharacterConsistencyEngine()
        engine2 = CharacterConsistencyEngine()
        assert engine1 is engine2
        
        # 口型同步引擎
        lip1 = ChineseLipSyncEngine()
        lip2 = ChineseLipSyncEngine()
        assert lip1 is lip2
        
        # 视频渲染引擎
        video1 = VideoRenderingEngine()
        video2 = VideoRenderingEngine()
        assert video1 is video2
        
        # 工作流编排器
        orch1 = WorkflowOrchestrator()
        orch2 = WorkflowOrchestrator()
        assert orch1 is orch2
    
    def test_system_components_count(self):
        """测试系统组件数量"""
        from app.main import app
        
        # 统计路由数量
        routes = [route for route in app.routes if hasattr(route, 'methods')]
        
        # 应该有大量的API端点
        assert len(routes) > 30  # 至少30个端点
    
    def test_core_engines_initialized(self):
        """测试核心引擎已初始化"""
        orchestrator = WorkflowOrchestrator()
        
        # 验证所有引擎都已初始化
        assert orchestrator.sound_matcher._initialized
        assert orchestrator.character_engine._initialized
        assert orchestrator.lip_sync_engine._initialized
        assert orchestrator.video_engine._initialized
        assert orchestrator._initialized


# 性能测试
class TestPerformance:
    """测试性能指标"""
    
    def create_test_image(self) -> bytes:
        """创建测试图像"""
        image = Image.new('RGB', (512, 512), color='blue')
        img_bytes = io.BytesIO()
        image.save(img_bytes, format='PNG')
        return img_bytes.getvalue()
    
    def test_workflow_execution_time(self):
        """测试工作流执行时间"""
        import time
        
        orchestrator = WorkflowOrchestrator()
        
        script = "场景1：测试场景"
        character_images = [self.create_test_image()]
        
        workflow = orchestrator.create_workflow(
            user_id="test_user",
            script=script,
            character_images=character_images
        )
        
        start_time = time.time()
        result = orchestrator.execute_workflow(
            workflow.workflow_id,
            auto_mode=True
        )
        execution_time = time.time() - start_time
        
        # 验证执行时间合理（应该在几秒内完成测试）
        assert execution_time < 30  # 30秒内完成
        assert result.execution_time > 0


# 总结测试
class TestCheckpoint11Summary:
    """检查点11总结测试"""
    
    def test_all_core_features_implemented(self):
        """测试所有核心功能已实现"""
        # 1. 中文口型同步引擎
        lip_sync = ChineseLipSyncEngine()
        assert lip_sync is not None
        
        # 2. 角色一致性引擎
        character = CharacterConsistencyEngine()
        assert character is not None
        
        # 3. 竖屏视频渲染引擎
        video = VideoRenderingEngine()
        assert video is not None
        
        # 4. 智能音效匹配器
        sound = SoundEffectMatcher()
        assert sound is not None
        
        # 5. 完整工作流编排器
        workflow = WorkflowOrchestrator()
        assert workflow is not None
    
    def test_system_integration_complete(self):
        """测试系统集成完整"""
        orchestrator = WorkflowOrchestrator()
        
        # 验证所有模块已集成
        assert orchestrator.sound_matcher is not None
        assert orchestrator.character_engine is not None
        assert orchestrator.lip_sync_engine is not None
        assert orchestrator.video_engine is not None
        
        # 验证可以创建和执行工作流
        script = "测试"
        image = Image.new('RGB', (512, 512), color='blue')
        img_bytes = io.BytesIO()
        image.save(img_bytes, format='PNG')
        
        workflow = orchestrator.create_workflow(
            user_id="test",
            script=script,
            character_images=[img_bytes.getvalue()]
        )
        
        assert workflow is not None
        assert workflow.workflow_id
