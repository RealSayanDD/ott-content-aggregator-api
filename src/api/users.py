from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_current_user, require_admin
from src.core.security import verify_password
from src.db.session import get_db
from src.models.user import User, UserRole
from src.schemas.user import AdminUserUpdate, PasswordChange, UserRead, UserUpdate
from src.services.user_service import UserService

router = APIRouter(prefix="/api/users", tags=["Users"])


async def _ensure_unique(service: UserService, data: UserUpdate, current: User) -> None:
    if data.email:
        other = await service.get_by_email(data.email)
        if other and other.id != current.id:
            raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered")
    if data.username:
        other = await service.get_by_username(data.username)
        if other and other.id != current.id:
            raise HTTPException(status.HTTP_409_CONFLICT, "Username already taken")


# ---- Current user ---------------------------------------------------------
@router.get("/me", response_model=UserRead)
async def read_me(user: User = Depends(get_current_user)):
    return user


@router.patch("/me", response_model=UserRead)
async def update_me(
    data: UserUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    await _ensure_unique(service, data, user)
    return await service.update(user, data)


@router.post("/me/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    data: PasswordChange,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not verify_password(data.current_password, user.hashed_password):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Current password is incorrect")
    await UserService(db).change_password(user, data.new_password)


# ---- Admin only -----------------------------------------------------------
@router.get("", response_model=list[UserRead])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    return await UserService(db).list_users(skip, limit)


@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: int, _: User = Depends(require_admin), db: AsyncSession = Depends(get_db)
):
    user = await UserService(db).get_by_id(user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    return user


@router.patch("/{user_id}", response_model=UserRead)
async def admin_update_user(
    user_id: int,
    data: AdminUserUpdate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    user = await service.get_by_id(user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    if user.id == admin.id and (data.role == UserRole.USER or data.is_active is False):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "Admins cannot demote or deactivate themselves"
        )
    await _ensure_unique(service, data, user)
    return await service.update(user, data)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    user = await service.get_by_id(user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    if user.id == admin.id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Admins cannot delete themselves")
    await service.delete(user)
