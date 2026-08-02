import uuid
from datetime import datetime

from sqlalchemy import Column, String, Text, Date, DateTime, Float, Boolean, CHAR

from app.core.database import Base


class Complaint(Base):
    __tablename__ = "complaints"

    # MySQL has no native UUID type, so we store it as a CHAR(36) string
    # and generate the UUID on the Python side.
    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # 1. Origin & Customer Details
    complaint_source = Column(String(255), nullable=True)
    customer_name = Column(String(255), nullable=True)

    # 2. Product & Batch Identification
    product_name = Column(String(255), nullable=True)
    product_strength_grade = Column(String(255), nullable=True)
    batch_lot_number = Column(String(255), nullable=True)
    manufacturing_date = Column(Date, nullable=True)
    expiry_date = Column(Date, nullable=True)
    quantity_affected = Column(Float, nullable=True)

    # 3. Complaint Details
    complaint_type = Column(String(255), nullable=True)
    complaint_date = Column(Date, nullable=True)
    detailed_description = Column(Text, nullable=True)

    # 4. Initial Assessment & Priority
    initial_severity = Column(String(255), nullable=True)  # Critical / Major / Minor
    priority = Column(String(255), nullable=True)  # High / Medium / Low

    # AI-derived fields (bonus features)
    completeness_score = Column(Float, nullable=True)  # 0-100, from Completeness Checker
    missing_fields = Column(Text, nullable=True)  # JSON-encoded list
    ai_risk_classification = Column(String(255), nullable=True)  # AI Risk Classification bonus
    ai_risk_rationale = Column(Text, nullable=True)
    is_possible_duplicate = Column(Boolean, default=False)
    duplicate_of_id = Column(CHAR(36), nullable=True)
    ai_summary = Column(Text, nullable=True)  # Complaint Summary bonus
    extraction_confidence = Column(Float, nullable=True)

    status = Column(String(255), default="Pending Triage")
    raw_source_text = Column(Text, nullable=True)  # original pasted/uploaded text, for audit trail

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
