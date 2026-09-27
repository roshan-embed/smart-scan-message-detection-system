import re
import os
import sqlite3
import logging
from app.config import Config

logger = logging.getLogger(__name__)

# Try importing pymysql
try:
    import pymysql
    import pymysql.cursors
    PYMYSQL_AVAILABLE = True
except ImportError:
    PYMYSQL_AVAILABLE = False
    logger.warning("PyMySQL is not installed. Will use SQLite fallback.")

class DatabaseManager:
    """
    Data Tier Database Manager:
    Manages connections, execution of queries, transaction commits,
    and automatic fallback between MySQL and SQLite.
    """
    _instance = None
    _active_db_type = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._init_connection()
        return cls._instance

    def _init_connection(self):
        """Detect and initialize database connection."""
        self._active_db_type = None
        
        # 1. Attempt MySQL connection if pymysql is present
        if PYMYSQL_AVAILABLE and Config.DB_TYPE.lower() == "mysql":
            try:
                # Test connection to MySQL server
                conn = pymysql.connect(
                    host=Config.DB_HOST,
                    port=Config.DB_PORT,
                    user=Config.DB_USER,
                    password=Config.DB_PASSWORD,
                    database=Config.DB_NAME,
                    cursorclass=pymysql.cursors.DictCursor,
                    autocommit=False,
                    connect_timeout=3
                )
                conn.close()
                self._active_db_type = "mysql"
                logger.info(f"Connected successfully to MySQL database '{Config.DB_NAME}' on {Config.DB_HOST}:{Config.DB_PORT}")
                return
            except Exception as e:
                logger.warning(f"MySQL connection failed: {e}")
                if not Config.ENABLE_SQLITE_FALLBACK:
                    raise ConnectionError(f"Could not connect to MySQL: {e}")
        
        # 2. Fallback to SQLite if allowed
        if Config.ENABLE_SQLITE_FALLBACK:
            self._active_db_type = "sqlite"
            self._init_sqlite_schema()
            logger.info(f"Running on SQLite fallback: {Config.SQLITE_DB_PATH}")
        else:
            raise RuntimeError("Database could not be initialized.")

    def get_active_db_type(self):
        return self._active_db_type

    def get_connection(self):
        """Returns a database connection based on active DB type."""
        if self._active_db_type == "mysql":
            return pymysql.connect(
                host=Config.DB_HOST,
                port=Config.DB_PORT,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                database=Config.DB_NAME,
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=False
            )
        else:
            db_dir = os.path.dirname(os.path.abspath(Config.SQLITE_DB_PATH))
            if db_dir:
                os.makedirs(db_dir, exist_ok=True)
            conn = sqlite3.connect(Config.SQLITE_DB_PATH)
            conn.row_factory = sqlite3.Row
            return conn

    def _init_sqlite_schema(self):
        """Initializes tables for SQLite if using fallback mode."""
        db_dir = os.path.dirname(os.path.abspath(Config.SQLITE_DB_PATH))
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        conn = sqlite3.connect(Config.SQLITE_DB_PATH)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                phone_number TEXT,
                bio TEXT,
                role TEXT DEFAULT 'user',
                status TEXT DEFAULT 'active',
                last_login_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # User sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_token TEXT NOT NULL UNIQUE,
                ip_address TEXT DEFAULT '127.0.0.1',
                user_agent TEXT,
                device_info TEXT DEFAULT 'Desktop / Web Browser',
                login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active INTEGER DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
        """)

        # Login audit logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS login_audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                attempted_identifier TEXT NOT NULL,
                status TEXT NOT NULL,
                ip_address TEXT DEFAULT '127.0.0.1',
                user_agent TEXT,
                failure_reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
            );
        """)

        # Scanned messages table (Module 2: Smart Message Scanner)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scanned_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                message_type TEXT NOT NULL DEFAULT 'sms',
                sender_info TEXT,
                subject TEXT,
                raw_content TEXT NOT NULL,
                sanitized_content TEXT NOT NULL,
                char_count INTEGER NOT NULL DEFAULT 0,
                word_count INTEGER NOT NULL DEFAULT 0,
                extracted_urls TEXT,
                extracted_phones TEXT,
                extracted_emails TEXT,
                has_urgency INTEGER DEFAULT 0,
                scan_status TEXT DEFAULT 'ready',
                threat_verdict TEXT DEFAULT 'Pending Analysis',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
        """)

        conn.commit()
        conn.close()

    def execute_query(self, query: str, params: tuple = None, fetch: str = None, commit: bool = True):
        """
        Executes a parameterized SQL query.
        
        :param query: SQL statement (uses %s placeholders)
        :param params: Tuple or dict of parameters
        :param fetch: 'one', 'all', or None
        :param commit: Whether to commit changes
        :return: Fetched dict/list of dicts, or lastrowid / affected rows
        """
        conn = self.get_connection()
        try:
            # Handle placeholder adaptation if on SQLite
            sql = query
            if self._active_db_type == "sqlite":
                # Convert %s placeholders to ?
                sql = query.replace("%s", "?")
                cursor = conn.cursor()
            else:
                cursor = conn.cursor()

            params_to_pass = params if params is not None else ()
            cursor.execute(sql, params_to_pass)

            result = None
            if fetch == "one":
                row = cursor.fetchone()
                if row:
                    result = dict(row)
            elif fetch == "all":
                rows = cursor.fetchall()
                result = [dict(r) for r in rows] if rows else []
            else:
                if self._active_db_type == "mysql":
                    result = cursor.lastrowid or cursor.rowcount
                else:
                    result = cursor.lastrowid or cursor.rowcount

            if commit:
                conn.commit()

            cursor.close()
            return result
        except Exception as e:
            if commit:
                conn.rollback()
            logger.error(f"Database error executing query [{query}]: {e}")
            raise e
        finally:
            conn.close()

# Singleton accessor
db = DatabaseManager()
