from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.api.deps import get_current_user
from src.db.session import get_db
from src.models.catalog import Title, WatchlistEntry
from src.models.user import User
from src.schemas.catalog import PageMeta, WatchlistEntryRead, WatchlistPage, WatchlistUpdate

router = APIRouter(prefix="/api/users/me", tags=["Watchlist"])


async def _page(user_id: int, offset: int, limit: int, favorites_only: bool, db: AsyncSession) -> WatchlistPage:
    filters = [WatchlistEntry.user_id == user_id]
    if favorites_only:
        filters.append(WatchlistEntry.is_favorite.is_(True))
    total = (await db.execute(select(func.count(WatchlistEntry.id)).where(*filters))).scalar_one()
    result = await db.execute(
        select(WatchlistEntry).where(*filters).options(
            selectinload(WatchlistEntry.title).selectinload(Title.genres),
            selectinload(WatchlistEntry.title).selectinload(Title.platforms),
        ).order_by(WatchlistEntry.created_at.desc(), WatchlistEntry.id.desc()).offset(offset).limit(limit)
    )
    return WatchlistPage(data=[WatchlistEntryRead.model_validate(row) for row in result.scalars().all()], meta=PageMeta(offset=offset, limit=limit, total=total))


@router.get("/watchlist", response_model=WatchlistPage)
async def list_watchlist(offset: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=100), user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await _page(user.id, offset, limit, False, db)


@router.get("/favorites", response_model=WatchlistPage)
async def list_favorites(offset: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=100), user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await _page(user.id, offset, limit, True, db)


@router.put("/watchlist/{title_id}", response_model=WatchlistEntryRead, status_code=status.HTTP_201_CREATED)
async def add_to_watchlist(title_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    title = await db.get(Title, title_id)
    if title is None or not title.is_published:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Published title not found")
    entry = (await db.execute(select(WatchlistEntry).where(WatchlistEntry.user_id == user.id, WatchlistEntry.title_id == title_id))).scalar_one_or_none()
    if entry is not None:
        return entry
    entry = WatchlistEntry(user_id=user.id, title_id=title_id)
    db.add(entry)
    await db.commit()
    result = await db.execute(select(WatchlistEntry).where(WatchlistEntry.id == entry.id).options(selectinload(WatchlistEntry.title).selectinload(Title.genres), selectinload(WatchlistEntry.title).selectinload(Title.platforms)))
    return result.scalar_one()


@router.patch("/watchlist/{title_id}", response_model=WatchlistEntryRead)
async def update_watchlist(title_id: int, data: WatchlistUpdate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    entry = (await db.execute(select(WatchlistEntry).where(WatchlistEntry.user_id == user.id, WatchlistEntry.title_id == title_id).options(selectinload(WatchlistEntry.title).selectinload(Title.genres), selectinload(WatchlistEntry.title).selectinload(Title.platforms)))).scalar_one_or_none()
    if entry is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Watchlist entry not found")
    entry.is_favorite = data.is_favorite
    await db.commit()
    await db.refresh(entry)
    return entry


@router.delete("/watchlist/{title_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_watchlist(title_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    entry = (await db.execute(select(WatchlistEntry).where(WatchlistEntry.user_id == user.id, WatchlistEntry.title_id == title_id))).scalar_one_or_none()
    if entry is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Watchlist entry not found")
    await db.delete(entry)
    await db.commit()
