from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.config.settings import settings
from app.dependencies import get_auth_service
from app.schemas.auth import Token, UserCreate, UserResponse
from app.services.auth_service import AuthService

router = APIRouter()

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service)
):
    user = auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=UserResponse)
async def register_user(
    user_in: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
):
    existing = auth_service.user_repository.get_by_email(user_in.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = auth_service.get_password_hash(user_in.password)
    user = auth_service.user_repository.create(
        email=user_in.email,
        hashed_password=hashed_password
    )
    return UserResponse(
        id=str(user.id),
        email=user.email,
        is_active=user.is_active
    )
