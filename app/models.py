from sqlalchemy import Column, Integer, String, Text
from .database import Base

class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)
    resident_name = Column(String)
    message = Column(Text)
    category = Column(String, default="Uncategorized")
    status = Column(String, default="Open")