from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.api.deps import require_admin
from src.core.cache import delete_cache, delete_cache_pattern
from src.db.session import get_db
from src.models.catalog import Platform, Title, TitleAvailability
from src.models.user import User
from src.schemas.catalog import AvailabilityCreate, AvailabilityRead

router = APIRouter(prefix="/api/titles", tags=["Provider Availability"])


async def _invalidate(title_id: int) -> None:
    await delete_cache(f"catalog:title:{title_id}")
    await delete_cache_pattern("catalog:titles:*")


@router.get("/{title_id}/availability", response_model=list[AvailabilityRead])
async def list_availability(title_id: int, country: str | None = Query(default=None, min_length=2, max_length=2), db: AsyncSession = Depends(get_db)):
    title = await db.get(Title, title_id)
    if title is None or not title.is_published:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Published title not found")
    now = datetime.now(timezone.utc)
    filters = [TitleAvailability.title_id == title_id]
    if country:
        filters.append(TitleAvailability.country_code == country.upper())
    filters.extend([ (TitleAvailability.available_from.is_(None)) | (TitleAvailability.available_from <= now), (TitleAvailability.available_until.is_(None)) | (TitleAvailability.available_until > now) ])
    result = await db.execute(select(TitleAvailability).where(and_(*filters)).options(selectinload(TitleAvailability.platform)).order_by(TitleAvailability.country_code, TitleAvailability.id))
    return result.scalars().all()


@router.post("/{title_id}/availability", response_model=AvailabilityRead, status_code=status.HTTP_201_CREATED)
async def create_availability(title_id: int, data: AvailabilityCreate, _: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    title = await db.get(Title, title_id)
    if title is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Title not found")
    if await db.get(Platform, data.platform_id) is None:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Platform not found")
    existing = (await db.execute(select(TitleAvailability).where(TitleAvailability.title_id == title_id, TitleAvailability.platform_id == data.platform_id, TitleAvailability.country_code == data.country_code))).scalar_one_or_none()
    if existing:
        raise HTTPException(status.HTTP_409_CONFLICT, "Availability already exists for this title, platform, and country")
    values = data.model_dump()
    values["url"] = str(values["url"])
    availability = TitleAvailability(title_id=title_id, **values)
    db.add(availability)
    await db.commit()
    result = await db.execute(select(TitleAvailability).where(TitleAvailability.id == availability.id).options(selectinload(TitleAvailability.platform)))
    await _invalidate(title_id)
    return result.scalar_one()


@router.delete("/{title_id}/availability/{availability_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_availability(title_id: int, availability_id: int, _: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    availability = (await db.execute(select(TitleAvailability).where(TitleAvailability.id == availability_id, TitleAvailability.title_id == title_id))).scalar_one_or_none()
    if availability is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Availability not found")
    await db.delete(availability)
    await db.commit()
    await _invalidate(title_id)
