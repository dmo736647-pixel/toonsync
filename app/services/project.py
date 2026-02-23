"""项目管理服务"""
from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload

from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectService:
    """项目管理服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_project(self, user_id: UUID, project_data: ProjectCreate) -> Project:
        """
        创建新项目
        
        参数:
            user_id: 用户ID
            project_data: 项目创建数据
        
        返回:
            Project: 创建的项目对象
        """
        project = Project(
            user_id=user_id,
            name=project_data.name,
            aspect_ratio=project_data.aspect_ratio,
            duration_minutes=project_data.duration_minutes,
            script=project_data.script
        )
        
        self.db.add(project)
        await self.db.commit()
        await self.db.refresh(project)
        
        return project
    
    async def get_project(self, project_id: UUID, user_id: UUID) -> Optional[Project]:
        """
        获取项目详情
        
        参数:
            project_id: 项目ID
            user_id: 用户ID（用于权限验证）
        
        返回:
            Optional[Project]: 项目对象，如果不存在或无权限则返回None
        """
        result = await self.db.execute(
            select(Project)
            .where(and_(Project.id == project_id, Project.user_id == user_id))
            .options(selectinload(Project.characters))
        )
        return result.scalar_one_or_none()
    
    async def list_projects(
        self,
        user_id: UUID,
        page: int = 1,
        page_size: int = 50,
        name_filter: Optional[str] = None
    ) -> tuple[List[Project], int]:
        """
        列出用户的项目
        
        参数:
            user_id: 用户ID
            page: 页码（从1开始）
            page_size: 每页数量
            name_filter: 项目名称过滤（可选）
        
        返回:
            tuple[List[Project], int]: (项目列表, 总数)
        """
        # 构建查询条件
        conditions = [Project.user_id == user_id]
        if name_filter:
            conditions.append(Project.name.ilike(f"%{name_filter}%"))
        
        # 查询总数
        count_result = await self.db.execute(
            select(func.count(Project.id)).where(and_(*conditions))
        )
        total = count_result.scalar_one()
        
        # 查询项目列表
        offset = (page - 1) * page_size
        result = await self.db.execute(
            select(Project)
            .where(and_(*conditions))
            .order_by(Project.updated_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        projects = result.scalars().all()
        
        return list(projects), total
    
    async def update_project(
        self,
        project_id: UUID,
        user_id: UUID,
        project_data: ProjectUpdate
    ) -> Optional[Project]:
        """
        更新项目
        
        参数:
            project_id: 项目ID
            user_id: 用户ID（用于权限验证）
            project_data: 项目更新数据
        
        返回:
            Optional[Project]: 更新后的项目对象，如果不存在或无权限则返回None
        """
        project = await self.get_project(project_id, user_id)
        if not project:
            return None
        
        # 更新字段
        update_data = project_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(project, field, value)
        
        await self.db.commit()
        await self.db.refresh(project)
        
        return project
    
    async def delete_project(self, project_id: UUID, user_id: UUID) -> bool:
        """
        删除项目
        
        参数:
            project_id: 项目ID
            user_id: 用户ID（用于权限验证）
        
        返回:
            bool: 是否删除成功
        """
        project = await self.get_project(project_id, user_id)
        if not project:
            return False
        
        await self.db.delete(project)
        await self.db.commit()
        
        return True
