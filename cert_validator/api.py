"""
FastAPI REST API for Certificate Validation
"""
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException, Depends, Security, status
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field

from cert_validator.core import CertificateValidator
from cert_validator.revocation import RevocationChecker
from cert_validator.ct_checker import CTChecker
from cert_validator.job_queue import JobQueue
from cert_validator.cache import ValidationCache

logger = logging.getLogger('HIDR.CertValidator.API')

# API Models
class ValidateRequest(BaseModel):
    type: str = Field(..., description="Certificate type: pem, tls, file_sig")
    cert_pem: str = Field(..., description="PEM-encoded certificate")
    intermediates: Optional[List[str]] = Field(default=[], description="Intermediate certificates")
    context: Optional[Dict[str, Any]] = Field(default={}, description="Validation context")

class ValidateResponse(BaseModel):
    verdict: str
    cert_score: int
    confidence_breakdown: Dict[str, float]
    chain: List[str]
    ocsp: Optional[Dict[str, Any]] = None
    ct: Optional[Dict[str, Any]] = None
    errors: List[str]
    need_async: Optional[bool] = False

class JobResponse(BaseModel):
    job_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    cache_stats: Dict[str, Any]
    queue_size: int

# Security
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)
VALID_API_KEYS = {"hidr-agent-key-12345"}  # In production, load from secure config

async def verify_api_key(api_key: str = Security(API_KEY_HEADER)):
    """Verify API key"""
    if api_key not in VALID_API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    return api_key

# Initialize components
validator = CertificateValidator()
revocation_checker = RevocationChecker()
ct_checker = CTChecker()
cache = ValidationCache(default_ttl=86400)
job_queue = JobQueue(validator, max_workers=2)
job_queue.start()

# Create FastAPI app
app = FastAPI(
    title="HIDR Certificate Validator API",
    description="Certificate validation service with OCSP, CRL, and CT checking",
    version="1.0.0"
)

@app.get("/", tags=["Health"])
async def root():
    """Root endpoint"""
    return {"service": "HIDR Certificate Validator", "version": "1.0.0"}

@app.get("/api/expert/status", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint (public for monitoring)"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(timezone.utc).isoformat(),
        cache_stats=cache.get_stats(),
        queue_size=job_queue.queue.qsize()
    )

@app.post("/api/validate", response_model=ValidateResponse, tags=["Validation"])
async def validate_sync(
    request: ValidateRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Synchronous certificate validation (returns within 1-2s)
    Uses cached OCSP/CRL if available, otherwise returns partial result
    """
    try:
        # Check cache
        cache_key = f"validate:{hash(request.cert_pem)}"
        cached_result = cache.get(cache_key)
        
        if cached_result:
            logger.info("Returning cached validation result")
            return ValidateResponse(**cached_result)
        
        # Perform quick validation
        result = validator.validate_chain(
            request.cert_pem,
            intermediates=request.intermediates,
            context=request.context
        )
        
        # Add confidence breakdown
        result['confidence_breakdown'] = {
            'signature': 50 if result.get('signature_verification', {}).get('valid') else 0,
            'policy': 30 if result.get('policy_check', {}).get('valid') else 0,
            'revocation': 0,  # Not checked in sync mode
            'ct': 0
        }
        
        # Check if async validation needed
        need_async = False
        if request.context.get('full_check', False):
            need_async = True
        
        response_data = {
            'verdict': result['verdict'],
            'cert_score': result['cert_score'],
            'confidence_breakdown': result['confidence_breakdown'],
            'chain': result.get('chain', []),
            'errors': result.get('errors', []),
            'need_async': need_async
        }
        
        # Cache result
        cache.set(cache_key, response_data, ttl=3600)
        
        return ValidateResponse(**response_data)
    
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/validate-job", response_model=JobResponse, tags=["Validation"])
async def validate_async(
    request: ValidateRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Asynchronous certificate validation (full OCSP/CRL/CT check)
    Returns job_id for status polling
    """
    try:
        job_id = job_queue.submit_job(
            request.cert_pem,
            intermediates=request.intermediates,
            context=request.context
        )
        
        return JobResponse(
            job_id=job_id,
            status="pending"
        )
    
    except Exception as e:
        logger.error(f"Job submission failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/validate-job/{job_id}", response_model=JobResponse, tags=["Validation"])
async def get_job_status(
    job_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Get validation job status and result"""
    job_status = job_queue.get_job_status(job_id)
    
    if not job_status:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return JobResponse(**job_status)

@app.get("/api/certs/{fingerprint}", tags=["Certificates"])
async def get_cert_metadata(
    fingerprint: str,
    api_key: str = Depends(verify_api_key)
):
    """Get certificate metadata by fingerprint"""
    # In production, would query cert database
    raise HTTPException(status_code=501, detail="Not implemented")

@app.post("/api/certs/ingest", tags=["Certificates"])
async def ingest_cert(
    cert_pem: str,
    api_key: str = Depends(verify_api_key)
):
    """Ingest/pin a CA certificate (admin only)"""
    # In production, would require admin role
    raise HTTPException(status_code=501, detail="Not implemented")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
