from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.database import engine, Base
import app.models # registers models with Base

# Import API routers
from app.api.v1.auth import router as auth_router
from app.api.v1.applications import router as applications_router
from app.api.v1.documents import router as documents_router
from app.api.v1.fields import router as fields_router
from app.api.v1.validation import router as validation_router
from app.api.v1.compliance import router as compliance_router
from app.api.v1.verification import router as verification_router
from app.api.v1.evidence_requests import router as evidence_requests_router
from app.api.v1.audit import router as audit_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.demo import router as demo_router

# Ensure tables are created
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AICTE SmartVerify API",
    description="""
    ## AICTE SmartVerify — SIH26261 MVP
    **AI-Powered Application Validation, Document Authentication and Regulatory Compliance Verification**
    
    *Important Notice: This application is an independent prototype developed for the Smart India Hackathon (SIH26261) and is not an official AICTE production system. All external issuing authority checks are simulated demonstration adapters.*
    """,
    version="1.0.0-PROTOTYPE",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for hackathon local dev flexibility
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API v1 Routers
API_V1_PREFIX = "/api/v1"
app.include_router(auth_router, prefix=API_V1_PREFIX)
app.include_router(applications_router, prefix=API_V1_PREFIX)
app.include_router(documents_router, prefix=API_V1_PREFIX)
app.include_router(fields_router, prefix=API_V1_PREFIX)
app.include_router(validation_router, prefix=API_V1_PREFIX)
app.include_router(compliance_router, prefix=API_V1_PREFIX)
app.include_router(verification_router, prefix=API_V1_PREFIX)
app.include_router(evidence_requests_router, prefix=API_V1_PREFIX)
app.include_router(audit_router, prefix=API_V1_PREFIX)
app.include_router(dashboard_router, prefix=API_V1_PREFIX)
app.include_router(demo_router, prefix=API_V1_PREFIX)


@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "HEALTHY",
        "system": "AICTE SmartVerify MVP",
        "version": "1.0.0-PROTOTYPE",
        "database": settings.DATABASE_URL.split(":")[0],
        "environment": settings.ENVIRONMENT
    }


@app.get("/", tags=["System"])
def root():
    return {
        "message": "Welcome to AICTE SmartVerify API (SIH26261 MVP)",
        "docs": "/docs",
        "prototype_disclaimer": "Independent prototype - not an official AICTE production system."
    }
