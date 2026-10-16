from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "OTT Content Aggregator API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # --- Security / JWT (auth module) ---
    SECRET_KEY: str = "dev-only-secret-change-me-in-production-0123456789"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # --- Database (an async driver is required) ---
    # PostgreSQL: postgresql+asyncpg://user:password@localhost:5432/ott
    DATABASE_URL: str = "sqlite+aiosqlite:///./app.db"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
