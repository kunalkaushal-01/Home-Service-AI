import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


load_dotenv()


DB_URL = os.getenv("DB_URL")

if not DB_URL:
    raise ValueError("❌ DB_URL is not set in the .env file")

# SQLAlchemy engine
engine = create_engine(DB_URL, pool_pre_ping=True, future=True)

# SessionLocal for DB operations
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# Base class for models (needed for Alembic migrations)
Base = declarative_base()


# Dependency function for FastAPI (optional, safe to keep for reuse)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
