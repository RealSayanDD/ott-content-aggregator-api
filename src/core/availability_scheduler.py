import asyncio
import logging

from src.core.config import settings
from src.db.session import AsyncSessionLocal
from src.services.availability_sync_service import AvailabilitySyncService

logger = logging.getLogger(__name__)


async def run_availability_scheduler(stop_event: asyncio.Event) -> None:
    """Run maintenance repeatedly until FastAPI shuts down."""
    interval = max(1, settings.AVAILABILITY_SYNC_INTERVAL_MINUTES) * 60
    while not stop_event.is_set():
        try:
            async with AsyncSessionLocal() as session:
                run = await AvailabilitySyncService(session).run()
                logger.info("Availability maintenance run %s expired %s records", run.id, run.records_expired)
        except Exception:
            logger.exception("Availability maintenance failed")
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=interval)
        except TimeoutError:
            continue
