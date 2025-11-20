"""
SQLAlchemy session maker for SQLite.
"""
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..settings import settings


def get_engine(db_path: str = settings.db_file):
    return create_engine(
        f"sqlite:///{db_path}",
        echo=False,
        future=True,
    )

def get_session(db_path: str = settings.db_file):
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    engine = get_engine(db_path)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)
