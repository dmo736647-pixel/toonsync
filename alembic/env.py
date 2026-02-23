"""Alembic环境配置"""
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os

# 导入应用配置和模型
from app.core.config import settings
from app.core.database import Base
from app.models import *  # noqa: F401, F403

# Alembic Config对象
config = context.config

# 设置数据库URL - 确保是字符串
database_url = settings.DATABASE_URL or os.getenv("DATABASE_URL")
if database_url:
    config.set_main_option("sqlalchemy.url", database_url)

# 配置日志
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 目标元数据
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """在'离线'模式下运行迁移"""
    url = config.get_main_option("sqlalchemy.url")
    if not url:
        print("WARNING: DATABASE_URL not set, skipping migrations")
        return
        
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """在'在线'模式下运行迁移"""
    url = config.get_main_option("sqlalchemy.url")
    if not url:
        print("WARNING: DATABASE_URL not set, skipping migrations")
        return
        
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
