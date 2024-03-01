from sqlalchemy import String, Boolean, Column, DateTime
from sqlalchemy.orm import relationship
from database.db_config import Base
import uuid
from datetime import datetime


class User(Base):
    __tablename__ = "users"
    id = Column(String(36), primary_key=True, default=str(uuid.uuid4()))
    fname = Column(String(32), nullable=False)
    lname = Column(String(32), nullable=False)
    uname = Column(String(32), nullable=False, unique=True)
    email = Column(String(32), nullable=False, unique=True)
    password = Column(String(70), nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow())
    modified_at = Column(DateTime, default=datetime.utcnow(), onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
