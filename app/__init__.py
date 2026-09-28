import os
from flask import Flask, render_template
from app.config import Config
from app.controllers.helpers import get_current_user
from app.controllers.auth_controller import auth_bp
from app.controllers.profile_controller import profile_bp
from app.controllers.dashboard_controller import dashboard_bp
from app.controllers.scanner_controller import scanner_bp
from app.controllers.checkup_controller import checkup_bp
from app.controllers.indicators_controller import indicators_bp
from app.controllers.ai_controller import ai_bp
from app.controllers.risk_controller import risk_bp
from app.controllers.analytics_controller import analytics_bp
from app.controllers.ocr_controller import ocr_bp
from app.controllers.verification_controller import verification_bp
from flask import redirect, url_for

def create_app(config_class=Config):
    """
    Application Factory Pattern for Flask MVC + 3-Tier Layered Architecture.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    app = Flask(
        __name__,
        template_folder=os.path.join(base_dir, "templates"),
        static_folder=os.path.join(base_dir, "static")
    )
    
    app.config.from_object(config_class)

    # Register Layer Controllers (Blueprints)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(scanner_bp)
    app.register_blueprint(ocr_bp)
    app.register_blueprint(verification_bp)
    app.register_blueprint(checkup_bp)
    app.register_blueprint(indicators_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(risk_bp)
    app.register_blueprint(analytics_bp)

    # Developer Preprocessor route graceful redirect to user scanner
    @app.route("/preprocessor/")
    @app.route("/preprocessor/<path:subpath>")
    def redirect_preprocessor(subpath=None):
        return redirect(url_for("scanner.index"))

    # Convenience login shortcut redirect
    @app.route("/login")
    def login_shortcut():
        return redirect(url_for("auth.login"))

    # Direct academic Black Book report viewer and print route
    @app.route("/blackbook")
    @app.route("/blackbook/")
    def view_blackbook():
        report_path = os.path.join(os.path.dirname(base_dir), "Black_Book_Report.html")
        if os.path.exists(report_path):
            with open(report_path, "r", encoding="utf-8") as f:
                return f.read()
        return "Black Book report file not found.", 404

    # Global template context processor
    @app.context_processor
    def inject_global_data():
        user = get_current_user()
        return {
            "current_user": user,
            "system_name": "SMART MESSAGE DETECTION",
            "system_subtitle": "Scam & Phishing Analysis Engine"
        }

    # Custom Error Handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template("errors/500.html"), 500

    return app
