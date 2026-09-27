from flask import Blueprint, render_template, request, jsonify, flash
from app.controllers.helpers import login_required, get_current_user
from app.services.scam_indicator_service import ScamIndicatorService

indicators_bp = Blueprint("indicators", __name__, url_prefix="/indicators")

INDICATOR_SAMPLES = {
    "high_risk_five_signs": {
        "title": "5 Warning Signs (Banking, Link, Urgency, KYC, Threat)",
        "channel": "SMS",
        "text": "URGENT: Your HDFC Bank account is scheduled to be blocked today! Complete mandatory KYC verification immediately within 24 hours at http://hdfc-netbanking-verify.xyz to prevent permanent suspension."
    },
    "otp_phish": {
        "title": "OTP & Personal Information Theft",
        "channel": "Email",
        "text": "Dear user, we detected an unauthorized login to your account. Enter your NetBanking Password and the OTP received on SMS at http://secure-login-protect.top to unblock your account."
    },
    "lottery_upi": {
        "title": "Prize Lottery & UPI Payment Solicitation",
        "channel": "WhatsApp",
        "text": "Congratulations! You won Rs 25,00,000 in KBC Lucky Draw! To claim your prize money, send Rs 2,500 registration fee via UPI to kbc-rewards@okhdfcbank right now."
    }
}

@indicators_bp.route("/", methods=["GET"])
@login_required
def index():
    """Scam Indicator Report view."""
    user = get_current_user()
    return render_template(
        "indicators/index.html",
        user=user,
        samples=INDICATOR_SAMPLES,
        report=None
    )

@indicators_bp.route("/analyze", methods=["POST"])
@login_required
def analyze():
    """Generates scam indicator report for submitted text."""
    user = get_current_user()
    data = request.get_json() if request.is_json else request.form.to_dict()
    text = data.get("text", "").strip()

    if not text:
        if request.is_json:
            return jsonify({"success": False, "message": "Please enter message text to analyze."}), 400
        flash("Please enter message text to analyze.", "danger")
        return render_template("indicators/index.html", user=user, samples=INDICATOR_SAMPLES, report=None)

    report = ScamIndicatorService.generate_report(text)

    if request.is_json:
        return jsonify({"success": True, "data": report}), 200

    flash("Scam indicator evaluation complete!", "success")
    return render_template(
        "indicators/index.html",
        user=user,
        samples=INDICATOR_SAMPLES,
        report=report,
        input_text=text
    )
