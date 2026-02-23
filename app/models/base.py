"""基础模型类"""
from datetime import datetime
from sqlalchemy import Column, DateTime, String, TypeDecorator
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
import uuid

from app.core.database import Base


class GUID(TypeDecorator):
    """兼容SQLite和PostgreSQL的UUID类型"""
    impl = String
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        else:
            return dialect.type_descriptor(String(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return value
        else:
            if isinstance(value, uuid.UUID):
                return str(value)
            return value

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, uuid.UUID):
            return value
        return uuid.UUID(value)


class BaseModel(Base):
    """所有模型的基类"""
    
    __abstract__ = True
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
