"""Scheduled availability maintenance; provider clients can plug in later."""
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.cache import delete_cache, delete_cache_pattern
from src.models.catalog import AvailabilitySyncRun, TitleAvailability


class AvailabilitySyncService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def run(self) -> AvailabilitySyncRun:
        run = AvailabilitySyncRun(status="running")
        self.db.add(run)
        await self.db.flush()
        try:
            now = datetime.now(timezone.utc)
            result = await self.db.execute(
                select(TitleAvailability).where(
                    TitleAvailability.available_until.is_not(None),
                    TitleAvailability.available_until <= now,
                )
            )
            expired = list(result.scalars().all())
            title_ids = {record.title_id for record in expired}
            for record in expired:
                await self.db.delete(record)
            run.records_expired = len(expired)
            run.status = "completed"
            run.completed_at = now
            await self.db.commit()
            for title_id in title_ids:
                await delete_cache(f"catalog:title:{title_id}")
            if title_ids:
                await delete_cache_pattern("catalog:titles:*")
            return run
        except Exception as exc:
            await self.db.rollback()
            run.status = "failed"
            run.error_message = str(exc)[:500]
            run.completed_at = datetime.now(timezone.utc)
            self.db.add(run)
            await self.db.commit()
            raise
