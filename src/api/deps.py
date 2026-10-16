"""Reusable FastAPI dependencies.

The rest of the project (e.g. CatalogService routes) should import from here:

    from src.api.deps import get_current_user, require_admin

    @router.post("/movies")
    async def add_movie(..., admin: User = Depends(require_admin)): ...
"""
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import ACCESS, decode_token
from src.db.session import get_db
from src.models.user import User, UserRole
from src.services.user_service import UserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

_credentials_error = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    try:
        payload = decode_token(token)
    except jwt.PyJWTError:
        raise _credentials_error
    if payload.get("type") != ACCESS:
        raise _credentials_error
    try:
        user_id = int(payload["sub"])
    except (KeyError, ValueError):
        raise _credentials_error

    user = await UserService(db).get_by_id(user_id)
    if user is None:
        raise _credentials_error
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    return user


def require_roles(*roles: UserRole):
    """Dependency factory for role-based access control."""

    async def checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
            )
        return user

    return checker


require_admin = require_roles(UserRole.ADMIN)
