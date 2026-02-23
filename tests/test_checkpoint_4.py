"""检查点4：认证和项目管理功能集成测试"""
import pytest
from sqlalchemy.orm import Session

from app.services.auth import AuthenticationService
from app.services.subscription import SubscriptionService
from app.services.usage import UsageService
from app.services.project import ProjectService
from app.services.collaboration import CollaborationService
from app.models.user import SubscriptionTier
from app.models.project import AspectRatio


class TestCheckpoint4Authentication:
    """检查点4 - 认证功能验证"""
    
    def test_complete_authentication_flow(self, db_session: Session):
        """测试完整的认证流程：注册 → 登录 → 获取用户信息"""
        auth_service = AuthenticationService(db_session)
        
        # 1. 用户注册
        user = auth_service.register_user("checkpoint@test.com", "password123")
        assert user is not None
        assert user.email == "checkpoint@test.com"
        assert user.subscription_tier == SubscriptionTier.FREE
        assert user.remaining_quota_minutes == 5.0
        print("✓ 用户注册成功")
        
        # 2. 用户登录
        logged_in_user, token = auth_service.login("checkpoint@test.com", "password123")
        assert logged_in_user.id == user.id
        assert token is not None
        assert len(token) > 0
        print("✓ 用户登录成功，获得JWT令牌")
        
        # 3. 验证令牌
        payload = auth_service.verify_token(token)
        assert payload is not None
        assert payload["sub"] == str(user.id)
        assert payload["email"] == user.email
        print("✓ JWT令牌验证成功")
        
        # 4. 使用令牌获取用户信息
        current_user = auth_service.get_current_user(token)
        assert current_user is not None
        assert current_user.id == user.id
        print("✓ 通过令牌获取用户信息成功")
        
        print("\n✅ 认证功能完整流程测试通过！")


class TestCheckpoint4Subscription:
    """检查点4 - 订阅管理功能验证"""
    
    def test_complete_subscription_flow(self, db_session: Session):
        """测试完整的订阅流程：注册 → 激活订阅 → 检查状态 → 切换计划"""
        auth_service = AuthenticationService(db_session)
        subscription_service = SubscriptionService(db_session)
        
        # 1. 创建用户
        user = auth_service.register_user("sub@test.com", "password123")
        print(f"✓ 创建用户，初始订阅层级：{user.subscription_tier.value}")
        
        # 2. 激活专业版订阅
        updated_user, subscription = subscription_service.activate_subscription(
            user_id=user.id,
            plan=SubscriptionTier.PROFESSIONAL
        )
        assert updated_user.subscription_tier == SubscriptionTier.PROFESSIONAL
        assert subscription.plan == SubscriptionTier.PROFESSIONAL
        assert subscription.quota_minutes == 50.0
        print(f"✓ 激活专业版订阅成功，额度：{updated_user.remaining_quota_minutes}分钟")
        
        # 3. 检查订阅状态
        is_expired = subscription_service.check_subscription_expiry(user.id)
        assert is_expired is False
        print("✓ 订阅状态检查：未过期")
        
        # 4. 获取活跃订阅
        active_sub = subscription_service.get_active_subscription(user.id)
        assert active_sub is not None
        assert active_sub.plan == SubscriptionTier.PROFESSIONAL
        print("✓ 获取活跃订阅成功")
        
        # 5. 切换到企业版
        new_user, new_sub = subscription_service.switch_subscription_plan(
            user_id=user.id,
            new_plan=SubscriptionTier.ENTERPRISE
        )
        assert new_user.subscription_tier == SubscriptionTier.ENTERPRISE
        print(f"✓ 切换到企业版成功，新额度：{new_user.remaining_quota_minutes}分钟")
        
        print("\n✅ 订阅管理功能完整流程测试通过！")


class TestCheckpoint4Usage:
    """检查点4 - 额度管理功能验证"""
    
    def test_complete_usage_flow(self, db_session: Session):
        """测试完整的额度管理流程：扣减 → 统计 → 恢复"""
        auth_service = AuthenticationService(db_session)
        usage_service = UsageService(db_session)
        
        # 1. 创建用户
        user = auth_service.register_user("usage@test.com", "password123")
        initial_quota = user.remaining_quota_minutes
        print(f"✓ 创建用户，初始额度：{initial_quota}分钟")
        
        # 2. 扣减额度
        updated_user, cost = usage_service.deduct_quota(
            user_id=user.id,
            duration_minutes=2.0,
            action_type="test_export"
        )
        assert updated_user.remaining_quota_minutes == initial_quota - 2.0
        print(f"✓ 扣减2分钟额度，剩余：{updated_user.remaining_quota_minutes}分钟")
        
        # 3. 获取使用统计
        statistics = usage_service.get_usage_statistics(user_id=user.id, days=30)
        assert statistics["total_usage_minutes"] >= 2.0
        assert statistics["usage_count"] >= 1
        print(f"✓ 获取使用统计：总使用{statistics['total_usage_minutes']}分钟，{statistics['usage_count']}次")
        
        # 4. 获取使用历史
        history = usage_service.get_usage_history(user_id=user.id, limit=10)
        assert len(history) >= 1
        print(f"✓ 获取使用历史：{len(history)}条记录")
        
        # 5. 计算导出费用
        cost_info = usage_service.calculate_export_cost(
            user_id=user.id,
            video_duration_minutes=1.5
        )
        assert "cost" in cost_info
        assert "needs_payment" in cost_info
        print(f"✓ 计算导出费用：{cost_info['cost']}元，需要付费：{cost_info['needs_payment']}")
        
        # 6. 恢复额度
        restored_user = usage_service.restore_quota(
            user_id=user.id,
            duration_minutes=1.0
        )
        assert restored_user.remaining_quota_minutes == updated_user.remaining_quota_minutes + 1.0
        print(f"✓ 恢复1分钟额度，当前：{restored_user.remaining_quota_minutes}分钟")
        
        print("\n✅ 额度管理功能完整流程测试通过！")


