from sqlalchemy import String, Integer, Boolean, Column, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from database.db_config import Base, engine
import uuid
from datetime import datetime

# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker, declarative_base

# engine = create_engine(
#     "postgresql://postgres:nk168@localhost/Authentication", echo=True
# )

# Base = declarative_base()

# # Bind the engine to the Base class
# Base.metadata.bind = engine

# SessionLocal = sessionmaker(bind=engine)


def uuid_generator():
    return str(uuid.uuid4())


def create_tables():
    Base.metadata.create_all(engine)


class User(Base):
    __tablename__ = "users"
    id = Column(String(36), primary_key=True, default=uuid_generator())
    fname = Column(String(32), nullable=False)
    lname = Column(String(32), nullable=False)
    uname = Column(String(32), nullable=False, unique=True)
    email = Column(String(32), nullable=False, unique=True)
    password = Column(String(70), nullable=False)
    isdeleted = Column(Boolean, default=False, nullable=False)
    iscreated = Column(DateTime, default=datetime.utcnow())
    # ismodified = Column(DateTime, default=datetime.utcnow())
    ismodified = Column(DateTime, default=datetime.utcnow(), onupdate=datetime.utcnow)
    isactive = Column(Boolean, default=True)
    isverified = Column(Boolean, default=False)


create_tables()
