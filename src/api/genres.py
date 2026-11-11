from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import require_admin
from src.core.cache import delete_cache_pattern
from src.db.session import get_db
from src.models.catalog import Genre
from src.models.user import User
from src.schemas.catalog import GenreCreate, GenreRead, GenreUpdate

router = APIRouter(prefix="/api/genres", tags=["Genres"])


async def _invalidate() -> None:
    await delete_cache_pattern("catalog:titles:*")
    await delete_cache_pattern("catalog:title:*")


@router.get("", response_model=list[GenreRead])
async def list_genres(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Genre).order_by(Genre.name).offset(offset).limit(limit)
    )
    return result.scalars().all()


@router.get("/{slug}", response_model=GenreRead)
async def get_genre(
    slug: str,
    db: AsyncSession = Depends(get_db),
):
    genre = (
        await db.execute(select(Genre).where(Genre.slug == slug))
    ).scalar_one_or_none()

    if genre is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Genre not found")

    return genre


@router.post(
    "",
    response_model=GenreRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_genre(
    data: GenreCreate,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    existing = (
        await db.execute(
            select(Genre).where(
                (Genre.name == data.name) | (Genre.slug == data.slug)
            )
        )
    ).scalar_one_or_none()

    if existing:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "Genre name or slug already exists",
        )

    genre = Genre(**data.model_dump())
    db.add(genre)
    await db.commit()
    await db.refresh(genre)
    await _invalidate()
    return genre


@router.patch("/{slug}", response_model=GenreRead)
async def update_genre(
    slug: str,
    data: GenreUpdate,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    genre = (
        await db.execute(select(Genre).where(Genre.slug == slug))
    ).scalar_one_or_none()

    if genre is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Genre not found")

    changes = data.model_dump(exclude_unset=True, exclude_none=True)

    if changes:
        other = (
            await db.execute(
                select(Genre).where(
                    (
                        (Genre.name == changes.get("name", genre.name))
                        | (Genre.slug == changes.get("slug", genre.slug))
                    )
                    & (Genre.id != genre.id)
                )
            )
        ).scalar_one_or_none()

        if other:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                "Genre name or slug already exists",
            )

        for field, value in changes.items():
            setattr(genre, field, value)

        await db.commit()
        await db.refresh(genre)
        await _invalidate()

    return genre


@router.delete("/{slug}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_genre(
    slug: str,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    genre = (
        await db.execute(select(Genre).where(Genre.slug == slug))
    ).scalar_one_or_none()

    if genre is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Genre not found")

    await db.delete(genre)
    await db.commit()
    await _invalidate()