from datetime import datetime
from app.models.db import db

class UserModel:
    """
    Data Tier / Model:
    Handles persistent storage operations for Users, User Sessions, and Audit Logs.
    """

    @staticmethod
    def get_by_id(user_id: int):
        """Fetch user by primary key ID."""
        sql = "SELECT * FROM users WHERE id = %s"
        return db.execute_query(sql, (user_id,), fetch="one")

    @staticmethod
    def get_by_email(email: str):
        """Fetch user by unique email address."""
        sql = "SELECT * FROM users WHERE LOWER(email) = LOWER(%s)"
        return db.execute_query(sql, (email.strip(),), fetch="one")

    @staticmethod
    def get_by_username(username: str):
        """Fetch user by unique username."""
        sql = "SELECT * FROM users WHERE LOWER(username) = LOWER(%s)"
        return db.execute_query(sql, (username.strip(),), fetch="one")

    @staticmethod
    def get_by_identifier(identifier: str):
        """Fetch user by either email or username."""
        sql = "SELECT * FROM users WHERE LOWER(email) = LOWER(%s) OR LOWER(username) = LOWER(%s)"
        clean_id = identifier.strip()
        return db.execute_query(sql, (clean_id, clean_id), fetch="one")

    @staticmethod
    def create(username: str, email: str, password_hash: str, first_name: str, 
               last_name: str, phone_number: str = None, role: str = 'user'):
        """Insert a newly registered user."""
        sql = """
            INSERT INTO users (username, email, password_hash, first_name, last_name, phone_number, role, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'active')
        """
        return db.execute_query(
            sql, 
            (username.strip(), email.strip().lower(), password_hash, first_name.strip(), last_name.strip(), phone_number, role),
            commit=True
        )

    @staticmethod
    def update_profile(user_id: int, first_name: str, last_name: str, phone_number: str = None, bio: str = None):
        """Update user profile personal details."""
        sql = """
            UPDATE users 
            SET first_name = %s, last_name = %s, phone_number = %s, bio = %s
            WHERE id = %s
        """
        return db.execute_query(
            sql,
            (first_name.strip(), last_name.strip(), phone_number.strip() if phone_number else None, bio.strip() if bio else None, user_id),
            commit=True
        )

    @staticmethod
    def update_password(user_id: int, new_password_hash: str):
        """Update user password hash."""
        sql = "UPDATE users SET password_hash = %s WHERE id = %s"
        return db.execute_query(sql, (new_password_hash, user_id), commit=True)

    @staticmethod
    def update_last_login(user_id: int):
        """Update last login timestamp."""
        now = datetime.now()
        sql = "UPDATE users SET last_login_at = %s WHERE id = %s"
        return db.execute_query(sql, (now, user_id), commit=True)

    # ------------------ Session Management ------------------ #

    @staticmethod
    def create_session(user_id: int, session_token: str, ip_address: str, user_agent: str, device_info: str):
        """Persist a new active login session."""
        sql = """
            INSERT INTO user_sessions (user_id, session_token, ip_address, user_agent, device_info, is_active)
            VALUES (%s, %s, %s, %s, %s, 1)
        """
        return db.execute_query(
            sql,
            (user_id, session_token, ip_address, user_agent, device_info),
            commit=True
        )

    @staticmethod
    def get_session_by_token(session_token: str):
        """Fetch session information by session token."""
        sql = """
            SELECT s.*, u.username, u.email, u.role, u.status 
            FROM user_sessions s
            JOIN users u ON s.user_id = u.id
            WHERE s.session_token = %s AND s.is_active = 1
        """
        return db.execute_query(sql, (session_token,), fetch="one")

    @staticmethod
    def update_session_activity(session_token: str):
        """Touch session timestamp for activity monitoring."""
        now = datetime.now()
        sql = "UPDATE user_sessions SET last_activity = %s WHERE session_token = %s"
        return db.execute_query(sql, (now, session_token), commit=True)

    @staticmethod
    def get_active_sessions_for_user(user_id: int):
        """Retrieve all active login sessions for a user."""
        sql = """
            SELECT id, session_token, ip_address, user_agent, device_info, login_time, last_activity, is_active
            FROM user_sessions 
            WHERE user_id = %s AND is_active = 1
            ORDER BY last_activity DESC
        """
        return db.execute_query(sql, (user_id,), fetch="all")

    @staticmethod
    def deactivate_session(session_token: str):
        """Log out / invalidate a specific session."""
        sql = "UPDATE user_sessions SET is_active = 0 WHERE session_token = %s"
        return db.execute_query(sql, (session_token,), commit=True)

    @staticmethod
    def deactivate_all_other_sessions(user_id: int, current_session_token: str):
        """Invalidate all other sessions except current."""
        sql = "UPDATE user_sessions SET is_active = 0 WHERE user_id = %s AND session_token != %s"
        return db.execute_query(sql, (user_id, current_session_token), commit=True)

    # ------------------ Audit & Security ------------------ #

    @staticmethod
    def log_audit(attempted_identifier: str, status: str, ip_address: str, 
                  user_agent: str, failure_reason: str = None, user_id: int = None):
        """Record login audit event for security monitoring."""
        sql = """
            INSERT INTO login_audit_logs (user_id, attempted_identifier, status, ip_address, user_agent, failure_reason)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        return db.execute_query(
            sql,
            (user_id, attempted_identifier, status, ip_address, user_agent, failure_reason),
            commit=True
        )

    @staticmethod
    def get_user_audit_logs(user_id: int, limit: int = 10):
        """Get recent login attempts for user security review."""
        sql = """
            SELECT id, attempted_identifier, status, ip_address, failure_reason, created_at
            FROM login_audit_logs 
            WHERE user_id = %s 
            ORDER BY created_at DESC 
            LIMIT %s
        """
        # When using SQLite, handle limit
        return db.execute_query(sql, (user_id, limit), fetch="all")
