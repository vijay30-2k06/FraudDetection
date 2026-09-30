import os
from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker


DATABASE_PATH = Path(__file__).resolve().parent / "fraud_detection.db"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATABASE_PATH.as_posix()}")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Yield one database session and always close it after the request."""
    database = SessionLocal()
    try:
        yield database
    finally:
        database.close()