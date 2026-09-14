from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.utils.parser import extract_text_from_file
from app.graph.workflow import complaint_agent
from app.db.models import Complaint
from app.db.session import get_db

router = APIRouter()

class ComplaintCreateSchema(BaseModel):
    complaint_source: Optional[str] = ""
    customer_name: Optional[str] = ""
    product_name: Optional[str] = ""
    product_strength_grade: Optional[str] = ""
    batch_number: Optional[str] = ""
    manufacturing_date: Optional[str] = ""
    expiry_date: Optional[str] = ""
    quantity_affected: Optional[str] = ""
    complaint_type: Optional[str] = ""
    complaint_date: Optional[str] = ""
    detailed_description: Optional[str] = ""
    initial_severity: Optional[str] = "Minor"
    priority: Optional[str] = "Low"
    root_cause_hypothesis: Optional[str] = ""
    recommended_capa: Optional[str] = ""
    completeness_score: Optional[int] = 0

@router.post("/process-complaint")
async def process_complaint(
    text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    """
    Accepts pasted complaint text OR an uploaded file (.pdf, .docx, .txt, .eml),
    invokes the LangGraph agent, and returns extracted form fields + QA triage.
    """
    raw_content = ""

    if file:
        file_bytes = await file.read()
        raw_content = extract_text_from_file(file_bytes, file.filename)
    elif text:
        raw_content = text.strip()

    if not raw_content:
        raise HTTPException(status_code=400, detail="No complaint text or valid file provided.")

    # Execute LangGraph workflow
    initial_state = {
        "raw_text": raw_content,
        "form_data": {},
        "capa_suggestion": "",
        "root_cause_hypothesis": "",
        "completeness_score": 0
    }
    result = complaint_agent.invoke(initial_state)

    return {
        "form_data": result.get("form_data", {}),
        "capa_suggestion": result.get("capa_suggestion", ""),
        "root_cause_hypothesis": result.get("root_cause_hypothesis", ""),
        "completeness_score": result.get("completeness_score", 0)
    }

@router.post("/save-complaint")
def save_complaint(payload: ComplaintCreateSchema, db: Session = Depends(get_db)):
    """
    Persists reviewed and verified complaint data into the database.
    """
    record = Complaint(**payload.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return {"status": "success", "complaint_id": record.id}

@router.get("/complaints")
def list_complaints(db: Session = Depends(get_db)):
    """Fetches all logged complaints for tracking."""
    return db.query(Complaint).order_by(Complaint.created_at.desc()).all()