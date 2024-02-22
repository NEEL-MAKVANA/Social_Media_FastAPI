from sqlalchemy import String, Integer, Boolean, Column, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database.db_config import Base, engine
import uuid
from datetime import datetime


def uuid_generator():
    return str(uuid.uuid4())


def create_tables():
    Base.metadata.create_all(engine)


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


create_tables()
