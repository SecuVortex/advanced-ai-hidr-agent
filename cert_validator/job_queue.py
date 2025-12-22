"""
Async Job Queue for Certificate Validation
Simplified implementation using threading (production would use Celery/RQ)
"""
import uuid
import logging
import threading
import time
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from queue import Queue
from enum import Enum

logger = logging.getLogger('HIDR.CertValidator.Jobs')

class JobStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class ValidationJob:
    """Represents a validation job"""
    
    def __init__(self, job_id: str, cert_pem: str, intermediates: list, context: dict):
        self.job_id = job_id
        self.cert_pem = cert_pem
        self.intermediates = intermediates
        self.context = context
        self.status = JobStatus.PENDING
        self.result = None
        self.error = None
        self.created_at = datetime.now(timezone.utc)
        self.completed_at = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert job to dictionary"""
        return {
            'job_id': self.job_id,
            'status': self.status.value,
            'result': self.result,
            'error': self.error,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

class JobQueue:
    """Simple job queue with worker thread"""
    
    def __init__(self, validator, max_workers=2):
        self.validator = validator
        self.jobs = {}
        self.queue = Queue()
        self.workers = []
        self.running = False
        self.max_workers = max_workers
    
    def start(self):
        """Start worker threads"""
        if self.running:
            return
        
        self.running = True
        for i in range(self.max_workers):
            worker = threading.Thread(target=self._worker, daemon=True, name=f"CertWorker-{i}")
            worker.start()
            self.workers.append(worker)
        
        logger.info(f"Job queue started with {self.max_workers} workers")
    
    def stop(self):
        """Stop worker threads"""
        self.running = False
        logger.info("Job queue stopped")
    
    def _worker(self):
        """Worker thread that processes jobs"""
        while self.running:
            try:
                job = self.queue.get(timeout=1)
                if job is None:
                    continue
                
                logger.info(f"Processing job {job.job_id}")
                job.status = JobStatus.RUNNING
                
                try:
                    # Perform full validation
                    result = self.validator.validate_chain(
                        job.cert_pem,
                        intermediates=job.intermediates,
                        context=job.context
                    )
                    
                    job.result = result
                    job.status = JobStatus.COMPLETED
                    job.completed_at = datetime.now(timezone.utc)
                    logger.info(f"Job {job.job_id} completed")
                
                except Exception as e:
                    logger.error(f"Job {job.job_id} failed: {e}")
                    job.error = str(e)
                    job.status = JobStatus.FAILED
                    job.completed_at = datetime.now(timezone.utc)
                
                finally:
                    self.queue.task_done()
            
            except Exception as e:
                if self.running:
                    logger.error(f"Worker error: {e}")
                time.sleep(0.1)
    
    def submit_job(self, cert_pem: str, intermediates: list = None, context: dict = None) -> str:
        """Submit a validation job"""
        job_id = str(uuid.uuid4())
        job = ValidationJob(job_id, cert_pem, intermediates or [], context or {})
        
        self.jobs[job_id] = job
        self.queue.put(job)
        
        logger.info(f"Job {job_id} submitted")
        return job_id
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job status and result"""
        job = self.jobs.get(job_id)
        if not job:
            return None
        
        return job.to_dict()
    
    def cleanup_old_jobs(self, max_age_hours=24):
        """Remove old completed jobs"""
        now = datetime.now(timezone.utc)
        to_remove = []
        
        for job_id, job in self.jobs.items():
            if job.completed_at:
                age = (now - job.completed_at).total_seconds() / 3600
                if age > max_age_hours:
                    to_remove.append(job_id)
        
        for job_id in to_remove:
            del self.jobs[job_id]
        
        if to_remove:
            logger.info(f"Cleaned up {len(to_remove)} old jobs")
