from sqlalchemy import String, Integer, Column, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database.db_config import Base
import uuid
from datetime import datetime


class Story(Base):
    __tablename__ = "stories"
    id = Column(String(36), primary_key=True, default=str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    types = Column(String(10))
    likes = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User")
