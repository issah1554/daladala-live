from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from databases import Database
from volta_api.core.config import DATABASE_URL

# SQLAlchemy Base
Base = declarative_base()

# Database connection for async
database = Database(DATABASE_URL)

# Optional: synchronous engine if needed by Alembic
engine = create_engine(DATABASE_URL)
