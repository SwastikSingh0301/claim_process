from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "claim_process"
    environment: str = "local"

    # Database
    database_url: str = (
        "postgresql+psycopg://postgres:postgres@db:5432/claims"
    )

    # Rate limiting
    rate_limit_per_minute: int = 10

    # Logging
    log_level: str = "INFO"


settings = Settings()