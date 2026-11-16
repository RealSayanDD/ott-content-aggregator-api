import asyncio

from src.core.database import engine
from src.models.base import Base

# Import models so SQLAlchemy registers their tables
from src.models.user import User
from src.models.title import Title
from src.models.genre import Genre
from src.models.platform import Platform
import src.models.association


async def create_tables():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    print("All database tables created successfully!")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(create_tables())