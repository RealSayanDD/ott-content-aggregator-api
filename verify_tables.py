
import asyncio
from sqlalchemy import inspect
from src.core.database import engine

async def main():
    async with engine.connect() as connection:

        def get_tables(sync_connection):
            inspector = inspect(sync_connection)
            return inspector.get_table_names()

        tables = await connection.run_sync(get_tables)

        print("\nPostgreSQL Tables:")

        for table in tables:
            print(" -", table)

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
