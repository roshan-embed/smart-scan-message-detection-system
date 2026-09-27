from flask import Blueprint, render_template
from app.controllers.helpers import login_required, get_current_user
from app.models.message_model import MessageModel

analytics_bp = Blueprint("analytics", __name__, url_prefix="/analytics")

@analytics_bp.route("/", methods=["GET"])
@login_required
def index():
    """Renders Scam Trends & Analytics view matching the enterprise dashboard."""
    user = get_current_user()
    stats = MessageModel.get_user_stats(user["id"])

    # Sample realistic analytics telemetry matching mockup
    top_keywords = [
        {"keyword": "KYC", "count": 48, "trend": "+12%"},
        {"keyword": "OTP", "count": 42, "trend": "+8%"},
        {"keyword": "Prize", "count": 37, "trend": "+15%"},
        {"keyword": "Urgent", "count": 29, "trend": "-3%"},
        {"keyword": "Click", "count": 26, "trend": "+5%"}
    ]

    categories = [
        {"name": "Financial", "percentage": 35, "color": "#00897B"},
        {"name": "KYC / Bank", "percentage": 25, "color": "#F9A825"},
        {"name": "Lottery", "percentage": 15, "color": "#C62828"},
        {"name": "Job / Work", "percentage": 15, "color": "#1976D2"},
        {"name": "Other", "percentage": 10, "color": "#8E24AA"}
    ]

    return render_template(
        "analytics/index.html",
        user=user,
        stats=stats,
        top_keywords=top_keywords,
        categories=categories
    )
