from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import settings

Base = declarative_base()


def _build_engine(database_url: str):
    if database_url.startswith("sqlite"):
        return create_engine(database_url, connect_args={"check_same_thread": False})
    return create_engine(database_url, pool_pre_ping=True)


engine = _build_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def initialize_database():
    global engine, SessionLocal

    try:
        Base.metadata.create_all(bind=engine)
    except OperationalError:
        if settings.database_url.startswith("mysql"):
            fallback_url = "sqlite:///./aivoa_complaints.db"
            engine = _build_engine(fallback_url)
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            Base.metadata.create_all(bind=engine)
        else:
            raise


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
