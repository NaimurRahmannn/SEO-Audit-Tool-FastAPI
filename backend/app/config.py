from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables / .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DATABASE_URL: str = "postgresql+psycopg://seo:seo@localhost:5432/seo_audit"
    PSI_API_KEY: str = ""
    FRONTEND_ORIGIN: str = "http://localhost:3000"


settings = Settings()
