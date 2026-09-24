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
    redis_url: str = "redis://redis:6379/0"
    job_max_attempts: int = 5
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from_email: str = ""
    smtp_use_tls: bool = True
    media_root: str = "/data/media"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
