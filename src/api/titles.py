import hashlib
import json

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import require_admin
from src.core.cache import delete_cache, delete_cache_pattern, get_cache, set_cache
from src.db.session import get_db
from src.models.catalog import ContentType
from src.models.user import User
from src.schemas.catalog import PageMeta, TitleCreate, TitlePage, TitleRead, TitleUpdate
from src.services.catalog_service import CatalogService

router = APIRouter(prefix="/api/titles", tags=["Titles"])


def _key(namespace: str, values: dict) -> str:
    raw = json.dumps(
        values,
        sort_keys=True,
        default=str,
        separators=(",", ":"),
    )
    return f"catalog:{namespace}:{hashlib.sha256(raw.encode()).hexdigest()}"


async def _invalidate(title_id: int | None = None) -> None:
    await delete_cache_pattern("catalog:titles:*")
    if title_id is not None:
        await delete_cache(f"catalog:title:{title_id}")


@router.get("", response_model=TitlePage)
async def list_titles(
    request: Request,
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    q: str | None = Query(default=None, min_length=1, max_length=100),
    content_type: ContentType | None = None,
    genre: str | None = Query(default=None, min_length=1, max_length=80),
    platform: str | None = Query(default=None, min_length=1, max_length=100),
    release_year: int | None = Query(default=None, ge=1888, le=2100),
    sort_by: str = Query(
        "created_at",
        pattern="^(name|release_year|created_at)$",
    ),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    db: AsyncSession = Depends(get_db),
):
    cache_key = _key("titles", dict(request.query_params))
    cached = await get_cache(cache_key)

    if cached is not None:
        return cached

    titles, total = await CatalogService(db).list_titles(
        offset=offset,
        limit=limit,
        query_text=q,
        content_type=content_type,
        genre_slug=genre,
        platform_slug=platform,
        release_year=release_year,
        published_only=True,
        sort_by=sort_by,
        descending=sort_order == "desc",
    )

    response = TitlePage(
        data=[TitleRead.model_validate(item) for item in titles],
        meta=PageMeta(offset=offset, limit=limit, total=total),
    )
    await set_cache(cache_key, response.model_dump(mode="json"))
    return response


@router.get("/{title_id}", response_model=TitleRead)
async def get_title(
    title_id: int,
    db: AsyncSession = Depends(get_db),
):
    cache_key = f"catalog:title:{title_id}"
    cached = await get_cache(cache_key)

    if cached is not None:
        return cached

    title = await CatalogService(db).get_title(
        title_id,
        published_only=True,
    )
    if title is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            "Published title not found",
        )

    response = TitleRead.model_validate(title)
    await set_cache(cache_key, response.model_dump(mode="json"))
    return response


@router.post(
    "",
    response_model=TitleRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_title(
    data: TitleCreate,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    try:
        title = await CatalogService(db).create_title(data)
    except ValueError as exc:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            str(exc),
        )

    await _invalidate()
    return title


@router.patch("/{title_id}", response_model=TitleRead)
async def update_title(
    title_id: int,
    data: TitleUpdate,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = CatalogService(db)
    title = await service.get_title(title_id)

    if title is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            "Title not found",
        )

    try:
        updated = await service.update_title(title, data)
    except ValueError as exc:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            str(exc),
        )

    await _invalidate(title_id)
    return updated


@router.delete(
    "/{title_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_title(
    title_id: int,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = CatalogService(db)
    title = await service.get_title(title_id)

    if title is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            "Title not found",
        )

    await service.delete_title(title)
    await _invalidate(title_id)