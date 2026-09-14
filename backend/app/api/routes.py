import json
from typing import Optional, Dict, Any
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.utils.parser import extract_text_from_file
from app.graph.workflow import complaint_copilot_agent
from app.db.models import Complaint
from app.db.session import get_db

router = APIRouter()

class ChatCopilotRequest(BaseModel):
    message: str
    action_type: str = "log_complaint" # "log_complaint" | "edit_complaint"
    current_form: Optional[Dict[str, Any]] = None
    current_risk: Optional[Dict[str, Any]] = None

@router.post("/copilot-chat")
def copilot_chat(payload: ChatCopilotRequest):
    """Handles conversational logging and natural language modifications."""
    initial_state = {
        "action_type": payload.action_type,
        "user_prompt": payload.message,
        "current_form": payload.current_form or {},
        "current_risk": payload.current_risk or {},
        "ai_response_message": ""
    }
    result = complaint_copilot_agent.invoke(initial_state)
    return {
        "form_data": result["current_form"],
        "risk_assessment": result["current_risk"],
        "reply": result["ai_response_message"]
    }

@router.post("/copilot-upload")
async def copilot_upload(
    file: UploadFile = File(...),
    current_form: Optional[str] = Form(None),
    current_risk: Optional[str] = Form(None)
):
    """Handles PDF, DOCX, EML parsing via the Document Extraction Tool."""
    file_bytes = await file.read()
    raw_text = extract_text_from_file(file_bytes, file.filename)
    if not raw_text:
        raise HTTPException(status_code=400, detail="Could not extract text from the file.")

    parsed_form = json.loads(current_form) if current_form else {}
    parsed_risk = json.loads(current_risk) if current_risk else {}

    initial_state = {
        "action_type": "document_extract",
        "user_prompt": raw_text,
        "current_form": parsed_form,
        "current_risk": parsed_risk,
        "ai_response_message": ""
    }
    result = complaint_copilot_agent.invoke(initial_state)
    return {
        "form_data": result["current_form"],
        "risk_assessment": result["current_risk"],
        "reply": f"Extracted complaint details from {file.filename}."
    }

@router.post("/save-complaint")
def save_complaint(data: dict, db: Session = Depends(get_db)):
    record = Complaint(**data)
    db.add(record)
    db.commit()
    db.refresh(record)
    return {"status": "success", "complaint_id": record.id}

@router.get("/complaints")
def list_complaints(db: Session = Depends(get_db)):
    """Fetches all logged complaints for tracking."""
    complaints = db.query(Complaint).order_by(Complaint.created_at.desc()).all()
    return complaints