from werkzeug.security import generate_password_hash, check_password_hash
from app.models.user_model import UserModel
from app.services.auth_service import AuthService

class UserService:
    """
    Business Logic Tier: User & Profile Management Service
    Encapsulates profile inspection, updating user info, password rotation,
    and managing active sessions.
    """

    @staticmethod
    def get_user_profile(user_id: int) -> dict | None:
        """Fetch sanitized user profile."""
        user = UserModel.get_by_id(user_id)
        if user:
            user_safe = dict(user)
            user_safe.pop("password_hash", None)
            return user_safe
        return None

    @staticmethod
    def update_profile(user_id: int, form_data: dict) -> tuple[bool, str, dict | None]:
        """Validate and update user profile details."""
        first_name = form_data.get("first_name", "").strip()
        last_name = form_data.get("last_name", "").strip()
        phone_number = form_data.get("phone_number", "").strip()
        bio = form_data.get("bio", "").strip()

        if not first_name or not last_name:
            return False, "First Name and Last Name cannot be empty.", None

        if len(first_name) > 50 or len(last_name) > 50:
            return False, "Name cannot exceed 50 characters.", None

        if phone_number and len(phone_number) > 25:
            return False, "Phone number is too long.", None

        try:
            UserModel.update_profile(user_id, first_name, last_name, phone_number, bio)
            updated_user = UserService.get_user_profile(user_id)
            return True, "Profile updated successfully.", updated_user
        except Exception as e:
            return False, f"Failed to update profile: {str(e)}", None

    @staticmethod
    def change_password(user_id: int, form_data: dict) -> tuple[bool, str]:
        """
        Securely handles password change:
        1. Checks current password against stored hash.
        2. Validates new password strength.
        3. Prevents re-using the exact same password.
        4. Verifies confirmation match.
        5. Updates hash in persistent store.
        """
        current_password = form_data.get("current_password", "")
        new_password = form_data.get("new_password", "")
        confirm_new_password = form_data.get("confirm_new_password", "")

        if not current_password or not new_password or not confirm_new_password:
            return False, "All password fields are required."

        user = UserModel.get_by_id(user_id)
        if not user:
            return False, "User account not found."

        # Verify current password
        if not check_password_hash(user["password_hash"], current_password):
            return False, "The current password you entered is incorrect."

        # Verify confirmation match
        if new_password != confirm_new_password:
            return False, "The new password and confirmation do not match."

        # Check if new password is identical to old password
        if check_password_hash(user["password_hash"], new_password):
            return False, "New password cannot be the same as your current password."

        # Validate complexity
        is_strong, msg = AuthService.validate_password_strength(new_password)
        if not is_strong:
            return False, msg

        # Hash and persist
        new_hash = generate_password_hash(new_password)
        try:
            UserModel.update_password(user_id, new_hash)
            return True, "Your password has been changed successfully."
        except Exception as e:
            return False, f"Failed to update password: {str(e)}"

    @staticmethod
    def get_user_sessions(user_id: int) -> list:
        """Retrieve all active login sessions for the user."""
        return UserModel.get_active_sessions_for_user(user_id)

    @staticmethod
    def terminate_session(user_id: int, session_token: str) -> bool:
        """Terminate a specific session token belonging to user."""
        session = UserModel.get_session_by_token(session_token)
        if session and session["user_id"] == user_id:
            UserModel.deactivate_session(session_token)
            return True
        return False

    @staticmethod
    def terminate_all_other_sessions(user_id: int, current_token: str) -> bool:
        """Log out from all other devices."""
        UserModel.deactivate_all_other_sessions(user_id, current_token)
        return True

    @staticmethod
    def get_login_history(user_id: int, limit: int = 5) -> list:
        """Retrieve recent security audit logs for the user."""
        return UserModel.get_user_audit_logs(user_id, limit=limit)
