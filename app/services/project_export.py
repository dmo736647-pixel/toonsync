"""项目源文件导出服务"""
import json
import zipfile
from pathlib import Path
from typing import Optional
from io import BytesIO
from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.character import Character
from app.models.storyboard import StoryboardFrame
from app.models.audio import AudioTrack
from app.core.storage import storage_manager


class ProjectExportService:
    """项目源文件导出服务
    
    需求：11.6
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def export_project(self, project_id: str, include_media: bool = True) -> BytesIO:
        """
        导出项目源文件
        
        参数:
            project_id: 项目ID
            include_media: 是否包含媒体文件（图片、音频等）
        
        返回:
            BytesIO: 包含项目数据的ZIP文件
        
        需求：11.6
        """
        # 获取项目数据
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError(f"项目不存在: {project_id}")
        
        # 创建ZIP文件
        zip_buffer = BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # 导出项目元数据
            self._export_project_metadata(zip_file, project)
            
            # 导出角色数据
            self._export_characters(zip_file, project, include_media)
            
            # 导出分镜数据
            self._export_storyboard(zip_file, project, include_media)
            
            # 导出音频数据
            self._export_audio(zip_file, project, include_media)
        
        zip_buffer.seek(0)
        return zip_buffer
    
    def _export_project_metadata(self, zip_file: zipfile.ZipFile, project: Project) -> None:
        """导出项目元数据"""
        metadata = {
            "id": str(project.id),
            "name": project.name,
            "aspect_ratio": project.aspect_ratio,
            "duration_minutes": project.duration_minutes,
            "script": project.script,
            "created_at": project.created_at.isoformat() if project.created_at else None,
            "updated_at": project.updated_at.isoformat() if project.updated_at else None
        }
        
        # 写入JSON文件
        zip_file.writestr(
            "project.json",
            json.dumps(metadata, indent=2, ensure_ascii=False)
        )
    
    def _export_characters(
        self,
        zip_file: zipfile.ZipFile,
        project: Project,
        include_media: bool
    ) -> None:
        """导出角色数据"""
        characters = self.db.query(Character).filter(
            Character.project_id == project.id
        ).all()
        
        characters_data = []
        
        for character in characters:
            char_data = {
                "id": str(character.id),
                "name": character.name,
                "style": character.style,
                "reference_image_url": character.reference_image_url,
                "consistency_model_url": character.consistency_model_url,
                "created_at": character.created_at.isoformat() if character.created_at else None
            }
            characters_data.append(char_data)
            
            # 如果包含媒体文件，下载并添加到ZIP
            if include_media:
                self._add_media_to_zip(
                    zip_file,
                    character.reference_image_url,
                    f"characters/{character.id}/reference_image"
                )
                
                if character.consistency_model_url:
                    self._add_media_to_zip(
                        zip_file,
                        character.consistency_model_url,
                        f"characters/{character.id}/consistency_model"
                    )
        
        # 写入角色列表JSON
        zip_file.writestr(
            "characters.json",
            json.dumps(characters_data, indent=2, ensure_ascii=False)
        )
    
    def _export_storyboard(
        self,
        zip_file: zipfile.ZipFile,
        project: Project,
        include_media: bool
    ) -> None:
        """导出分镜数据"""
        frames = self.db.query(StoryboardFrame).filter(
            StoryboardFrame.project_id == project.id
        ).order_by(StoryboardFrame.sequence_number).all()
        
        frames_data = []
        
        for frame in frames:
            frame_data = {
                "id": str(frame.id),
                "sequence_number": frame.sequence_number,
                "character_id": str(frame.character_id) if frame.character_id else None,
                "scene_description": frame.scene_description,
                "image_url": frame.image_url,
                "duration_seconds": frame.duration_seconds,
                "lip_sync_keyframes": frame.lip_sync_keyframes,
                "created_at": frame.created_at.isoformat() if frame.created_at else None
            }
            frames_data.append(frame_data)
            
            # 如果包含媒体文件，下载并添加到ZIP
            if include_media and frame.image_url:
                self._add_media_to_zip(
                    zip_file,
                    frame.image_url,
                    f"storyboard/frame_{frame.sequence_number:04d}"
                )
        
        # 写入分镜列表JSON
        zip_file.writestr(
            "storyboard.json",
            json.dumps(frames_data, indent=2, ensure_ascii=False)
        )
    
    def _export_audio(
        self,
        zip_file: zipfile.ZipFile,
        project: Project,
        include_media: bool
    ) -> None:
        """导出音频数据"""
        audio_tracks = self.db.query(AudioTrack).filter(
            AudioTrack.project_id == project.id
        ).all()
        
        audio_data = []
        
        for track in audio_tracks:
            track_data = {
                "id": str(track.id),
                "audio_file_url": track.audio_file_url,
                "duration_seconds": track.duration_seconds,
                "transcript": track.transcript,
                "created_at": track.created_at.isoformat() if track.created_at else None
            }
            audio_data.append(track_data)
            
            # 如果包含媒体文件，下载并添加到ZIP
            if include_media and track.audio_file_url:
                self._add_media_to_zip(
                    zip_file,
                    track.audio_file_url,
                    f"audio/{track.id}"
                )
        
        # 写入音频列表JSON
        zip_file.writestr(
            "audio.json",
            json.dumps(audio_data, indent=2, ensure_ascii=False)
        )
    
    def _add_media_to_zip(
        self,
        zip_file: zipfile.ZipFile,
        media_url: str,
        zip_path: str
    ) -> None:
        """添加媒体文件到ZIP"""
        try:
            # 从URL提取对象键
            # 假设URL格式为 /storage/path/to/file 或 https://s3.../path/to/file
            if media_url.startswith("/storage/"):
                object_key = media_url.replace("/storage/", "")
            else:
                # 从完整URL提取路径
                from urllib.parse import urlparse
                parsed = urlparse(media_url)
                object_key = parsed.path.lstrip("/")
            
            # 下载文件
            file_content = storage_manager.download_file(object_key)
            
            # 添加到ZIP（保留文件扩展名）
            file_ext = Path(object_key).suffix
            zip_file.writestr(f"{zip_path}{file_ext}", file_content)
        
        except Exception as e:
            # 如果下载失败，记录错误但继续导出
            print(f"警告: 无法下载媒体文件 {media_url}: {str(e)}")
    
    def get_export_filename(self, project_id: str) -> str:
        """
        获取导出文件名
        
        参数:
            project_id: 项目ID
        
        返回:
            导出文件名
        """
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return f"project_{project_id}.zip"
        
        # 清理项目名称，移除不安全字符
        safe_name = "".join(c for c in project.name if c.isalnum() or c in (' ', '-', '_'))
        safe_name = safe_name.strip().replace(' ', '_')
        
        return f"{safe_name}_{project_id[:8]}.zip"
