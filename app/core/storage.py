"""对象存储管理（S3或本地存储）"""
import os
from pathlib import Path
from typing import BinaryIO, Optional
import boto3
from botocore.exceptions import ClientError

from app.core.config import settings


class StorageManager:
    """存储管理器（支持S3和本地存储）"""
    
    def __init__(self) -> None:
        self.use_local = settings.USE_LOCAL_STORAGE
        
        if self.use_local:
            # 使用本地存储
            self.storage_path = Path(settings.LOCAL_STORAGE_PATH)
            self.storage_path.mkdir(parents=True, exist_ok=True)
        else:
            # 使用S3存储
            self.s3_client = boto3.client(
                's3',
                endpoint_url=settings.S3_ENDPOINT_URL or None,
                aws_access_key_id=settings.S3_ACCESS_KEY,
                aws_secret_access_key=settings.S3_SECRET_KEY,
                region_name=settings.S3_REGION,
            )
            self.bucket_name = settings.S3_BUCKET_NAME
    
    def upload_file(
        self,
        file: BinaryIO,
        object_key: str,
        content_type: Optional[str] = None
    ) -> str:
        """
        上传文件
        
        参数:
            file: 文件对象
            object_key: 对象键（路径）
            content_type: 内容类型
        
        返回:
            文件URL
        """
        if self.use_local:
            return self._upload_local(file, object_key)
        else:
            return self._upload_s3(file, object_key, content_type)
    
    def _upload_local(self, file: BinaryIO, object_key: str) -> str:
        """上传到本地存储"""
        file_path = self.storage_path / object_key
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'wb') as f:
            f.write(file.read())
        
        return f"/storage/{object_key}"
    
    def _upload_s3(
        self,
        file: BinaryIO,
        object_key: str,
        content_type: Optional[str]
    ) -> str:
        """上传到S3"""
        extra_args = {}
        if content_type:
            extra_args['ContentType'] = content_type
        
        try:
            self.s3_client.upload_fileobj(
                file,
                self.bucket_name,
                object_key,
                ExtraArgs=extra_args
            )
            
            # 返回S3 URL
            if settings.S3_ENDPOINT_URL:
                return f"{settings.S3_ENDPOINT_URL}/{self.bucket_name}/{object_key}"
            else:
                return f"https://{self.bucket_name}.s3.{settings.S3_REGION}.amazonaws.com/{object_key}"
        
        except ClientError as e:
            raise Exception(f"上传文件失败: {str(e)}")
    
    def download_file(self, object_key: str) -> bytes:
        """
        下载文件
        
        参数:
            object_key: 对象键（路径）
        
        返回:
            文件内容
        """
        if self.use_local:
            return self._download_local(object_key)
        else:
            return self._download_s3(object_key)
    
    def _download_local(self, object_key: str) -> bytes:
        """从本地存储下载"""
        file_path = self.storage_path / object_key
        
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {object_key}")
        
        with open(file_path, 'rb') as f:
            return f.read()
    
    def _download_s3(self, object_key: str) -> bytes:
        """从S3下载"""
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=object_key
            )
            return response['Body'].read()
        
        except ClientError as e:
            raise Exception(f"下载文件失败: {str(e)}")
    
    def delete_file(self, object_key: str) -> bool:
        """
        删除文件
        
        参数:
            object_key: 对象键（路径）
        
        返回:
            是否删除成功
        """
        if self.use_local:
            return self._delete_local(object_key)
        else:
            return self._delete_s3(object_key)
    
    def _delete_local(self, object_key: str) -> bool:
        """从本地存储删除"""
        file_path = self.storage_path / object_key
        
        if file_path.exists():
            file_path.unlink()
            return True
        
        return False
    
    def _delete_s3(self, object_key: str) -> bool:
        """从S3删除"""
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=object_key
            )
            return True
        
        except ClientError:
            return False
    
    def file_exists(self, object_key: str) -> bool:
        """
        检查文件是否存在
        
        参数:
            object_key: 对象键（路径）
        
        返回:
            是否存在
        """
        if self.use_local:
            file_path = self.storage_path / object_key
            return file_path.exists()
        else:
            try:
                self.s3_client.head_object(
                    Bucket=self.bucket_name,
                    Key=object_key
                )
                return True
            except ClientError:
                return False


# 全局存储管理器实例
storage_manager = StorageManager()


def get_storage() -> StorageManager:
    """获取存储管理器的依赖注入函数"""
    return storage_manager
