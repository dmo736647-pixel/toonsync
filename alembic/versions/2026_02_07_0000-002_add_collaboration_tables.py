"""add collaboration tables

Revision ID: 002
Revises: 001
Create Date: 2026-02-07 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 创建枚举类型
    op.execute("CREATE TYPE collaboratorrole AS ENUM ('viewer', 'editor', 'admin')")
    op.execute("CREATE TYPE invitationstatus AS ENUM ('pending', 'accepted', 'rejected', 'expired')")
    op.execute("CREATE TYPE template_visibility AS ENUM ('PUBLIC', 'PRIVATE')")
    
    # 创建项目协作者表
    op.create_table(
        'project_collaborators',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.Enum('viewer', 'editor', 'admin', name='collaboratorrole'), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_project_collaborators_project_id', 'project_collaborators', ['project_id'])
    op.create_index('ix_project_collaborators_user_id', 'project_collaborators', ['user_id'])
    
    # 创建项目邀请表
    op.create_table(
        'project_invitations',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('inviter_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('invitee_email', sa.String(255), nullable=False),
        sa.Column('role', sa.Enum('viewer', 'editor', 'admin', name='collaboratorrole'), nullable=False),
        sa.Column('status', sa.Enum('pending', 'accepted', 'rejected', 'expired', name='invitationstatus'), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['inviter_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_project_invitations_project_id', 'project_invitations', ['project_id'])
    op.create_index('ix_project_invitations_invitee_email', 'project_invitations', ['invitee_email'])
    
    # 创建项目版本表
    op.create_table(
        'project_versions',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('version_number', sa.Integer(), nullable=False),
        sa.Column('description', sa.String(500), nullable=True),
        sa.Column('snapshot_data', sa.String(), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_project_versions_project_id', 'project_versions', ['project_id'])
    
    # 创建项目模板表
    op.create_table(
        'project_templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.String(1000), nullable=True),
        sa.Column('template_data', sa.String(), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('is_public', sa.Enum('PUBLIC', 'PRIVATE', name='template_visibility'), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('project_templates')
    op.drop_table('project_versions')
    op.drop_index('ix_project_invitations_invitee_email', 'project_invitations')
    op.drop_index('ix_project_invitations_project_id', 'project_invitations')
    op.drop_table('project_invitations')
    op.drop_index('ix_project_collaborators_user_id', 'project_collaborators')
    op.drop_index('ix_project_collaborators_project_id', 'project_collaborators')
    op.drop_table('project_collaborators')
    
    op.execute("DROP TYPE template_visibility")
    op.execute("DROP TYPE invitationstatus")
    op.execute("DROP TYPE collaboratorrole")
