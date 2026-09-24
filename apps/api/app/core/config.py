from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


def _development_secret() -> str:
    import secrets

    return secrets.token_urlsafe(48)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "eFootball Marketplace API"
    environment: str = "development"
    database_url: str = (
        "postgresql+psycopg://efootball:efootball@localhost:5432/efootball"
    )
    cors_origins: str = "http://localhost:5173"
    auth_secret_key: str = _development_secret()
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 14
    payment_webhook_secret: str = ""

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
