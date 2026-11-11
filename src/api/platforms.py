from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import require_admin
from src.core.cache import delete_cache_pattern
from src.db.session import get_db
from src.models.catalog import Platform
from src.models.user import User
from src.schemas.catalog import PlatformCreate, PlatformRead, PlatformUpdate

router = APIRouter(
    prefix="/api/platforms",
    tags=["Streaming Platforms"],
)


async def _invalidate() -> None:
    await delete_cache_pattern("catalog:titles:*")
    await delete_cache_pattern("catalog:title:*")


@router.get("", response_model=list[PlatformRead])
async def list_platforms(
    include_inactive: bool = False,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(Platform)
        .order_by(Platform.name)
        .offset(offset)
        .limit(limit)
    )

    if not include_inactive:
        query = query.where(Platform.is_active.is_(True))

    return (await db.execute(query)).scalars().all()


@router.get("/{slug}", response_model=PlatformRead)
async def get_platform(
    slug: str,
    db: AsyncSession = Depends(get_db),
):
    platform = (
        await db.execute(
            select(Platform).where(
                Platform.slug == slug,
                Platform.is_active.is_(True),
            )
        )
    ).scalar_one_or_none()

    if platform is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            "Active platform not found",
        )

    return platform


@router.post(
    "",
    response_model=PlatformRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_platform(
    data: PlatformCreate,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    existing = (
        await db.execute(
            select(Platform).where(
                (Platform.name == data.name)
                | (Platform.slug == data.slug)
            )
        )
    ).scalar_one_or_none()

    if existing:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "Platform name or slug already exists",
        )

    values = data.model_dump()

    if values["website_url"] is not None:
        values["website_url"] = str(values["website_url"])

    platform = Platform(**values)
    db.add(platform)
    await db.commit()
    await db.refresh(platform)
    await _invalidate()
    return platform


@router.patch("/{slug}", response_model=PlatformRead)
async def update_platform(
    slug: str,
    data: PlatformUpdate,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    platform = (
        await db.execute(select(Platform).where(Platform.slug == slug))
    ).scalar_one_or_none()

    if platform is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Platform not found")

    changes = data.model_dump(exclude_unset=True, exclude_none=True)

    if changes:
        other = (
            await db.execute(
                select(Platform).where(
                    (
                        (Platform.name == changes.get("name", platform.name))
                        | (
                            Platform.slug
                            == changes.get("slug", platform.slug)
                        )
                    )
                    & (Platform.id != platform.id)
                )
            )
        ).scalar_one_or_none()

        if other:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                "Platform name or slug already exists",
            )

        if "website_url" in changes:
            changes["website_url"] = str(changes["website_url"])

        for field, value in changes.items():
            setattr(platform, field, value)

        await db.commit()
        await db.refresh(platform)
        await _invalidate()

    return platform


@router.delete("/{slug}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_platform(
    slug: str,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    platform = (
        await db.execute(select(Platform).where(Platform.slug == slug))
    ).scalar_one_or_none()

    if platform is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Platform not found")

    await db.delete(platform)
    await db.commit()
    await _invalidate()