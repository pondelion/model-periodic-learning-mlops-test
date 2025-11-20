"""
Base class for SQLAlchemy ORM models.
"""

from sqlalchemy.orm import declarative_base

Base = declarative_base()


def init_db(engine):
    Base.metadata.create_all(bind=engine)