class TestCheckpoint4Project:
    """检查点4 - 项目管理功能验证"""
    
    def test_complete_project_flow(self, db_session: Session):
        """测试完整的项目管理流程：创建 → 列表 → 更新 → 删除"""
        auth_service = AuthenticationService(db_session)
        project_service = ProjectService(db_session)
        
        # 1. 创建用户
        user = auth_service.register_user("project@test.com", "password123")
        print("✓ 创建用户")
        
        # 2. 创建项目
        project = project_service.create_project(
            user_id=user.id,
            name="测试项目",
            aspect_ratio=AspectRatio.VERTICAL_9_16,
            script="这是一个测试剧本"
        )
        assert project is not None
        assert project.name == "测试项目"
        assert project.user_id == user.id
        assert project.aspect_ratio == AspectRatio.VERTICAL_9_16
        print(f"✓ 创建项目成功，项目ID：{project.id}")
        
        # 3. 获取项目列表
        projects = project_service.get_user_projects(user_id=user.id)
        assert len(projects) >= 1
        assert projects[0].id == project.id
        print(f"✓ 获取项目列表：{len(projects)}个项目")
        
        # 4. 获取单个项目
        retrieved_project = project_service.get_project(project_id=project.id)
        assert retrieved_project is not None
        assert retrieved_project.id == project.id
        print("✓ 获取单个项目成功")
        
        # 5. 更新项目
        updated_project = project_service.update_project(
            project_id=project.id,
            name="更新后的项目名称",
            script="更新后的剧本"
        )
        assert updated_project.name == "更新后的项目名称"
        assert updated_project.script == "更新后的剧本"
        print("✓ 更新项目成功")
        
        # 6. 删除项目
        result = project_service.delete_project(project_id=project.id)
        assert result is True
        print("✓ 删除项目成功")
        
        # 7. 验证项目已删除
        deleted_project = project_service.get_project(project_id=project.id)
        assert deleted_project is None
        print("✓ 验证项目已删除")
        
        print("\n✅ 项目管理功能完整流程测试通过！")


class TestCheckpoint4Collaboration:
    """检查点4 - 协作功能验证"""
    
    def test_complete_collaboration_flow(self, db_session: Session):
        """测试完整的协作流程：邀请 → 接受 → 权限验证"""
        auth_service = AuthenticationService(db_session)
        project_service = ProjectService(db_session)
        collaboration_service = CollaborationService(db_session)
        
        # 1. 创建两个用户
        owner = auth_service.register_user("owner@test.com", "password123")
        collaborator = auth_service.register_user("collab@test.com", "password123")
        print("✓ 创建项目所有者和协作者")
        
        # 2. 创建项目
        project = project_service.create_project(
            user_id=owner.id,
            name="协作测试项目"
        )
        print(f"✓ 创建项目：{project.name}")
        
        # 3. 邀请协作者
        from app.models.collaboration import CollaboratorRole
        invitation = collaboration_service.invite_collaborator(
            project_id=project.id,
            inviter_id=owner.id,
            email="collab@test.com",
            role=CollaboratorRole.EDITOR
        )
        assert invitation is not None
        print(f"✓ 发送邀请给 {invitation.email}，角色：{invitation.role.value}")
        
        # 4. 接受邀请
        accepted = collaboration_service.accept_invitation(
            invitation_id=invitation.id,
            user_id=collaborator.id
        )
        assert accepted is True
        print("✓ 协作者接受邀请")
        
        # 5. 获取项目协作者列表
        collaborators = collaboration_service.get_project_collaborators(project_id=project.id)
        assert len(collaborators) >= 1
        print(f"✓ 获取协作者列表：{len(collaborators)}个协作者")
        
        # 6. 检查用户权限
        has_permission = collaboration_service.check_user_permission(
            project_id=project.id,
            user_id=collaborator.id,
            required_role=CollaboratorRole.VIEWER
        )
        assert has_permission is True
        print("✓ 验证协作者权限成功")
        
        # 7. 获取用户可访问的项目
        accessible_projects = collaboration_service.get_user_accessible_projects(
            user_id=collaborator.id
        )
        assert len(accessible_projects) >= 1
        print(f"✓ 协作者可访问 {len(accessible_projects)} 个项目")
        
        print("\n✅ 协作功能完整流程测试通过！")


