from sqlalchemy import create_engine

from app.core.config import get_settings


def create_db_engine():
    settings = get_settings()
    return create_engine(
        settings.database_url,
        pool_pre_ping=True,
        future=True,
    )
