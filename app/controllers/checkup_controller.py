from flask import Blueprint, render_template, request, jsonify, flash
from app.controllers.helpers import login_required, get_current_user
from app.services.security_checkup_service import SecurityCheckupService

checkup_bp = Blueprint("checkup", __name__, url_prefix="/checkup")

# Curated test samples for Security Checkup
CHECKUP_SAMPLES = {
    "banking_kyc": {
        "title": "Banking KYC Threat (Urgency + Link)",
        "channel": "SMS",
        "text": "Dear customer, your SBI NetBanking a/c is blocked due to incomplete KYC. Verify now at http://sbi-kyc-update.xyz within 24 hours to avoid permanent suspension. Call +91 98765 43210."
    },
    "upi_cashback": {
        "title": "UPI & Payment Cashback Scam",
        "channel": "WhatsApp",
        "text": "Congratulations! You have received a cashback reward of Rs 4,999 on PhonePe. Click here to claim your reward instantly into your bank account via UPI: send money to cashback-reward@ybl."
    },
    "credential_harvesting": {
        "title": "Sensitive Info & OTP Request",
        "channel": "Email",
        "text": "Security Alert: Unusual sign-in attempt detected. To verify your identity, reply with your registered email, ATM PIN, and the OTP sent to your phone number to secure your account."
    }
}

@checkup_bp.route("/", methods=["GET"])
@login_required
def index():
    """Message Security Checkup view."""
    user = get_current_user()
    return render_template(
        "checkup/index.html",
        user=user,
        samples=CHECKUP_SAMPLES,
        checkup=None
    )

@checkup_bp.route("/analyze", methods=["POST"])
@login_required
def analyze():
    """Runs security checkup on submitted text."""
    user = get_current_user()
    data = request.get_json() if request.is_json else request.form.to_dict()
    text = data.get("text", "").strip()

    if not text:
        if request.is_json:
            return jsonify({"success": False, "message": "Please enter message text to check."}), 400
        flash("Please enter message text to check.", "danger")
        return render_template("checkup/index.html", user=user, samples=CHECKUP_SAMPLES, checkup=None)

    checkup = SecurityCheckupService.evaluate(text)

    if request.is_json:
        return jsonify({"success": True, "data": checkup}), 200

    flash("Message security checkup completed successfully!", "success")
    return render_template(
        "checkup/index.html",
        user=user,
        samples=CHECKUP_SAMPLES,
        checkup=checkup,
        input_text=text
    )
