"""协作相关模型"""
from sqlalchemy import Column, String, ForeignKey, Enum as SQLEnum, Integer
from sqlalchemy.orm import relationship
import enum

from app.models.base import BaseModel, GUID


class CollaboratorRole(str, enum.Enum):
    """协作者角色"""
    VIEWER = "viewer"  # 查看者：只能查看项目
    EDITOR = "editor"  # 编辑者：可以编辑项目
    ADMIN = "admin"    # 管理员：可以管理项目和协作者


class TemplateVisibility(str, enum.Enum):
    """模板可见性"""
    PUBLIC = "public"
    PRIVATE = "private"



class InvitationStatus(str, enum.Enum):
    """邀请状态"""
    PENDING = "pending"      # 待处理
    ACCEPTED = "accepted"    # 已接受
    REJECTED = "rejected"    # 已拒绝
    EXPIRED = "expired"      # 已过期


class ProjectCollaborator(BaseModel):
    """项目协作者"""
    
    __tablename__ = "project_collaborators"
    
    project_id = Column(GUID(), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(SQLEnum(CollaboratorRole), nullable=False, default=CollaboratorRole.VIEWER)
    
    # 关系
    project = relationship("Project", backref="collaborators")
    user = relationship("User", backref="collaborations")
    
    __table_args__ = (
        # 确保同一用户在同一项目中只能有一个角色
        {'schema': None},
    )


class ProjectInvitation(BaseModel):
    """项目邀请"""
    
    __tablename__ = "project_invitations"
    
    project_id = Column(GUID(), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    inviter_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    invitee_email = Column(String(255), nullable=False, index=True)
    role = Column(SQLEnum(CollaboratorRole), nullable=False, default=CollaboratorRole.VIEWER)
    status = Column(SQLEnum(InvitationStatus), nullable=False, default=InvitationStatus.PENDING)
    
    # 关系
    project = relationship("Project", backref="invitations")
    inviter = relationship("User", foreign_keys=[inviter_id])


class ProjectVersion(BaseModel):
    """项目版本历史"""
    
    __tablename__ = "project_versions"
    
    project_id = Column(GUID(), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)
    description = Column(String(500), nullable=True)
    snapshot_data = Column(String, nullable=False)  # JSON格式的项目快照
    created_by = Column(GUID(), ForeignKey("users.id"), nullable=False)
    
    # 关系
    project = relationship("Project", backref="versions")
    creator = relationship("User")
    
    __table_args__ = (
        {'schema': None},
    )


class ProjectTemplate(BaseModel):
    """项目模板"""
    
    __tablename__ = "project_templates"
    
    name = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    template_data = Column(String, nullable=False)  # JSON格式的模板数据
    created_by = Column(GUID(), ForeignKey("users.id"), nullable=False)
    is_public = Column(SQLEnum(TemplateVisibility), nullable=False, default=TemplateVisibility.PRIVATE)
    
    # 关系
    creator = relationship("User", backref="templates")
