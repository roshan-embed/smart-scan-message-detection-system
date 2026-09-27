from flask import Blueprint, render_template, request, jsonify, flash
from app.controllers.helpers import login_required, get_current_user
from app.services.risk_scoring_service import RiskScoringService

risk_bp = Blueprint("risk", __name__, url_prefix="/risk")

RISK_SAMPLES = {
    "banking_kyc_scam": {
        "title": "SBI KYC Phishing",
        "channel": "SMS",
        "risk_tier": "High Risk",
        "expected_risk": "High Risk (87/100)",
        "score": "87/100",
        "badge_class": "badge-danger",
        "text": "Dear customer, your SBI NetBanking a/c is blocked due to incomplete KYC. Verify now at http://sbi-kyc-update.xyz within 24 hours to avoid permanent suspension. Call +91 98765 43210."
    },
    "lottery_prize_scam": {
        "title": "WhatsApp Lottery Fraud",
        "channel": "WhatsApp",
        "risk_tier": "High Risk",
        "expected_risk": "High Risk (84/100)",
        "score": "84/100",
        "badge_class": "badge-danger",
        "text": "Congratulations! You have won Rs 25,00,000 in KBC Lucky Draw! Claim your prize money right now by sending registration fee via UPI to kbc-rewards@okhdfcbank."
    },
    "moderate_suspicious": {
        "title": "Unverified Cloud Link",
        "channel": "SMS",
        "risk_tier": "Suspicious",
        "expected_risk": "Suspicious (40/100)",
        "score": "40/100",
        "badge_class": "badge-warning",
        "text": "Hi, please check out the latest photos from yesterday's team meetup here: http://photo-drop-share-v9.xyz/album?id=842"
    },
    "benign_meeting": {
        "title": "Office Lunch Meetup",
        "channel": "SMS",
        "risk_tier": "Safe",
        "expected_risk": "Safe (3/100)",
        "score": "3/100",
        "badge_class": "badge-safe",
        "text": "Hey Rahul, let's meet for lunch at the office cafeteria around 1pm tomorrow to discuss the project presentation. Thanks!"
    }
}

@risk_bp.route("/", methods=["GET"])
@login_required
def index():
    """Module 6: Risk Assessment & Threat Scoring view."""
    user = get_current_user()
    return render_template(
        "risk/index.html",
        user=user,
        samples=RISK_SAMPLES,
        assessment=None
    )

@risk_bp.route("/assess", methods=["POST"])
@login_required
def assess():
    """Calculates overall risk score combining Scam Indicators and AI Prediction."""
    user = get_current_user()
    data = request.get_json() if request.is_json else request.form.to_dict()
    text = data.get("text", "").strip()

    if not text:
        if request.is_json:
            return jsonify({"success": False, "message": "Please enter message text to assess."}), 400
        flash("Please enter message text to assess risk.", "danger")
        return render_template("risk/index.html", user=user, samples=RISK_SAMPLES, assessment=None)

    assessment = RiskScoringService.assess_risk(text)

    if request.is_json:
        return jsonify({"success": True, "data": assessment}), 200

    flash("Risk assessment & threat scoring calculated successfully!", "success")
    return render_template(
        "risk/index.html",
        user=user,
        samples=RISK_SAMPLES,
        assessment=assessment,
        input_text=text
    )
