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
    
    # Database Configuration (MySQL / SQLite)
    # When running in Vercel Serverless environment, default directly to SQLite
    if os.getenv("VERCEL"):
        DB_TYPE = "sqlite"
        ENABLE_SQLITE_FALLBACK = True
    else:
        DB_TYPE = os.getenv("DB_TYPE", "mysql")
        ENABLE_SQLITE_FALLBACK = os.getenv("ENABLE_SQLITE_FALLBACK", "True").lower() == "true"

    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", 3306))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "smart_scam_detection")
    
    _base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    _default_db = os.path.join(_base_dir, "smart_scam_detection.db")

    # Support writable SQLite storage on Vercel Serverless environment
    if os.getenv("VERCEL"):
        import tempfile
        _tmp_db = os.path.join(tempfile.gettempdir(), "smart_scam_detection.db")
        try:
            os.makedirs(tempfile.gettempdir(), exist_ok=True)
            if not os.path.exists(_tmp_db) and os.path.exists(_default_db):
                import shutil
                shutil.copyfile(_default_db, _tmp_db)
        except Exception:
            pass
        SQLITE_DB_PATH = _tmp_db
    else:
        SQLITE_DB_PATH = os.path.join(_base_dir, os.getenv("SQLITE_DB_PATH", "smart_scam_detection.db"))
    
    # Security parameters
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_TIME_MINUTES = 15
