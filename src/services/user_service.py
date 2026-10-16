from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import hash_password, verify_password
from src.models.user import User, UserRole
from src.schemas.user import AdminUserUpdate, UserCreate, UserUpdate


class UserService:
    """All user-related database logic lives here, routes stay thin."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: int) -> User | None:
        return await self.db.get(User, user_id)

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(
            select(User).where(func.lower(User.email) == email.lower())
        )
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        result = await self.db.execute(
            select(User).where(func.lower(User.username) == username.lower())
        )
        return result.scalar_one_or_none()

    async def list_users(self, skip: int = 0, limit: int = 50) -> list[User]:
        result = await self.db.execute(
            select(User).order_by(User.id).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def create(self, data: UserCreate, role: UserRole = UserRole.USER) -> User:
        user = User(
            email=data.email.lower(),
            username=data.username,
            full_name=data.full_name,
            hashed_password=hash_password(data.password),
            role=role,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def authenticate(self, identifier: str, password: str) -> User | None:
        """identifier can be an email or a username."""
        result = await self.db.execute(
            select(User).where(
                or_(
                    func.lower(User.email) == identifier.lower(),
                    func.lower(User.username) == identifier.lower(),
                )
            )
        )
        user = result.scalar_one_or_none()
        if user is None or not verify_password(password, user.hashed_password):
            return None
        return user

    async def update(self, user: User, data: UserUpdate | AdminUserUpdate) -> User:
        changes = data.model_dump(exclude_unset=True, exclude_none=True)
        if "email" in changes:
            changes["email"] = changes["email"].lower()
        for field, value in changes.items():
            setattr(user, field, value)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def change_password(self, user: User, new_password: str) -> None:
        user.hashed_password = hash_password(new_password)
        await self.db.commit()

    async def delete(self, user: User) -> None:
        await self.db.delete(user)
        await self.db.commit()
