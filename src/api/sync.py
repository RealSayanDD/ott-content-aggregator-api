"""Administrator controls for the safe mock provider-ingestion workflow."""
from fastapi import APIRouter, BackgroundTasks, Depends, status

from src.api.deps import require_admin
from src.db.session import AsyncSessionLocal
from src.models.user import User
from src.services.provider_sync_service import ProviderSyncService

router = APIRouter(prefix="/api/admin", tags=["Provider Sync"])


async def run_mock_provider_sync() -> None:
    """Open an independent session because BackgroundTasks outlives the request."""
    async with AsyncSessionLocal() as session:
        await ProviderSyncService(session).run()


@router.post("/provider-sync", status_code=status.HTTP_202_ACCEPTED)
async def start_provider_sync(
    background_tasks: BackgroundTasks,
    _: User = Depends(require_admin),
):
    background_tasks.add_task(run_mock_provider_sync)
    return {"detail": "Mock provider sync accepted"}