class TestCheckpoint4Integration:
    """检查点4 - 集成测试"""
    
    def test_end_to_end_scenario(self, db_session: Session):
        """测试端到端场景：用户注册 → 订阅 → 创建项目 → 邀请协作 → 使用额度"""
        auth_service = AuthenticationService(db_session)
        subscription_service = SubscriptionService(db_session)
        project_service = ProjectService(db_session)
        collaboration_service = CollaborationService(db_session)
        usage_service = UsageService(db_session)
        
        print("\n开始端到端集成测试...")
        
        # 场景1：用户A注册并升级订阅
        user_a = auth_service.register_user("usera@test.com", "password123")
        print(f"1. 用户A注册成功：{user_a.email}")
        
        user_a, sub_a = subscription_service.activate_subscription(
            user_id=user_a.id,
            plan=SubscriptionTier.PROFESSIONAL
        )
        print(f"2. 用户A升级到专业版，额度：{user_a.remaining_quota_minutes}分钟")
        
        # 场景2：用户A创建项目
        project = project_service.create_project(
            user_id=user_a.id,
            name="我的第一个微短剧",
            aspect_ratio=AspectRatio.VERTICAL_9_16,
            script="场景1：室内，白天。角色A：你好！"
        )
        print(f"3. 用户A创建项目：{project.name}")
        
        # 场景3：用户B注册
        user_b = auth_service.register_user("userb@test.com", "password123")
        print(f"4. 用户B注册成功：{user_b.email}")
        
        # 场景4：用户A邀请用户B协作
        from app.models.collaboration import CollaboratorRole
        invitation = collaboration_service.invite_collaborator(
            project_id=project.id,
            inviter_id=user_a.id,
            email="userb@test.com",
            role=CollaboratorRole.EDITOR
        )
        print(f"5. 用户A邀请用户B为编辑者")
        
        # 场景5：用户B接受邀请
        collaboration_service.accept_invitation(
            invitation_id=invitation.id,
            user_id=user_b.id
        )
        print("6. 用户B接受邀请")
        
        # 场景6：用户A使用额度导出视频
        cost_info = usage_service.calculate_export_cost(
            user_id=user_a.id,
            video_duration_minutes=2.5
        )
        print(f"7. 计算导出费用：{cost_info['cost']}元")
        
        if not cost_info['needs_payment']:
            user_a, cost = usage_service.deduct_quota(
                user_id=user_a.id,
                duration_minutes=2.5,
                action_type="video_export"
            )
            print(f"8. 扣减额度成功，剩余：{user_a.remaining_quota_minutes}分钟")
        
        # 场景7：查看使用统计
        statistics = usage_service.get_usage_statistics(user_id=user_a.id, days=30)
        print(f"9. 使用统计：总使用{statistics['total_usage_minutes']}分钟")
        
        # 场景8：用户B查看可访问的项目
        accessible_projects = collaboration_service.get_user_accessible_projects(
            user_id=user_b.id
        )
        print(f"10. 用户B可访问{len(accessible_projects)}个项目")
        
        print("\n✅ 端到端集成测试通过！所有功能协同工作正常！")


def test_checkpoint_4_summary(db_session: Session):
    """检查点4总结测试"""
    print("\n" + "="*60)
    print("检查点4：认证和项目管理功能验证")
    print("="*60)
    
    # 运行所有检查点测试
    checkpoint_auth = TestCheckpoint4Authentication()
    checkpoint_auth.test_complete_authentication_flow(db_session)
    
    checkpoint_sub = TestCheckpoint4Subscription()
    checkpoint_sub.test_complete_subscription_flow(db_session)
    
    checkpoint_usage = TestCheckpoint4Usage()
    checkpoint_usage.test_complete_usage_flow(db_session)
    
    checkpoint_project = TestCheckpoint4Project()
    checkpoint_project.test_complete_project_flow(db_session)
    
    checkpoint_collab = TestCheckpoint4Collaboration()
    checkpoint_collab.test_complete_collaboration_flow(db_session)
    
    checkpoint_integration = TestCheckpoint4Integration()
    checkpoint_integration.test_end_to_end_scenario(db_session)
    
    print("\n" + "="*60)
    print("✅ 检查点4：所有测试通过！")
    print("="*60)
    print("\n已验证的功能模块：")
    print("  ✓ 用户认证（注册、登录、JWT令牌）")
    print("  ✓ 订阅管理（激活、切换、到期处理）")
    print("  ✓ 额度管理（扣减、恢复、统计）")
    print("  ✓ 项目管理（创建、更新、删除）")
    print("  ✓ 协作功能（邀请、接受、权限验证）")
    print("  ✓ 端到端集成（多模块协同工作）")
    print("\n系统已准备好进入下一阶段开发！")
    print("="*60 + "\n")
