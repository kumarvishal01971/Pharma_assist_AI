import uuid
from datetime import date, datetime
from typing import Optional, List

from pydantic import BaseModel


class ComplaintBase(BaseModel):
    complaint_source: Optional[str] = None
    customer_name: Optional[str] = None
    product_name: Optional[str] = None
    product_strength_grade: Optional[str] = None
    batch_lot_number: Optional[str] = None
    manufacturing_date: Optional[date] = None
    expiry_date: Optional[date] = None
    quantity_affected: Optional[float] = None
    complaint_type: Optional[str] = None
    complaint_date: Optional[date] = None
    detailed_description: Optional[str] = None
    initial_severity: Optional[str] = None
    priority: Optional[str] = None


class ComplaintCreate(ComplaintBase):
    pass


class ComplaintUpdate(ComplaintBase):
    status: Optional[str] = None


class ComplaintOut(ComplaintBase):
    id: uuid.UUID
    completeness_score: Optional[float] = None
    missing_fields: Optional[str] = None
    ai_risk_classification: Optional[str] = None
    ai_risk_rationale: Optional[str] = None
    is_possible_duplicate: bool = False
    duplicate_of_id: Optional[uuid.UUID] = None
    ai_summary: Optional[str] = None
    extraction_confidence: Optional[float] = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ExtractionRequest(BaseModel):
    """For the 'Paste Complaint Text / Email' path."""
    text: str


class ExtractionResponse(BaseModel):
    extracted: ComplaintBase
    completeness_score: float
    missing_fields: List[str]
    ai_risk_classification: Optional[str] = None
    ai_risk_rationale: Optional[str] = None
    ai_summary: Optional[str] = None
    extraction_confidence: float
    possible_duplicate_ids: List[uuid.UUID] = []


class ChatRequest(BaseModel):
    complaint_id: Optional[uuid.UUID] = None
    message: str


class ChatResponse(BaseModel):
    reply: str
