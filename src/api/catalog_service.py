from collections.abc import Sequence

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.catalog import ContentType, Genre, Platform, Title
from src.schemas.catalog import TitleCreate, TitleUpdate


class CatalogService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_title(self, title_id: int, *, published_only: bool = False) -> Title | None:
        query = select(Title).where(Title.id == title_id)
        if published_only:
            query = query.where(Title.is_published.is_(True))
        result = await self.db.execute(query.options(selectinload(Title.genres), selectinload(Title.platforms)))
        return result.scalar_one_or_none()

    async def list_titles(
        self,
        *,
        offset: int,
        limit: int,
        query_text: str | None,
        content_type: ContentType | None,
        genre_slug: str | None,
        platform_slug: str | None,
        release_year: int | None,
        published_only: bool,
        sort_by: str,
        descending: bool,
    ) -> tuple[Sequence[Title], int]:
        filters = []
        if query_text:
            filters.append(func.lower(Title.name).contains(query_text.lower()))
        if content_type:
            filters.append(Title.content_type == content_type)
        if genre_slug:
            filters.append(Title.genres.any(Genre.slug == genre_slug))
        if platform_slug:
            filters.append(Title.platforms.any(Platform.slug == platform_slug))
        if release_year:
            filters.append(Title.release_year == release_year)
        if published_only:
            filters.append(Title.is_published.is_(True))

        sortable = {"name": Title.name, "release_year": Title.release_year, "created_at": Title.created_at}
        ordering = sortable[sort_by].desc() if descending else sortable[sort_by].asc()
        total = (await self.db.execute(select(func.count(Title.id)).where(*filters))).scalar_one()
        result = await self.db.execute(
            select(Title)
            .where(*filters)
            .options(selectinload(Title.genres), selectinload(Title.platforms))
            .order_by(ordering, Title.id)
            .offset(offset)
            .limit(limit)
        )
        return result.scalars().all(), total

    async def _related(self, genre_ids: list[int], platform_ids: list[int]) -> tuple[list[Genre], list[Platform]]:
        genres = await self._get_many(Genre, genre_ids)
        platforms = await self._get_many(Platform, platform_ids)
        if len(genres) != len(set(genre_ids)):
            raise ValueError("One or more genre_ids do not exist")
        if len(platforms) != len(set(platform_ids)):
            raise ValueError("One or more platform_ids do not exist")
        return genres, platforms

    async def _get_many(self, model: type[Genre] | type[Platform], ids: list[int]):
        if not ids:
            return []
        result = await self.db.execute(select(model).where(model.id.in_(set(ids))))
        return list(result.scalars().all())

    async def create_title(self, data: TitleCreate) -> Title:
        genres, platforms = await self._related(data.genre_ids, data.platform_ids)
        values = data.model_dump(exclude={"genre_ids", "platform_ids"})
        title = Title(**values, genres=genres, platforms=platforms)
        self.db.add(title)
        await self.db.commit()
        return await self.get_title(title.id)  # type: ignore[return-value]

    async def update_title(self, title: Title, data: TitleUpdate) -> Title:
        changes = data.model_dump(exclude_unset=True, exclude_none=True)
        genre_ids = changes.pop("genre_ids", None)
        platform_ids = changes.pop("platform_ids", None)
        if genre_ids is not None or platform_ids is not None:
            genres, platforms = await self._related(
                genre_ids if genre_ids is not None else [genre.id for genre in title.genres],
                platform_ids if platform_ids is not None else [platform.id for platform in title.platforms],
            )
            title.genres, title.platforms = genres, platforms
        for field, value in changes.items():
            setattr(title, field, value)
        await self.db.commit()
        return await self.get_title(title.id)  # type: ignore[return-value]

    async def delete_title(self, title: Title) -> None:
        await self.db.delete(title)
        await self.db.commit()
