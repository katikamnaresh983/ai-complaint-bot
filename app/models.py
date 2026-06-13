from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from .database import Base


class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)
    resident_name = Column(String(120), nullable=False)
    message = Column(Text, nullable=False)
    category = Column(String(80), default="Uncategorized", nullable=False)
    status = Column(String(40), default="Open", nullable=False)
    priority = Column(String(40), default="Medium", nullable=False)
    sentiment = Column(String(40), default="Neutral", nullable=False)
    summary = Column(Text, default="", nullable=False)
    suggested_response = Column(Text, default="", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
