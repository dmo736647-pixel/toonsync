"""认证服务"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.config import settings
from app.models.user import User, SubscriptionTier


# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthenticationService:
    """认证服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """生成密码哈希"""
        return pwd_context.hash(password)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """创建JWT访问令牌"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[dict]:
        """验证JWT令牌"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except JWTError:
            return None
    
    def register_user(self, email: str, password: str) -> User:
        """
        注册新用户
        
        参数:
            email: 用户邮箱
            password: 用户密码
        
        返回:
            User: 创建的用户对象
        
        异常:
            ValueError: 邮箱已存在或无效
        """
        # 检查邮箱是否已存在
        existing_user = self.db.query(User).filter(User.email == email).first()
        if existing_user:
            raise ValueError("邮箱已被注册")
        
        # 创建新用户
        password_hash = self.get_password_hash(password)
        user = User(
            email=email,
            password_hash=password_hash,
            subscription_tier=SubscriptionTier.FREE,
            remaining_quota_minutes=5.0
        )
        
        try:
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user
        except IntegrityError:
            self.db.rollback()
            raise ValueError("邮箱已被注册")
    
    def login(self, email: str, password: str) -> tuple[User, str]:
        """
        用户登录
        
        参数:
            email: 用户邮箱
            password: 用户密码
        
        返回:
            tuple[User, str]: 用户对象和JWT令牌
        
        异常:
            ValueError: 凭证无效
        """
        # 查找用户
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            raise ValueError("邮箱或密码错误")
        
        # 验证密码
        if not self.verify_password(password, user.password_hash):
            raise ValueError("邮箱或密码错误")
        
        # 生成JWT令牌
        access_token = self.create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )
        
        return user, access_token
    
    def get_current_user(self, token: str) -> Optional[User]:
        """
        根据JWT令牌获取当前用户
        
        参数:
            token: JWT令牌
        
        返回:
            Optional[User]: 用户对象，如果令牌无效则返回None
        """
        payload = self.verify_token(token)
        if not payload:
            return None
        
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        user = self.db.query(User).filter(User.id == user_id).first()
        return user
