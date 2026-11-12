import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from src.models.user import UserRole


def _check_password_strength(value: str) -> str:
    if not re.search(r"[A-Za-z]", value) or not re.search(r"\d", value):
        raise ValueError("Password must contain at least one letter and one digit")
    return value


class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=32, pattern=r"^[A-Za-z0-9_.-]+$")
    password: str = Field(min_length=8, max_length=72)
    full_name: str | None = Field(default=None, max_length=100)

    _pw = field_validator("password")(_check_password_strength)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    username: str
    full_name: str | None
    role: UserRole
    is_active: bool
    created_at: datetime


class UserUpdate(BaseModel):
    """Fields a user may change on their own profile."""

    email: EmailStr | None = None
    username: str | None = Field(
        default=None, min_length=3, max_length=32, pattern=r"^[A-Za-z0-9_.-]+$"
    )
    full_name: str | None = Field(default=None, max_length=100)


class AdminUserUpdate(UserUpdate):
    """Extra fields only an admin may change."""

    role: UserRole | None = None
    is_active: bool | None = None


class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=72)

    _pw = field_validator("new_password")(_check_password_strength)
