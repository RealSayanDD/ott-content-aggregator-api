import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import (
    REFRESH,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from src.db.session import get_db
from src.schemas.token import RefreshRequest, Token
from src.schemas.user import UserCreate, UserRead
from src.services.user_service import UserService

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


def _tokens_for(user_id: int) -> Token:
    return Token(
        access_token=create_access_token(user_id),
        refresh_token=create_refresh_token(user_id),
    )


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    service = UserService(db)
    if await service.get_by_email(data.email):
        raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered")
    if await service.get_by_username(data.username):
        raise HTTPException(status.HTTP_409_CONFLICT, "Username already taken")
    # Public registration always creates a normal user, never an admin.
    return await service.create(data)


@router.post("/login", response_model=Token)
async def login(
    form: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    """`username` field accepts either the username or the email."""
    user = await UserService(db).authenticate(form.username, form.password)
    if user is None:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Inactive user")
    return _tokens_for(user.id)


@router.post("/refresh", response_model=Token)
async def refresh(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    error = HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid refresh token")
    try:
        payload = decode_token(body.refresh_token)
    except jwt.PyJWTError:
        raise error
    if payload.get("type") != REFRESH:
        raise error
    user = await UserService(db).get_by_id(int(payload["sub"]))
    if user is None or not user.is_active:
        raise error
    return _tokens_for(user.id)
