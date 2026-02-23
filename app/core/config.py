"""应用配置管理"""
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置"""
    
    # 项目基本信息
    PROJECT_NAME: str = "AI Webtoon Video Maker"
    VERSION: str = "0.1.0"
    API_V1_PREFIX: str = "/api/v1"
    
    # 全球化配置
    DEFAULT_LANGUAGE: str = "en"  # 默认英文
    SUPPORTED_LANGUAGES: List[str] = ["en", "zh", "ja", "ko", "es", "fr", "de"]
    
    # CORS配置
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000", "http://localhost:5173", "http://localhost:5174"]
    
    # 数据库配置（支持直接使用DATABASE_URL或分开配置）
    DATABASE_URL: Optional[str] = None  # 优先使用此URL（Supabase/Railway提供）
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "short_drama_db"
    
    @property
    def database_url(self) -> str:
        """获取数据库连接URL"""
        # 如果提供了完整的DATABASE_URL，直接使用
        if self.DATABASE_URL:
            return self.DATABASE_URL
        
        # 开发环境：如果USE_LOCAL_STORAGE为True，使用SQLite
        if self.USE_LOCAL_STORAGE and self.ENVIRONMENT == "development":
            return "sqlite:///./test.db"
        
        # 否则从分开的配置构建PostgreSQL连接
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
    
    # Redis配置（支持直接使用REDIS_URL或分开配置）
    REDIS_URL: Optional[str] = None  # 优先使用此URL（Upstash/Railway提供）
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""
    USE_REDIS: bool = True # 是否使用Redis，默认True，开发环境可设置为False
    
    @property
    def redis_url(self) -> str:
        """获取Redis连接URL"""
        # 如果提供了完整的REDIS_URL，直接使用
        if self.REDIS_URL:
            return self.REDIS_URL
        # 否则从分开的配置构建
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    # 存储配置（支持Supabase Storage或S3）
    STORAGE_TYPE: str = "local"  # local, supabase, s3
    
    # Supabase配置
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None
    SUPABASE_BUCKET: str = "short-drama-assets"
    
    # S3/对象存储配置
    S3_ENDPOINT_URL: str = ""  # 留空使用AWS S3，或设置为MinIO等本地存储
    S3_ACCESS_KEY: str = ""
    S3_SECRET_KEY: str = ""
    S3_BUCKET_NAME: str = "short-drama-platform"
    S3_REGION: str = "us-east-1"
    USE_LOCAL_STORAGE: bool = True  # 开发环境使用本地存储
    LOCAL_STORAGE_PATH: str = "./storage"
    
    # JWT认证配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7天
    
    # AI模型API配置
    # Replicate API（推荐用于生产环境）
    REPLICATE_API_TOKEN: Optional[str] = None
    
    # OpenAI API（用于GPT功能和多语言支持）
    OPENAI_API_KEY: Optional[str] = None
    
    # ElevenLabs API（英文TTS，全球化语音合成）
    ELEVENLABS_API_KEY: Optional[str] = None
    
    # Stability AI API（图像生成）
    STABILITY_API_KEY: Optional[str] = None
    
    # 多语言TTS配置
    TTS_PROVIDERS: dict = {
        "en": "elevenlabs",  # 英文使用ElevenLabs
        "zh": "azure",       # 中文使用Azure
        "ja": "azure",       # 日文使用Azure
        "ko": "azure",       # 韩文使用Azure
        "es": "elevenlabs",  # 西班牙文使用ElevenLabs
        "fr": "elevenlabs",  # 法文使用ElevenLabs
        "de": "elevenlabs",  # 德文使用ElevenLabs
    }
    
    # Azure TTS配置
    AZURE_SPEECH_KEY: Optional[str] = None
    AZURE_SPEECH_REGION: str = "eastasia"
    
    # 支付配置
    # Stripe
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_PUBLISHABLE_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    
    # PayPal（可选）
    PAYPAL_CLIENT_ID: Optional[str] = None
    PAYPAL_CLIENT_SECRET: Optional[str] = None
    PAYPAL_MODE: str = "sandbox"  # sandbox 或 live
    
    # 环境配置
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Railway/Cloudflare特定配置
    PORT: int = 8000  # Railway会自动设置PORT环境变量
    
    # 云端部署时的CORS配置
    @property
    def cors_origins(self) -> List[str]:
        """动态CORS配置"""
        if self.ENVIRONMENT == "production":
            # 生产环境：只允许你的域名
            return [
                "https://your-domain.pages.dev",  # Cloudflare Pages默认域名
                "https://your-custom-domain.com",  # 你的自定义域名
            ]
        else:
            # 开发环境：允许本地开发
            return self.ALLOWED_ORIGINS
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()
