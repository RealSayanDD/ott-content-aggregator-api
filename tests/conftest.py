import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from src.core.security import hash_password
from src.db.base import Base
from src.db.session import get_db
from src.main import app
from src.models.user import User, UserRole


@pytest_asyncio.fixture
async def session_factory():
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield async_sessionmaker(engine, expire_on_commit=False)
    await engine.dispose()


@pytest_asyncio.fixture
async def client(session_factory):
    async def override_get_db():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c
    app.dependency_overrides.clear()


async def register(client: AsyncClient, email="a@example.com", username="alice", password="secret123"):
    return await client.post(
        "/api/auth/register",
        json={"email": email, "username": username, "password": password},
    )


async def login(client: AsyncClient, identifier="alice", password="secret123"):
    return await client.post(
        "/api/auth/login", data={"username": identifier, "password": password}
    )


def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def user_token(client):
    await register(client)
    return (await login(client)).json()["access_token"]


@pytest_asyncio.fixture
async def admin_token(client, session_factory):
    async with session_factory() as db:  # type: AsyncSession
        db.add(
            User(
                email="admin@example.com",
                username="admin",
                hashed_password=hash_password("adminpass1"),
                role=UserRole.ADMIN,
            )
        )
        await db.commit()
    return (await login(client, "admin", "adminpass1")).json()["access_token"]
