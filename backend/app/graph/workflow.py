import os
from typing import TypedDict, Optional
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

# Schema matching the exact reference UI form inputs
class ExtractedComplaintData(BaseModel):
    complaint_source: Optional[str] = Field(default="", description="Source of complaint, e.g. Hospital, Pharmacy, Distributor")
    customer_name: Optional[str] = Field(default="", description="Name of reporting individual, clinic, or pharmacy")
    product_name: Optional[str] = Field(default="", description="Name of the pharmaceutical drug or API")
    product_strength_grade: Optional[str] = Field(default="", description="Strength (e.g., 500mg, 10ml) or API purity grade")
    batch_number: Optional[str] = Field(default="", description="Batch / Lot number mentioned")
    manufacturing_date: Optional[str] = Field(default="", description="YYYY-MM-DD format if available")
    expiry_date: Optional[str] = Field(default="", description="YYYY-MM-DD format if available")
    quantity_affected: Optional[str] = Field(default="", description="Number or weight of units affected (e.g., 100 vials, 50 kg)")
    complaint_type: Optional[str] = Field(default="", description="Category: Packaging, Contamination, Physical Defect, Labeling, Efficacy")
    complaint_date: Optional[str] = Field(default="", description="Date complaint was filed or received (YYYY-MM-DD)")
    detailed_description: Optional[str] = Field(default="", description="Detailed narrative of the defect reported")
    initial_severity: Optional[str] = Field(default="Minor", description="Critical, Major, or Minor")
    priority: Optional[str] = Field(default="Low", description="High, Medium, or Low")

class GraphState(TypedDict):
    raw_text: str
    form_data: dict
    capa_suggestion: str
    root_cause_hypothesis: str
    completeness_score: int

llm = ChatGroq(
    model_name="openai/gpt-oss-20b", 
    temperature=0.1,
    max_tokens=500,
    groq_api_key=os.getenv("GROQ_API_KEY")
)
def extract_complaint_node(state: GraphState):
    """Extracts structured complaint entities using constrained LLM output."""
    structured_llm = llm.with_structured_output(ExtractedComplaintData)
    prompt = (
        "You are an expert Pharmaceutical Quality Assurance specialist.\n"
        "Extract all available complaint details from the text below. "
        "Leave unknown fields as empty strings.\n\n"
        f"Complaint Text:\n{state['raw_text']}"
    )
    result: ExtractedComplaintData = structured_llm.invoke(prompt)
    return {"form_data": result.model_dump()}

def triage_and_capa_node(state: GraphState):
    """Assesses QMS severity, root cause, CAPA recommendation, and completeness."""
    form = state["form_data"]

    triage_prompt = f"""You are a Pharmaceutical Quality Assurance Lead evaluating a GMP customer complaint.
Product: {form.get('product_name')} ({form.get('product_strength_grade')})
Batch Number: {form.get('batch_number')}
Reported Issue: {form.get('detailed_description')}

Respond with:
1. HYPOTHESIZED ROOT CAUSE (1-2 sentences):
2. RECOMMENDED CAPA ACTION (1-2 practical corrective/preventive steps):
"""
    response = llm.invoke(triage_prompt)
    content = response.content

    # Split response into root cause and CAPA
    root_cause = "Pending QA investigation."
    capa = content
    if "RECOMMENDED CAPA" in content:
        parts = content.split("RECOMMENDED CAPA")
        root_cause = parts[0].replace("HYPOTHESIZED ROOT CAUSE", "").replace("1.", "").strip(":\n *")
        capa = parts[1].strip(":\n *")

    # Compute a completeness score based on populated fields
    total_fields = len(form)
    filled_fields = sum(1 for v in form.values() if v and str(v).strip())
    score = int((filled_fields / total_fields) * 100) if total_fields else 0

    return {
        "root_cause_hypothesis": root_cause,
        "capa_suggestion": capa,
        "completeness_score": score
    }

# Build and compile LangGraph state workflow
workflow = StateGraph(GraphState)
workflow.add_node("extractor", extract_complaint_node)
workflow.add_node("qa_triage", triage_and_capa_node)

workflow.set_entry_point("extractor")
workflow.add_edge("extractor", "qa_triage")
workflow.add_edge("qa_triage", END)

complaint_agent = workflow.compile()