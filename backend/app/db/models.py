from sqlalchemy import Column,Integer,String,Text,DateTime
from sqlalchemy import func
from app.db.session import Base

class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer,primary_key = True,index=True)

    complaint_source = Column(String(255),nullable = True)
    customer_name = Column(String(255), nullable=True)

    product_name = Column(String(255), nullable=True)
    product_strength_grade = Column(String(100), nullable=True)
    batch_number = Column(String(100), nullable=True)
    manufacturing_date = Column(String(50), nullable=True)
    expiry_date = Column(String(50), nullable=True)
    quantity_affected = Column(String(100), nullable=True)

    # 3. Complaint Details
    complaint_type = Column(String(100), nullable=True)
    complaint_date = Column(String(50), nullable=True)
    detailed_description = Column(Text, nullable=True)

    # 4. Initial Assessment & Priority
    initial_severity = Column(String(50), nullable=True)
    priority = Column(String(50), nullable=True)

    # Additional QMS Tracking & Bonus Insights
    status = Column(String(50), default="Pending Triage")
    root_cause_hypothesis = Column(Text, nullable=True)
    recommended_capa = Column(Text, nullable=True)
    completeness_score = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())