from datetime import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime

from app.core.db import Base


class File(Base):
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    create_date = Column(DateTime, default=datetime.now)


