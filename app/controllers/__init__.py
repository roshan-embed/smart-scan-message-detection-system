from app.controllers.auth_controller import auth_bp
from app.controllers.profile_controller import profile_bp
from app.controllers.dashboard_controller import dashboard_bp
from app.controllers.scanner_controller import scanner_bp
from app.controllers.preprocessor_controller import preprocessor_bp
from app.controllers.checkup_controller import checkup_bp
from app.controllers.indicators_controller import indicators_bp

__all__ = [
    "auth_bp",
    "profile_bp",
    "dashboard_bp",
    "scanner_bp",
    "preprocessor_bp",
    "checkup_bp",
    "indicators_bp"
]
