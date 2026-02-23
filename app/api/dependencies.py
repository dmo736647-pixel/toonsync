"""API依赖项"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.auth import AuthenticationService
from app.models.user import User


security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    获取当前认证用户
    
    从JWT令牌中提取用户信息
    """
    token = credentials.credentials
    auth_service = AuthenticationService(db)
    
    user = auth_service.get_current_user(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭证",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_current_user_ws(
    token: str,
    db: Session = Depends(get_db)
) -> User:
    """
    获取当前认证用户（WebSocket版本）
    
    从JWT令牌中提取用户信息
    """
    auth_service = AuthenticationService(db)
    
    user = auth_service.get_current_user(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭证",
        )
    
    return user
