from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

engine = create_engine(
    "postgresql://postgres:nk168@localhost/Authentication", echo=True
)

Base = declarative_base()

# Bind the engine to the Base class
Base.metadata.bind = engine

SessionLocal = sessionmaker(bind=engine)
