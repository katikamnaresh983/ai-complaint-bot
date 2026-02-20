from pydantic import BaseModel

class ComplaintCreate(BaseModel):
    resident_name: str
    message: str
class ComplaintUpdate(BaseModel):
    status: str