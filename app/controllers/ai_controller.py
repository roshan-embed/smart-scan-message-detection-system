from flask import Blueprint, render_template, request, jsonify, flash
from app.controllers.helpers import login_required, get_current_user
from app.services.distilbert_service import DistilBertService

ai_bp = Blueprint("ai", __name__, url_prefix="/ai")

AI_SAMPLES = {
    "banking_kyc_scam": {
        "title": "Banking KYC Scam (Prediction: SCAM ~91%)",
        "channel": "SMS",
        "text": "Dear customer, your SBI NetBanking a/c is blocked due to incomplete KYC. Verify now at http://sbi-kyc-update.xyz within 24 hours to avoid permanent suspension. Call +91 98765 43210."
    },
    "lottery_prize_scam": {
        "title": "Lottery & Prize Fraud (Prediction: SCAM ~94%)",
        "channel": "WhatsApp",
        "text": "Congratulations! You have won Rs 25,00,000 in KBC Lucky Draw! Claim your prize money right now by sending registration fee via UPI to kbc-rewards@okhdfcbank."
    },
    "benign_meeting": {
        "title": "Legitimate Message (Prediction: SAFE ~96%)",
        "channel": "SMS",
        "text": "Hey Rahul, let's meet for lunch at the office cafeteria around 1pm tomorrow to discuss the project presentation. Thanks!"
    }
}

@ai_bp.route("/", methods=["GET"])
@login_required
def index():
    """Module 5: AI Scam Classification view."""
    user = get_current_user()
    return render_template(
        "ai/index.html",
        user=user,
        samples=AI_SAMPLES,
        analysis=None
    )

@ai_bp.route("/classify", methods=["POST"])
@login_required
def classify():
    """Executes local DistilBERT classification on submitted message."""
    user = get_current_user()
    data = request.get_json() if request.is_json else request.form.to_dict()
    text = data.get("text", "").strip()

    if not text:
        if request.is_json:
            return jsonify({"success": False, "message": "Please enter message text to classify."}), 400
        flash("Please enter message text to classify.", "danger")
        return render_template("ai/index.html", user=user, samples=AI_SAMPLES, analysis=None)

    analysis = DistilBertService.classify(text)

    if request.is_json:
        return jsonify({"success": True, "data": analysis}), 200

    flash("Local DistilBERT classification executed successfully!", "success")
    return render_template(
        "ai/index.html",
        user=user,
        samples=AI_SAMPLES,
        analysis=analysis,
        input_text=text
    )
