
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from src.core.database import get_db
from src.models.genre import Genre

router = APIRouter(prefix="/genres", tags=["Genres"])


class GenreCreate(BaseModel):
    name: str


@router.post("/")
async def create_genre(
    genre_data: GenreCreate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Genre).where(Genre.name == genre_data.name)
    )
    existing_genre = result.scalar_one_or_none()

    if existing_genre:
        raise HTTPException(
            status_code=400,
            detail="Genre already exists"
        )

    new_genre = Genre(name=genre_data.name)

    db.add(new_genre)
    await db.commit()
    await db.refresh(new_genre)

    return new_genre


@router.get("/")
async def get_genres(
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Genre))
    return result.scalars().all()
