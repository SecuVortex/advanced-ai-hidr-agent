"""
Configuration Management for HIDR Multi-Agent System
Loads environment variables and provides centralized configuration.
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)


class Config:
    """Centralized configuration for HIDR Multi-Agent System"""
    
    VIRUSTOTAL_API_KEY: str = os.getenv("VIRUSTOTAL_API_KEY", "")
    
    # System Configuration
    REQUIRE_HUMAN_APPROVAL: bool = os.getenv("REQUIRE_HUMAN_APPROVAL", "true").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    MAX_THREAT_SCORE: int = int(os.getenv("MAX_THREAT_SCORE", "10"))
    QUARANTINE_ENABLED: bool = os.getenv("QUARANTINE_ENABLED", "true").lower() == "true"
    
    # Detection Thresholds
    SUSPICIOUS_THRESHOLD: int = 3  # Threat level >= 3 is suspicious
    CRITICAL_THRESHOLD: int = 7    # Threat level >= 7 is critical
    
    # Timeouts (seconds)
    API_TIMEOUT: int = 10
    PROCESS_TIMEOUT: int = 3
    HUMAN_APPROVAL_TIMEOUT: int = 300  # 5 minutes
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent
    QUARANTINE_DIR: Path = BASE_DIR / "quarantine"
    BACKUP_DIR: Path = BASE_DIR / "backups"
    LOGS_DIR: Path = BASE_DIR / "logs"
    REPORTS_DIR: Path = BASE_DIR / "reports"
    
    @classmethod
    def validate(cls) -> bool:
        return True
    
    @classmethod
    def ensure_directories(cls) -> None:
        """Ensure all required directories exist"""
        for directory in [cls.QUARANTINE_DIR, cls.BACKUP_DIR, cls.LOGS_DIR, cls.REPORTS_DIR]:
            directory.mkdir(exist_ok=True, parents=True)


Config.ensure_directories()
