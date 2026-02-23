"""认证API端点"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.auth import AuthenticationService
from app.api.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    UserResponse,
    UserLoginResponse,
)


router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: UserRegisterRequest,
    db: Session = Depends(get_db)
):
    """
    用户注册
    
    创建新用户账户，默认为免费版订阅，包含5分钟免费额度
    """
    auth_service = AuthenticationService(db)
    
    try:
        user = auth_service.register_user(request.email, request.password)
        return UserResponse.model_validate(user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=UserLoginResponse)
async def login(
    request: UserLoginRequest,
    db: Session = Depends(get_db)
):
    """
    用户登录
    
    验证用户凭证并返回JWT访问令牌
    """
    auth_service = AuthenticationService(db)
    
    try:
        user, access_token = auth_service.login(request.email, request.password)
        return UserLoginResponse(
            user=UserResponse.model_validate(user),
            access_token=access_token,
            token_type="bearer"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户信息
    
    需要有效的JWT令牌
    """
    return UserResponse.model_validate(current_user)
