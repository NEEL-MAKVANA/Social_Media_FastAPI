from sqlalchemy import String, Integer, Boolean, Column, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base, engine
import uuid
from datetime import datetime


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
    ismodified = Column(DateTime, default=datetime.utcnow(), onupdate=datetime.utcnow)
    isactive = Column(Boolean, default=True)
    isverified = Column(Boolean, default=False)


class Otp(Base):
    __tablename__ = "otps"
    id = Column(String(36), primary_key=True, default=uuid_generator())
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    email = Column(String(36))
    otp = Column(String(6))
    attempts = Column(Integer, default=1)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = relationship("User")
