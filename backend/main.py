from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as api_router
from app.db.session import engine, Base
import app.db.models  # Ensures models register with SQLAlchemy metadata

# Create database tables automatically
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AIVOA Pharma QMS Customer Complaint API",
    version="1.0.0"
)

# Enable CORS for local React/Vite development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "AIVOA QMS Intake Engine"}