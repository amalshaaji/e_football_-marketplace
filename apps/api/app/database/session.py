from collections.abc import Generator

from sqlalchemy.orm import Session, sessionmaker

from app.database.connection import create_db_engine

engine = create_db_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
