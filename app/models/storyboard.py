"""分镜模型"""
from sqlalchemy import Column, Integer, Text, Float, ForeignKey, JSON, ARRAY
from sqlalchemy.orm import relationship

from app.models.base import BaseModel, GUID


class StoryboardFrame(BaseModel):
    """分镜帧模型 (对应数据库中的 scenes 表)"""
    
    __tablename__ = "scenes"
    
    project_id = Column(GUID(), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    sequence_number = Column(Integer, nullable=False)
    # character_id = Column(GUID(), ForeignKey("characters.id"), nullable=True) # Old model
    # scene_description = Column(Text, nullable=True) # Old model
    
    # Mapping to existing 'scenes' table schema
    description = Column(Text, nullable=False) # Maps to scene_description concept
    character_ids = Column(ARRAY(GUID), nullable=True) # Maps to character_ids array in DB
    
    # Optional fields from schema or needed for app
    dialogue = Column(Text, nullable=True)
    background_desc = Column(Text, nullable=True)
    status = Column(Text, default='pending')
    
    # New fields not in original schema but useful (if we can alter table, otherwise ignore or mapped)
    # If the table doesn't have these, SQLAlchemy will error on insert/select unless we migrate.
    # The schema.sql shows: id, project_id, script_id, sequence_number, description, dialogue, character_ids, background_desc, status, created_at
    
    # We need to be careful. The original 'scenes' table doesn't have image_url directly?
    # Schema says: 6. GENERATED_ASSETS table stores images.
    # So StoryboardFrame (Scene) shouldn't have image_url column if we follow schema strictly.
    # But frontend expects image_url.
    # We should probably join with GeneratedAssets or add a property.
    
    # For now, to make the insert work, we must match the table columns.
    
    script_id = Column(GUID(), ForeignKey("scripts.id"), nullable=True)

    # Relationships
    project = relationship("Project", back_populates="storyboard_frames")
    # character = relationship("Character", back_populates="storyboard_frames") # This won't work easily with ARRAY
    
    # We can add a relationship to assets
    generated_assets = relationship("GeneratedAsset", back_populates="scene", cascade="all, delete-orphan")

    @property
    def image_url(self):
        """Helper to get the latest image url from assets"""
        # This logic should be in service/schema, but model property is convenient if loaded eagerly
        # For simplicity in this fix, we will handle this in service/schema mapping
        return None

