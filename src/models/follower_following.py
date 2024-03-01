from sqlalchemy import String, Column, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from database.db_config import Base
import uuid
from datetime import datetime


class FollowerFollowing(Base):
    __tablename__ = "follower_following"
    id = Column(String(36), primary_key=True, default=str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    follower = Column(JSON)
    following = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User")
