import os
from collections.abc import Generator

import duckdb
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from peleton_api.core.config import settings

Base = declarative_base()

# Lazy-loaded singletons to prevent import-time crashes
_engine = None
_session_local: sessionmaker | None = None


def get_engine():
    """Lazily creates and returns the SQLAlchemy engine."""
    global _engine
    if _engine is None:
        _engine = create_engine(
            settings.database_url,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
            connect_args={"connect_timeout": 10},
        )
    return _engine


def get_session_local() -> sessionmaker:
    """Lazily creates and returns the sessionmaker."""
    global _session_local
    if _session_local is None:
        _session_local = sessionmaker(
            autocommit=False, 
            autoflush=False, 
            bind=get_engine()
        )
    return _session_local


def get_db() -> Generator[Session, None, None]:
    """Dependency injection for PostgreSQL database sessions."""
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_duckdb_connection() -> duckdb.DuckDBPyConnection:
    """Opens a safe DuckDB connection (local file or MotherDuck cloud)."""
    db_path = settings.duckdb_path
    
    # If using MotherDuck cloud, connect directly without checking file existence
    if db_path.startswith("md:"):
        return duckdb.connect(db_path, read_only=True)
        
    # Otherwise, verify local file exists
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"DuckDB database file not found at {db_path}")
    
    return duckdb.connect(db_path, read_only=True)