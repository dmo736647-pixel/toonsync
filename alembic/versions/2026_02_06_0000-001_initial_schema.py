"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2026-02-06 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 创建用户表
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('subscription_tier', sa.Enum('FREE', 'PAY_PER_USE', 'PROFESSIONAL', 'ENTERPRISE', name='subscriptiontier'), nullable=False),
        sa.Column('remaining_quota_minutes', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    
    # 创建项目表
    op.create_table(
        'projects',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('aspect_ratio', sa.Enum('VERTICAL_9_16', 'HORIZONTAL_16_9', 'SQUARE_1_1', name='aspectratio'), nullable=False),
        sa.Column('duration_minutes', sa.Float(), nullable=True),
        sa.Column('script', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_projects_id'), 'projects', ['id'], unique=False)
    op.create_index(op.f('ix_projects_user_id'), 'projects', ['user_id'], unique=False)
    
    # 创建角色表
    op.create_table(
        'characters',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('reference_image_url', sa.Text(), nullable=False),
        sa.Column('consistency_model_url', sa.Text(), nullable=True),
        sa.Column('style', sa.Enum('ANIME', 'REALISTIC', name='renderstyle'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_characters_id'), 'characters', ['id'], unique=False)
    op.create_index(op.f('ix_characters_project_id'), 'characters', ['project_id'], unique=False)
    
    # 创建分镜表
    op.create_table(
        'storyboard_frames',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('sequence_number', sa.Integer(), nullable=False),
        sa.Column('character_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('scene_description', sa.Text(), nullable=True),
        sa.Column('image_url', sa.Text(), nullable=True),
        sa.Column('duration_seconds', sa.Float(), nullable=True),
        sa.Column('lip_sync_keyframes', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['character_id'], ['characters.id'], ),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_storyboard_frames_id'), 'storyboard_frames', ['id'], unique=False)
    op.create_index(op.f('ix_storyboard_frames_project_id'), 'storyboard_frames', ['project_id'], unique=False)
    
    # 创建音频轨道表
    op.create_table(
        'audio_tracks',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('audio_file_url', sa.Text(), nullable=False),
        sa.Column('duration_seconds', sa.Float(), nullable=False),
        sa.Column('transcript', sa.Text(), nullable=True),
        sa.Column('audio_analysis', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_audio_tracks_id'), 'audio_tracks', ['id'], unique=False)
    op.create_index(op.f('ix_audio_tracks_project_id'), 'audio_tracks', ['project_id'], unique=False)
    
    # 创建音效表
    op.create_table(
        'sound_effects',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('audio_file_url', sa.Text(), nullable=False),
        sa.Column('duration_seconds', sa.Float(), nullable=False),
        sa.Column('tags', sa.ARRAY(sa.String()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sound_effects_category'), 'sound_effects', ['category'], unique=False)
    op.create_index(op.f('ix_sound_effects_id'), 'sound_effects', ['id'], unique=False)
    
    # 创建订阅表
    op.create_table(
        'subscriptions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('plan', sa.Enum('FREE', 'PAY_PER_USE', 'PROFESSIONAL', 'ENTERPRISE', name='subscriptiontier'), nullable=False),
        sa.Column('quota_minutes', sa.Float(), nullable=False),
        sa.Column('start_date', sa.DateTime(), nullable=False),
        sa.Column('end_date', sa.DateTime(), nullable=False),
        sa.Column('auto_renew', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_subscriptions_id'), 'subscriptions', ['id'], unique=False)
    op.create_index(op.f('ix_subscriptions_user_id'), 'subscriptions', ['user_id'], unique=False)


def downgrade() -> None:
    # 删除表（逆序）
    op.drop_index(op.f('ix_subscriptions_user_id'), table_name='subscriptions')
    op.drop_index(op.f('ix_subscriptions_id'), table_name='subscriptions')
    op.drop_table('subscriptions')
    
    op.drop_index(op.f('ix_sound_effects_id'), table_name='sound_effects')
    op.drop_index(op.f('ix_sound_effects_category'), table_name='sound_effects')
    op.drop_table('sound_effects')
    
    op.drop_index(op.f('ix_audio_tracks_project_id'), table_name='audio_tracks')
    op.drop_index(op.f('ix_audio_tracks_id'), table_name='audio_tracks')
    op.drop_table('audio_tracks')
    
    op.drop_index(op.f('ix_storyboard_frames_project_id'), table_name='storyboard_frames')
    op.drop_index(op.f('ix_storyboard_frames_id'), table_name='storyboard_frames')
    op.drop_table('storyboard_frames')
    
    op.drop_index(op.f('ix_characters_project_id'), table_name='characters')
    op.drop_index(op.f('ix_characters_id'), table_name='characters')
    op.drop_table('characters')
    
    op.drop_index(op.f('ix_projects_user_id'), table_name='projects')
    op.drop_index(op.f('ix_projects_id'), table_name='projects')
    op.drop_table('projects')
    
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    
    # 删除枚举类型
    sa.Enum(name='subscriptiontier').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='aspectratio').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='renderstyle').drop(op.get_bind(), checkfirst=True)
