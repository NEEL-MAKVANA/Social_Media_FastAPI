from sqlalchemy import String, Integer, Boolean, Column, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from database.db_config import Base
import uuid
from datetime import datetime


class Post(Base):
    __tablename__ = "posts"
    id = Column(String(36), primary_key=True, default=str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    types = Column(String(10))
    title = Column(String(100))
    description = Column(String(400))
    likes = Column(Integer, default=0)
    comments = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    user = relationship("User")
