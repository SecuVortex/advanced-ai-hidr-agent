import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)


class Config:
    VIRUSTOTAL_API_KEY: Optional[str] = os.getenv('VIRUSTOTAL_API_KEY')
    GOOGLE_API_KEY: Optional[str] = os.getenv('GOOGLE_API_KEY')
    OPENAI_API_KEY: Optional[str] = os.getenv('OPENAI_API_KEY')
    MISTRAL_API_KEY: Optional[str] = os.getenv('MISTRAL_API_KEY')
    LLM_PROVIDER: str = os.getenv('LLM_PROVIDER', 'gemini')
    REQUIRE_HUMAN_APPROVAL: bool = os.getenv('REQUIRE_HUMAN_APPROVAL', 'true'
        ).lower() == 'true'
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    MAX_THREAT_SCORE: int = int(os.getenv('MAX_THREAT_SCORE', 10))
    QUARANTINE_ENABLED: bool = os.getenv('QUARANTINE_ENABLED', 'true').lower(
        ) == 'true'
    API_TIMEOUT: int = int(os.getenv('API_TIMEOUT', 20))
    BASE_DIR: Path = Path(__file__).parent.parent
    QUARANTINE_DIR: Path = BASE_DIR / 'quarantine'
    BACKUP_DIR: Path = BASE_DIR / 'backup'
    LOGS_DIR: Path = BASE_DIR / 'logs'
    REPORTS_DIR: Path = BASE_DIR / 'reports'

    @classmethod
    def validate(cls):
        if (not cls.VIRUSTOTAL_API_KEY or cls.VIRUSTOTAL_API_KEY ==
            'your_virustotal_api_key_here'):
            print(
                '⚠️  Warning: VIRUSTOTAL_API_KEY not set. Threat intelligence will be disabled.'
                )
        if not cls.GOOGLE_API_KEY and cls.LLM_PROVIDER == 'gemini':
            print(
                '⚠️  Warning: GOOGLE_API_KEY not set. AI analysis will be limited.'
                )
            return False
        return True

    @classmethod
    def get_llm_config(cls) ->dict:
        return {'provider': cls.LLM_PROVIDER, 'google_api_key': cls.
            GOOGLE_API_KEY, 'openai_api_key': cls.OPENAI_API_KEY,
            'mistral_api_key': cls.MISTRAL_API_KEY}

    @classmethod
    def ensure_directories(cls):
        for directory in [cls.QUARANTINE_DIR, cls.BACKUP_DIR, cls.LOGS_DIR,
            cls.REPORTS_DIR]:
            directory.mkdir(exist_ok=True, parents=True)


Config.validate()
Config.ensure_directories()
