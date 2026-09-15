import os
import json
from typing import TypedDict, Optional, Dict, Any
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

class ComplaintFormModel(BaseModel):
    complaint_source: Optional[str] = Field(default="", description="Source, e.g. Hospital, Pharmacy, Distributor")
    customer_name: Optional[str] = Field(default="", description="Customer or reporting facility name")
    product_name: Optional[str] = Field(default="", description="Product name or API")
    product_strength_grade: Optional[str] = Field(default="", description="Strength (e.g. 500mg) or Grade (e.g. IP/BP)")
    batch_number: Optional[str] = Field(default="", description="Batch or lot number")
    manufacturing_date: Optional[str] = Field(default="", description="YYYY-MM-DD")
    expiry_date: Optional[str] = Field(default="", description="YYYY-MM-DD")
    quantity_affected: Optional[str] = Field(default="", description="Quantity affected with units")
    complaint_type: Optional[str] = Field(default="", description="Complaint category/type")
    complaint_date: Optional[str] = Field(default="", description="YYYY-MM-DD")
    detailed_description: Optional[str] = Field(default="", description="Comprehensive description of defect")
    initial_severity: Optional[str] = Field(default="Minor", description="Critical, Major, or Minor")
    priority: Optional[str] = Field(default="Low", description="High, Medium, or Low")

#    """Same shape as ComplaintFormModel but everything optional/None so unmentioned fields don't get overwritten."""

# Model specifically for edits: all fields default to None so unmentioned fields are ignored
class PartialComplaintEditModel(BaseModel):
    complaint_source: Optional[str] = Field(default=None)
    customer_name: Optional[str] = Field(default=None)
    product_name: Optional[str] = Field(default=None)
    product_strength_grade: Optional[str] = Field(default=None)
    batch_number: Optional[str] = Field(default=None)
    manufacturing_date: Optional[str] = Field(default=None)
    expiry_date: Optional[str] = Field(default=None)
    quantity_affected: Optional[str] = Field(default=None)
    complaint_type: Optional[str] = Field(default=None)
    complaint_date: Optional[str] = Field(default=None)
    detailed_description: Optional[str] = Field(default=None)

class RiskAssessmentModel(BaseModel):
    severity_classification: str = Field(default="Minor", description="Critical, Major, or Minor")
    risk_justification: str = Field(default="", description="Pharma risk evaluation & GMP impact")
    suggested_next_action: str = Field(default="", description="e.g. Route to QA investigation and issue replacement")
    capa_recommendation: str = Field(default="", description="Corrective and preventive action recommendation")
    regulatory_impact: str = Field(default="No immediate recall required", description="Recall or regulatory notification impact")

class GraphState(TypedDict):
    action_type: str  # "log_complaint" | "edit_complaint" | "document_extract"
    user_prompt: str
    current_form: Dict[str, Any]
    current_risk: Dict[str, Any]
    ai_response_message: str

llm = ChatGroq(
    model_name="openai/gpt-oss-20b",
    temperature=0.1,
    max_tokens=600,
    groq_api_key=os.getenv("GROQ_API_KEY")
)

def copilot_agent_node(state: GraphState):
    action = state["action_type"]
    user_input = state["user_prompt"]
    current_form = dict(state.get("current_form") or {})

    if action == "edit_complaint":
        # Extract ONLY the fields the user wants to patch
        patch_llm = llm.with_structured_output(PartialComplaintEditModel)
        edit_prompt = (
            "Identify ONLY the fields explicitly mentioned for modification in this correction text. "
            "Leave all untouched fields as null/None.\n\n"
            f"Correction: {user_input}"
        )
        patch_result = patch_llm.invoke(edit_prompt)
        patch_dict = {k: v for k, v in patch_result.model_dump().items() if v is not None and str(v).strip() != ""}

        # Merge changes into existing form (preserving all previous data)
        form_dict = {**current_form, **patch_dict}
        modified_fields = list(patch_dict.keys())
        bot_msg = f"Updated {', '.join(modified_fields)} while preserving all other complaint data."

    else:
        # Full extraction for log_complaint and document_extract
        full_extractor = llm.with_structured_output(ComplaintFormModel)
        extraction_prompt = (
            "Extract all pharmaceutical complaint details from the text below. "
            "Leave unknown fields empty.\n\n"
            f"Text: {user_input}"
        )
        extracted = full_extractor.invoke(extraction_prompt)
        form_dict = extracted.model_dump()
        bot_msg = f"Extracted complaint details for {form_dict.get('product_name') or 'the reported product'}."

    # Re-calculate Risk Assessment with updated form data
    risk_llm = llm.with_structured_output(RiskAssessmentModel)
    risk_prompt = (
        f"Pharmaceutical QA Risk Assessment:\n"
        f"Product: {form_dict.get('product_name')} ({form_dict.get('product_strength_grade')})\n"
        f"Batch: {form_dict.get('batch_number')}\n"
        f"Quantity: {form_dict.get('quantity_affected')}\n"
        f"Issue: {form_dict.get('detailed_description') or form_dict.get('complaint_type')}\n\n"
        "Provide: severity (Critical/Major/Minor), risk justification, suggested next action, and CAPA."
    )
    risk_result: RiskAssessmentModel = risk_llm.invoke(risk_prompt)
    risk_dict = risk_result.model_dump()

    # Sync severity and priority
    form_dict["initial_severity"] = risk_dict["severity_classification"]
    SEVERITY_TO_PRIORITY = {"Critical": "High", "Major": "Medium", "Minor": "Low"}
    form_dict["priority"] = SEVERITY_TO_PRIORITY.get(risk_dict["severity_classification"], "Low")
    return {
        "current_form": form_dict,
        "current_risk": risk_dict,
        "ai_response_message": bot_msg
    }

workflow = StateGraph(GraphState)
workflow.add_node("copilot", copilot_agent_node)
workflow.set_entry_point("copilot")
workflow.add_edge("copilot", END)
complaint_copilot_agent = workflow.compile()