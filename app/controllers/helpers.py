from functools import wraps
from flask import session, redirect, url_for, flash, request, jsonify
from app.models.user_model import UserModel

def get_current_user():
    """Retrieve logged in user object if valid session exists."""
    user_id = session.get("user_id")
    session_token = session.get("session_token")
    if not user_id or not session_token:
        return None
    
    # Verify session is still marked active in database
    session_info = UserModel.get_session_by_token(session_token)
    if not session_info or session_info["user_id"] != user_id:
        # Invalidated or expired session
        session.clear()
        return None
    
    # Touch activity
    UserModel.update_session_activity(session_token)
    return UserModel.get_by_id(user_id)

def login_required(f):
    """Decorator to enforce authenticated sessions on protected routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            if request.is_json:
                return jsonify({"success": False, "message": "Authentication required. Please log in."}), 401
            flash("Please sign in to access this page.", "warning")
            return redirect(url_for("auth.login", next=request.path))
        return f(*args, **kwargs)
    return decorated_function

def get_client_ip():
    """Extract client IP address handling proxies safely."""
    if request.headers.get("X-Forwarded-For"):
        return request.headers["X-Forwarded-For"].split(",")[0].strip()
    return request.remote_addr or "127.0.0.1"
