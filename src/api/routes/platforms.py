
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from src.core.database import get_db
from src.models.platform import Platform

router = APIRouter(prefix="/platforms", tags=["Platforms"])


class PlatformCreate(BaseModel):
    name: str


@router.post("/")
async def create_platform(
    platform_data: PlatformCreate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Platform).where(
            Platform.name == platform_data.name
        )
    )
    existing_platform = result.scalar_one_or_none()

    if existing_platform:
        raise HTTPException(
            status_code=400,
            detail="Platform already exists"
        )

    new_platform = Platform(name=platform_data.name)

    db.add(new_platform)
    await db.commit()
    await db.refresh(new_platform)

    return new_platform


@router.get("/")
async def get_platforms(
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Platform))
    return result.scalars().all()
