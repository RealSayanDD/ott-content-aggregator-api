from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.core.database import get_db
from src.models.title import Title
from src.models.genre import Genre
from src.models.platform import Platform
from src.models.association import title_genres, title_platforms

router = APIRouter(
    prefix="/titles",
    tags=["Movies and Shows"]
)


# Request schema: Create a movie/show
class TitleCreate(BaseModel):
    name: str
    description: str | None = None
    title_type: str
    release_year: int


# Request schema: Update a movie/show
class TitleUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    title_type: str | None = None
    release_year: int | None = None


# Response schema
class TitleResponse(BaseModel):
    id: int
    name: str
    description: str | None
    title_type: str
    release_year: int

    model_config = ConfigDict(from_attributes=True)
class TitleCreate(BaseModel):
    name: str
    description: str | None = None
    title_type: str
    release_year: int

# 1. CREATE MOVIE / SHOW
@router.post(
    "/",
    response_model=TitleResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_title(
    title_data: TitleCreate,
    db: AsyncSession = Depends(get_db)
):
    new_title = Title(**title_data.model_dump())

    db.add(new_title)
    await db.commit()
    await db.refresh(new_title)

    return new_title


# 2. GET ALL MOVIES / SHOWS
@router.get(
    "/",
    response_model=list[TitleResponse]
)
async def get_all_titles(
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Title))
    return result.scalars().all()

# SEARCH AND FILTER MOVIES / SHOWS

@router.get("/search", response_model=list[TitleResponse])
async def search_titles(
    name: str | None = None,
    title_type: str | None = None,
    release_year: int | None = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(Title)

    # Search by movie or show name
    if name:
        query = query.where(Title.name.ilike(f"%{name}%"))

    # Filter by movie or show type
    if title_type:
        query = query.where(Title.title_type == title_type)

    # Filter by release year
    if release_year:
        query = query.where(Title.release_year == release_year)

    result = await db.execute(query)

    return result.scalars().all()


# 3. GET MOVIE / SHOW BY ID
@router.get(
    "/{title_id}",
    response_model=TitleResponse
)
async def get_title(
    title_id: int,
    db: AsyncSession = Depends(get_db)
):
    title = await db.get(Title, title_id)

    if title is None:
        raise HTTPException(
            status_code=404,
            detail="Movie or show not found"
        )

    return title


# 4. UPDATE MOVIE / SHOW
@router.put(
    "/{title_id}",
    response_model=TitleResponse
)
async def update_title(
    title_id: int,
    title_data: TitleUpdate,
    db: AsyncSession = Depends(get_db)
):
    title = await db.get(Title, title_id)

    if title is None:
        raise HTTPException(
            status_code=404,
            detail="Movie or show not found"
        )

    update_data = title_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(title, key, value)

    await db.commit()
    await db.refresh(title)

    return title


# 5. DELETE MOVIE / SHOW
@router.delete(
    "/{title_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_title(
    title_id: int,
    db: AsyncSession = Depends(get_db)
):
    title = await db.get(Title, title_id)

    if title is None:
        raise HTTPException(
            status_code=404,
            detail="Movie or show not found"
        )
    
    await db.delete(title)
    await db.commit()

@router.post("/{title_id}/genres/{genre_id}")
async def add_genre_to_title(
    title_id: int,
    genre_id: int,
    db: AsyncSession = Depends(get_db)
):
    # Get title and load genres
    result = await db.execute(
        select(Title)
        .options(selectinload(Title.genres))
        .where(Title.id == title_id)
    )

    title = result.scalar_one_or_none()

    if not title:
        raise HTTPException(
            status_code=404,
            detail="Title not found"
        )

    # Get genre
    genre = await db.get(Genre, genre_id)

    if not genre:
        raise HTTPException(
            status_code=404,
            detail="Genre not found"
        )

    # Add genre
    if genre not in title.genres:
        title.genres.append(genre)

    await db.commit()

    return {
        "message": "Genre added successfully"
    }
      
@router.post("/{title_id}/platforms/{platform_id}")
async def add_platform_to_title(
    title_id: int,
    platform_id: int,
    db: AsyncSession = Depends(get_db)
):
    # Check whether the title exists
    title_result = await db.execute(
        select(Title).where(Title.id == title_id)
    )
    title = title_result.scalar_one_or_none()

    if not title:
        raise HTTPException(
            status_code=404,
            detail="Title not found"
        )

    # Check whether the platform exists
    platform_result = await db.execute(
        select(Platform).where(Platform.id == platform_id)
    )
    platform = platform_result.scalar_one_or_none()

    if not platform:
        raise HTTPException(
            status_code=404,
            detail="Platform not found"
        )

    # Check whether the relationship already exists
    existing = await db.execute(
        select(title_platforms).where(
            title_platforms.c.title_id == title_id,
            title_platforms.c.platform_id == platform_id
        )
    )

    if existing.first():
        return {"message": "Platform already added to title"}

    # Insert the relationship
    await db.execute(
        insert(title_platforms).values(
            title_id=title_id,
            platform_id=platform_id
        )
    )

    await db.commit()

    return {"message": "Platform added to title successfully"}