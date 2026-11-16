
import asyncio
from sqlalchemy import text
from src.core.database import engine


async def main():
    try:
        async with engine.connect() as connection:
            result = await connection.execute(text("SELECT 1"))

            print("PostgreSQL connected successfully!")
            print("Test result:", result.scalar())

    except Exception as error:
        print("Database connection failed!")
        print("Error:", error)

    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
