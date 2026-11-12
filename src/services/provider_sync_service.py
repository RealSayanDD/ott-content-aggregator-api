"""Safe, deterministic provider-ingestion example.

Replace ``MockProviderClient`` with a licensed provider-feed adapter in a real
deployment.  It intentionally does not scrape provider pages or use cookies.
"""
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.catalog import ContentType, Genre, Platform, ProviderSyncRun, Title, TitleAvailability


class MockProviderClient:
    name = "mock-ott-feed"

    async def fetch_titles(self) -> list[dict]:
        # A deterministic sample makes the background workflow testable offline.
        return [{
            "name": "Example Arrival", "content_type": ContentType.MOVIE,
            "release_year": 2026, "synopsis": "A sample title supplied by the mock feed.",
            "genre": ("Science Fiction", "science-fiction"),
            "platform": ("Example Stream", "example-stream", "https://example.test"),
            "country_code": "IN", "url": "https://example.test/watch/example-arrival",
            "provider_content_id": "mock-example-arrival",
        }]


class ProviderSyncService:
    def __init__(self, db: AsyncSession, client: MockProviderClient | None = None):
        self.db = db
        self.client = client or MockProviderClient()

    async def run(self) -> ProviderSyncRun:
        run = ProviderSyncRun(provider_name=self.client.name, status="running")
        self.db.add(run)
        await self.db.flush()
        try:
            for item in await self.client.fetch_titles():
                genre = await self._genre(*item["genre"])
                platform = await self._platform(*item["platform"])
                title = (await self.db.execute(select(Title).where(Title.name == item["name"]))).scalar_one_or_none()
                if title is None:
                    title = Title(name=item["name"], content_type=item["content_type"], release_year=item["release_year"], synopsis=item["synopsis"], is_published=True, genres=[genre], platforms=[platform])
                    self.db.add(title)
                    await self.db.flush()
                    run.titles_created += 1
                else:
                    title.synopsis, title.release_year, title.is_published = item["synopsis"], item["release_year"], True
                    if genre not in title.genres:
                        title.genres.append(genre)
                    if platform not in title.platforms:
                        title.platforms.append(platform)
                    run.titles_updated += 1
                availability = (await self.db.execute(select(TitleAvailability).where(TitleAvailability.title_id == title.id, TitleAvailability.platform_id == platform.id, TitleAvailability.country_code == item["country_code"]))).scalar_one_or_none()
                if availability is None:
                    self.db.add(TitleAvailability(title_id=title.id, platform_id=platform.id, country_code=item["country_code"], provider_content_id=item["provider_content_id"], url=item["url"]))
                else:
                    availability.url, availability.provider_content_id = item["url"], item["provider_content_id"]
            run.status, run.completed_at = "completed", datetime.now(timezone.utc)
            await self.db.commit()
            return run
        except Exception as exc:
            await self.db.rollback()
            run.status, run.completed_at, run.error_message = "failed", datetime.now(timezone.utc), str(exc)[:500]
            self.db.add(run)
            await self.db.commit()
            raise

    async def _genre(self, name: str, slug: str) -> Genre:
        item = (await self.db.execute(select(Genre).where(Genre.slug == slug))).scalar_one_or_none()
        if item is None:
            item = Genre(name=name, slug=slug)
            self.db.add(item)
            await self.db.flush()
        return item

    async def _platform(self, name: str, slug: str, website_url: str) -> Platform:
        item = (await self.db.execute(select(Platform).where(Platform.slug == slug))).scalar_one_or_none()
        if item is None:
            item = Platform(name=name, slug=slug, website_url=website_url)
            self.db.add(item)
            await self.db.flush()
        return item
