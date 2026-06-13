from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


ComplaintStatus = Literal["Open", "In Progress", "Resolved", "Closed"]
ComplaintPriority = Literal["Low", "Medium", "High", "Urgent"]


class ComplaintCreate(BaseModel):
    resident_name: str = Field(..., min_length=1, max_length=120)
    message: str = Field(..., min_length=5)
    category: str | None = None


class ComplaintUpdate(BaseModel):
    status: ComplaintStatus


class ComplaintCategoryUpdate(BaseModel):
    category: str = Field(..., min_length=2, max_length=80)


class ComplaintOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    resident_name: str
    message: str
    category: str
    status: str
    priority: str
    sentiment: str
    summary: str
    suggested_response: str
    created_at: datetime
    updated_at: datetime | None = None


class ComplaintAnalysis(BaseModel):
    category: str
    priority: ComplaintPriority
    sentiment: str
    summary: str
    suggested_response: str


class WhatsAppMessage(BaseModel):
    resident_name: str = Field(..., min_length=1, max_length=120)
    phone_number: str | None = None
    apartment_unit: str | None = Field(default=None, max_length=40)
    message: str = Field(..., min_length=5)


class WhatsAppReply(BaseModel):
    complaint_id: int
    reply: str
    complaint: ComplaintOut


class DashboardStats(BaseModel):
    total: int
    open: int
    in_progress: int
    resolved: int
    urgent: int
    categories: dict[str, int]
    priorities: dict[str, int]
