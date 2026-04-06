"""
FastAPI REST API for the Intelligent Loan Processing System

This module provides HTTP endpoints for external integration
with the multi-agent loan processing system.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uvicorn
import asyncio
from datetime import datetime
import uuid
import os
import sys

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crew.crew_setup import create_loan_crew, quick_loan_process
from utils.logger import get_logger
from utils.rules import validate_kyc


# Pydantic models for API
class LoanApplication(BaseModel):
    """Loan application model"""
    name: str = Field(..., description="Applicant's full name", min_length=2, max_length=100)
    age: int = Field(..., description="Applicant's age in years", ge=18, le=100)
    income: int = Field(..., description="Annual income in local currency", gt=0)
    loan_amount: int = Field(..., description="Requested loan amount", gt=0, le=10000000)
    credit_score: int = Field(..., description="Credit score (300-900)", ge=300, le=900)
    existing_loans: int = Field(..., description="Number of existing loans", ge=0)


class LoanDecision(BaseModel):
    """Loan decision response model"""
    application_id: str
    applicant_name: str
    loan_amount_requested: int
    status: str  # Approved, Rejected, Review
    reason: str
    risk_level: str
    credit_score: int
    income: int
    age: int
    processing_time: Optional[float] = None
    timestamp: str


class BatchApplication(BaseModel):
    """Batch loan application model"""
    applications: List[LoanApplication] = Field(..., description="List of loan applications")


class BatchDecision(BaseModel):
    """Batch decision response model"""
    batch_id: str
    total_applications: int
    decisions: List[LoanDecision]
    processing_time: Optional[float] = None
    timestamp: str


class HealthCheck(BaseModel):
    """Health check response model"""
    status: str
    version: str
    timestamp: str
    uptime: float


class SystemInfo(BaseModel):
    """System information response model"""
    agents: List[Dict[str, str]]
    supported_operations: List[str]
    max_batch_size: int
    api_version: str


# Initialize FastAPI app
app = FastAPI(
    title="Intelligent Loan Processing API",
    description="Multi-agent AI system for BFSI loan processing automation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
logger = get_logger("loan_api")
crew = create_loan_crew()
start_time = datetime.now()

# In-memory storage for batch results (in production, use Redis/Database)
batch_results: Dict[str, BatchDecision] = {}


@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint"""
    return {
        "message": "Intelligent Loan Processing API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint"""
    uptime = (datetime.now() - start_time).total_seconds()
    return HealthCheck(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.now().isoformat(),
        uptime=uptime
    )


@app.get("/info", response_model=SystemInfo)
async def system_info():
    """System information endpoint"""
    agent_info = crew.get_agent_info()
    return SystemInfo(
        agents=agent_info,
        supported_operations=["single_application", "batch_processing", "validation"],
        max_batch_size=50,
        api_version="1.0.0"
    )


@app.post("/validate", response_model=Dict[str, Any])
async def validate_application(application: LoanApplication):
    """Validate loan application data"""
    try:
        # Convert to dict for validation
        app_data = application.dict()
        
        # Perform KYC validation
        is_valid, reason = validate_kyc(app_data)
        
        return {
            "valid": is_valid,
            "reason": reason,
            "application_id": str(uuid.uuid4())
        }
        
    except Exception as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/process", response_model=LoanDecision)
async def process_loan_application(application: LoanApplication, background_tasks: BackgroundTasks):
    """Process a single loan application"""
    start_processing = datetime.now()
    application_id = str(uuid.uuid4())
    
    try:
        # Log application start
        logger.log_application_start(application.dict())
        
        # Process application
        result = quick_loan_process(application.dict())
        
        # Calculate processing time
        processing_time = (datetime.now() - start_processing).total_seconds()
        
        # Log application completion
        logger.log_application_complete(result)
        
        # Create response
        decision = LoanDecision(
            application_id=application_id,
            applicant_name=result.get('applicant_name', 'Unknown'),
            loan_amount_requested=result.get('loan_amount_requested', 0),
            status=result.get('status', 'Unknown'),
            reason=result.get('reason', 'No reason provided'),
            risk_level=result.get('risk_level', 'Unknown'),
            credit_score=result.get('credit_score', 0),
            income=result.get('income', 0),
            age=result.get('age', 0),
            processing_time=processing_time,
            timestamp=datetime.now().isoformat()
        )
        
        # Log processing metrics
        background_tasks.add_task(
            logger.log_system_metrics,
            {
                "operation": "single_application",
                "processing_time": processing_time,
                "status": result.get('status', 'Unknown')
            }
        )
        
        return decision
        
    except Exception as e:
        logger.log_error_with_context(e, {"application_id": application_id})
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


@app.post("/batch", response_model=BatchDecision)
async def process_batch_applications(batch: BatchApplication, background_tasks: BackgroundTasks):
    """Process multiple loan applications in batch"""
    start_processing = datetime.now()
    batch_id = str(uuid.uuid4())
    
    try:
        # Validate batch size
        if len(batch.applications) > 50:
            raise HTTPException(
                status_code=400, 
                detail="Batch size exceeds maximum limit of 50 applications"
            )
        
        logger.info(f"Starting batch processing", batch_id=batch_id, applications=len(batch.applications))
        
        # Convert applications to dicts
        applications_data = [app.dict() for app in batch.applications]
        
        # Process batch
        results = crew.process_multiple_applications(applications_data)
        
        # Calculate processing time
        processing_time = (datetime.now() - start_processing).total_seconds()
        
        # Create decision objects
        decisions = []
        for i, result in enumerate(results):
            decision = LoanDecision(
                application_id=f"{batch_id}_{i+1}",
                applicant_name=result.get('applicant_name', 'Unknown'),
                loan_amount_requested=result.get('loan_amount_requested', 0),
                status=result.get('status', 'Unknown'),
                reason=result.get('reason', 'No reason provided'),
                risk_level=result.get('risk_level', 'Unknown'),
                credit_score=result.get('credit_score', 0),
                income=result.get('income', 0),
                age=result.get('age', 0),
                timestamp=datetime.now().isoformat()
            )
            decisions.append(decision)
        
        # Create batch response
        batch_decision = BatchDecision(
            batch_id=batch_id,
            total_applications=len(batch.applications),
            decisions=decisions,
            processing_time=processing_time,
            timestamp=datetime.now().isoformat()
        )
        
        # Store batch result
        batch_results[batch_id] = batch_decision
        
        # Log batch completion
        background_tasks.add_task(
            logger.log_system_metrics,
            {
                "operation": "batch_processing",
                "batch_id": batch_id,
                "total_applications": len(batch.applications),
                "processing_time": processing_time
            }
        )
        
        logger.info(f"Batch processing completed", batch_id=batch_id, processing_time=processing_time)
        
        return batch_decision
        
    except Exception as e:
        logger.log_error_with_context(e, {"batch_id": batch_id})
        raise HTTPException(status_code=500, detail=f"Batch processing failed: {str(e)}")


@app.get("/batch/{batch_id}", response_model=BatchDecision)
async def get_batch_result(batch_id: str):
    """Get batch processing result"""
    if batch_id not in batch_results:
        raise HTTPException(status_code=404, detail="Batch ID not found")
    
    return batch_results[batch_id]


@app.get("/statistics")
async def get_processing_statistics():
    """Get processing statistics"""
    # In production, this would query a database
    total_batches = len(batch_results)
    total_applications = sum(batch.total_applications for batch in batch_results.values())
    
    if total_applications > 0:
        approved_count = sum(
            len([d for d in batch.decisions if d.status == "Approved"])
            for batch in batch_results.values()
        )
        rejected_count = sum(
            len([d for d in batch.decisions if d.status == "Rejected"])
            for batch in batch_results.values()
        )
        review_count = sum(
            len([d for d in batch.decisions if d.status == "Review"])
            for batch in batch_results.values()
        )
        
        approval_rate = (approved_count / total_applications) * 100
        rejection_rate = (rejected_count / total_applications) * 100
        review_rate = (review_count / total_applications) * 100
    else:
        approval_rate = rejection_rate = review_rate = 0
    
    return {
        "total_batches_processed": total_batches,
        "total_applications_processed": total_applications,
        "approval_rate": round(approval_rate, 2),
        "rejection_rate": round(rejection_rate, 2),
        "review_rate": round(review_rate, 2),
        "api_uptime": (datetime.now() - start_time).total_seconds()
    }


@app.delete("/batch/{batch_id}")
async def delete_batch_result(batch_id: str):
    """Delete batch processing result"""
    if batch_id not in batch_results:
        raise HTTPException(status_code=404, detail="Batch ID not found")
    
    del batch_results[batch_id]
    return {"message": f"Batch {batch_id} results deleted successfully"}


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    logger.error(f"HTTP exception: {exc.status_code} - {exc.detail}")
    return {"error": exc.detail, "status_code": exc.status_code}


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.log_error_with_context(exc, {"endpoint": str(request.url)})
    return {"error": "Internal server error", "status_code": 500}


def create_app() -> FastAPI:
    """Create and configure the FastAPI app"""
    return app


if __name__ == "__main__":
    # Run the API server
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
