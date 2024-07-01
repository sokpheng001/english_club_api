
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base


# PostgreSQL connection details
SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://postgres:123@136.228.158.126:50000/english_club_db"

# Create an async engine
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True, future=True)

#  spefify table creation order


# Create a session class for async sessions
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Base class for declarative ORM models
Base = declarative_base()

# Dependency to get async DB session
async def get_db():
    async with SessionLocal() as session:
        yield session
