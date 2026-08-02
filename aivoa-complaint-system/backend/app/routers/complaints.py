import uuid
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.file_parsing import extract_text_from_upload
from app.models.complaint import Complaint
from app.schemas.complaint import (
    ComplaintOut,
    ComplaintCreate,
    ComplaintUpdate,
    ExtractionRequest,
    ExtractionResponse,
    ChatRequest,
    ChatResponse,
)
from app.agents.graph import complaint_graph
from app.agents.duplicate import find_possible_duplicates
from app.agents.copilot import answer_copilot_question

router = APIRouter(prefix="/api/complaints", tags=["complaints"])


def _run_extraction_pipeline(raw_text: str, db: Session) -> ExtractionResponse:
    result = complaint_graph.invoke({"raw_text": raw_text})
    duplicates = find_possible_duplicates(db, result.get("extracted", {}))

    return ExtractionResponse(
        extracted=result.get("extracted", {}),
        completeness_score=result.get("completeness_score", 0),
        missing_fields=result.get("missing_fields", []),
        ai_risk_classification=result.get("ai_risk_classification"),
        ai_risk_rationale=result.get("ai_risk_rationale"),
        ai_summary=result.get("ai_summary"),
        extraction_confidence=result.get("extraction_confidence", 0),
        possible_duplicate_ids=[d.id for d in duplicates],
    )


@router.post("/extract", response_model=ExtractionResponse)
def extract_from_text(payload: ExtractionRequest, db: Session = Depends(get_db)):
    """Path B in the UI: 'Paste Complaint Text / Email'."""
    if not payload.text.strip():
        raise HTTPException(status_code=400, detail="Text is empty.")
    return _run_extraction_pipeline(payload.text, db)


@router.post("/extract-file", response_model=ExtractionResponse)
async def extract_from_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Path A in the UI: drag & drop complaint document."""
    raw_text = await extract_text_from_upload(file)
    if not raw_text.strip():
        raise HTTPException(status_code=400, detail="Could not extract any text from the file.")
    return _run_extraction_pipeline(raw_text, db)


@router.post("", response_model=ComplaintOut)
def save_complaint(payload: ComplaintCreate, db: Session = Depends(get_db)):
    """'Save Complaint' button — persists the (possibly AI-populated, human-reviewed) form."""
    complaint = Complaint(**payload.model_dump())
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    return complaint


@router.get("", response_model=list[ComplaintOut])
def list_complaints(db: Session = Depends(get_db)):
    return db.query(Complaint).order_by(Complaint.created_at.desc()).all()


@router.get("/{complaint_id}", response_model=ComplaintOut)
def get_complaint(complaint_id: uuid.UUID, db: Session = Depends(get_db)):
    complaint = db.query(Complaint).filter(Complaint.id == str(complaint_id)).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found.")
    return complaint


@router.put("/{complaint_id}", response_model=ComplaintOut)
def update_complaint(complaint_id: uuid.UUID, payload: ComplaintUpdate, db: Session = Depends(get_db)):
    complaint = db.query(Complaint).filter(Complaint.id == str(complaint_id)).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found.")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(complaint, field, value)
    db.commit()
    db.refresh(complaint)
    return complaint


@router.post("/chat", response_model=ChatResponse)
def chat_with_copilot(payload: ChatRequest, db: Session = Depends(get_db)):
    """AI Copilot chat box — 'Ask me anything about this complaint...'"""
    context = None
    if payload.complaint_id:
        complaint = db.query(Complaint).filter(Complaint.id == str(payload.complaint_id)).first()
        if complaint:
            context = ComplaintOut.model_validate(complaint).model_dump(mode="json")
    reply = answer_copilot_question(payload.message, context)
    return ChatResponse(reply=reply)
