import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

TESTING = os.getenv("TESTING") == "TESTING_ENVIRONMENT"

if TESTING:
  DATABASE_URL = "sqlite:///./test.db"
else:
  DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if TESTING else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
