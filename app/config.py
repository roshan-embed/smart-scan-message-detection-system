import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base application configuration."""
    SECRET_KEY = os.getenv("SECRET_KEY", "smart-scam-detection-secure-key-2026-distilbert-mvc")
    
    # Session Configuration
    SESSION_COOKIE_NAME = os.getenv("SESSION_COOKIE_NAME", "scam_detect_session")
    PERMANENT_SESSION_LIFETIME = timedelta(
        hours=int(os.getenv("PERMANENT_SESSION_LIFETIME_HOURS", 24))
    )
    SESSION_COOKIE_HTTPONLY = os.getenv("SESSION_COOKIE_HTTPONLY", "True").lower() == "true"
    SESSION_COOKIE_SAMESITE = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")
    
    # Database Configuration (MySQL)
    DB_TYPE = os.getenv("DB_TYPE", "mysql")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", 3306))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "smart_scam_detection")
    
    # Fallback to local SQLite if MySQL server is not locally running
    ENABLE_SQLITE_FALLBACK = os.getenv("ENABLE_SQLITE_FALLBACK", "True").lower() == "true"
    _base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    _default_db = os.path.join(_base_dir, os.getenv("SQLITE_DB_PATH", "smart_scam_detection.db"))

    # Support writable SQLite storage on Vercel Serverless environment
    if os.getenv("VERCEL"):
        _tmp_db = "/tmp/smart_scam_detection.db"
        if not os.path.exists(_tmp_db) and os.path.exists(_default_db):
            try:
                import shutil
                shutil.copyfile(_default_db, _tmp_db)
            except Exception:
                pass
        SQLITE_DB_PATH = _tmp_db if os.path.exists(_tmp_db) else _default_db
    else:
        SQLITE_DB_PATH = _default_db
    
    # Security parameters
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_TIME_MINUTES = 15
