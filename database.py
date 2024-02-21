from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

engine = create_engine(
    "postgresql://postgres:nk168@localhost/Authentication", echo=True
)

Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)
