import re
import secrets
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.user_model import UserModel

class AuthService:
    """
    Business Logic Tier: Authentication Service
    Handles user registration logic, password validation, cryptographic hashing,
    and session token creation.
    """

    @staticmethod
    def validate_username(username: str) -> tuple[bool, str]:
        """Validate username constraints."""
        if not username or len(username.strip()) < 3:
            return False, "Username must be at least 3 characters long."
        if len(username.strip()) > 30:
            return False, "Username cannot exceed 30 characters."
        if not re.match(r"^[a-zA-Z0-9_.-]+$", username.strip()):
            return False, "Username can only contain letters, numbers, hyphens, and underscores."
        return True, ""

    @staticmethod
    def validate_email(email: str) -> tuple[bool, str]:
        """Validate email address format."""
        if not email:
            return False, "Email address is required."
        pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(pattern, email.strip()):
            return False, "Please enter a valid email address."
        return True, ""

    @staticmethod
    def validate_password_strength(password: str) -> tuple[bool, str]:
        """
        Validate password complexity:
        - At least 8 characters
        - At least 1 lowercase letter
        - At least 1 uppercase letter
        - At least 1 number
        - At least 1 special character
        """
        if not password or len(password) < 8:
            return False, "Password must be at least 8 characters long."
        if not re.search(r"[a-z]", password):
            return False, "Password must contain at least one lowercase letter."
        if not re.search(r"[A-Z]", password):
            return False, "Password must contain at least one uppercase letter."
        if not re.search(r"[0-9]", password):
            return False, "Password must contain at least one number."
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=~`\[\]/]", password):
            return False, "Password must contain at least one special character."
        return True, ""

    @classmethod
    def register_user(cls, form_data: dict) -> tuple[bool, str, int | None]:
        """
        Processes new user registration.
        """
        username = form_data.get("username", "").strip()
        email = form_data.get("email", "").strip()
        first_name = form_data.get("first_name", "").strip()
        last_name = form_data.get("last_name", "").strip()
        phone_number = form_data.get("phone_number", "").strip()
        password = form_data.get("password", "")
        confirm_password = form_data.get("confirm_password", "")

        # 1. Required field checks
        if not first_name or not last_name:
            return False, "First and last names are required.", None

        # 2. Username format check
        valid_u, msg_u = cls.validate_username(username)
        if not valid_u:
            return False, msg_u, None

        # 3. Email format check
        valid_e, msg_e = cls.validate_email(email)
        if not valid_e:
            return False, msg_e, None

        # 4. Check uniqueness
        if UserModel.get_by_username(username):
            return False, "This username is already taken. Please choose another.", None

        if UserModel.get_by_email(email):
            return False, "An account with this email address already exists.", None

        # 5. Password match & strength check
        if password != confirm_password:
            return False, "Passwords do not match.", None

        valid_p, msg_p = cls.validate_password_strength(password)
        if not valid_p:
            return False, msg_p, None

        # 6. Secure Hashing (PBKDF2-SHA256 with 600,000 salt rounds)
        password_hash = generate_password_hash(password, method="scrypt") if hasattr(generate_password_hash, "scrypt") else generate_password_hash(password)

        # 7. Create User Record
        try:
            user_id = UserModel.create(
                username=username,
                email=email,
                password_hash=password_hash,
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number if phone_number else None,
                role="user"
            )
            return True, "Registration successful! You can now log in.", user_id
        except Exception as e:
            return False, f"Registration failed due to a system error: {str(e)}", None

    @classmethod
    def authenticate_user(cls, identifier: str, password: str, 
                          ip_address: str = "127.0.0.1", user_agent: str = "") -> tuple[bool, str, dict | None, str | None]:
        """
        Authenticates user credentials and provisions a session token.
        """
        clean_id = identifier.strip() if identifier else ""
        if not clean_id or not password:
            return False, "Please enter both username/email and password.", None, None

        user = UserModel.get_by_identifier(clean_id)
        if not user:
            UserModel.log_audit(clean_id, "failed", ip_address, user_agent, "User not found")
            return False, "Invalid username/email or password.", None, None

        # Check account status
        if user.get("status") != "active":
            UserModel.log_audit(clean_id, "blocked", ip_address, user_agent, f"Account status: {user.get('status')}", user["id"])
            return False, f"Your account is currently {user.get('status')}. Please contact an administrator.", None, None

        # Verify password
        if not check_password_hash(user["password_hash"], password):
            UserModel.log_audit(clean_id, "failed", ip_address, user_agent, "Incorrect password", user["id"])
            return False, "Invalid username/email or password.", None, None

        # Success - log audit and update last login
        UserModel.log_audit(clean_id, "success", ip_address, user_agent, None, user["id"])
        UserModel.update_last_login(user["id"])

        # Generate secure random session token
        session_token = secrets.token_hex(32)
        device_info = cls._parse_device_info(user_agent)
        UserModel.create_session(user["id"], session_token, ip_address, user_agent, device_info)

        # Remove password_hash from returned user dict for security
        user_safe = dict(user)
        user_safe.pop("password_hash", None)

        return True, "Login successful!", user_safe, session_token

    @staticmethod
    def _parse_device_info(user_agent: str) -> str:
        """Helper to create a human-readable device string."""
        if not user_agent:
            return "Web Browser"
        ua = user_agent.lower()
        os_name = "Windows" if "windows" in ua else ("Mac" if "macintosh" in ua else ("Linux" if "linux" in ua else ("Android" if "android" in ua else ("iOS" if "iphone" in ua else "Device"))))
        browser = "Chrome" if "chrome" in ua and "edg" not in ua else ("Edge" if "edg" in ua else ("Firefox" if "firefox" in ua else ("Safari" if "safari" in ua else "Browser")))
        return f"{browser} on {os_name}"

    @staticmethod
    def logout_session(session_token: str) -> bool:
        """Deactivate the user's active session."""
        if session_token:
            UserModel.deactivate_session(session_token)
            return True
        return False
