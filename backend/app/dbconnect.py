from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

# NOTE: for simplicity purposes, user and password are provided
# but in practice, this should be stored as an ENV variable for security reasons
DATABASE_URL = "postgresql://titanic:titanic@titanicdb:5432/titanicdb"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    """Dependency for database sessions"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
