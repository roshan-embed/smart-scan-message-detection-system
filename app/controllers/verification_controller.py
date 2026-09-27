from flask import Blueprint, render_template, request, jsonify, flash
from app.controllers.helpers import login_required, get_current_user
from app.services.url_sender_verification_service import URLSenderVerificationService

verification_bp = Blueprint("verification", __name__, url_prefix="/verification")

@verification_bp.route("/", methods=["GET"])
@login_required
def index():
    """Module 4: URL & Sender Verification Studio."""
    user = get_current_user()
    
    # Preloaded sample for user inspection
    default_url = "http://example.xyz/login"
    default_sender = "ALERT-SBI"
    
    url_res = URLSenderVerificationService.verify_url(default_url)
    sender_res = URLSenderVerificationService.verify_sender(default_sender)

    return render_template(
        "verification/index.html",
        user=user,
        url_input=default_url,
        sender_input=default_sender,
        url_result=url_res,
        sender_result=sender_res
    )

@verification_bp.route("/inspect", methods=["POST"])
@login_required
def inspect():
    """
    Evaluates submitted URL and/or sender identity.
    Returns rendered HTML cards or JSON payload.
    """
    user = get_current_user()
    url_input = request.form.get("url", "").strip() if not request.is_json else request.json.get("url", "").strip()
    sender_input = request.form.get("sender", "").strip() if not request.is_json else request.json.get("sender", "").strip()

    url_result = URLSenderVerificationService.verify_url(url_input) if url_input else None
    sender_result = URLSenderVerificationService.verify_sender(sender_input) if sender_input else None

    if request.is_json:
        return jsonify({
            "success": True,
            "url_result": url_result,
            "sender_result": sender_result
        })

    return render_template(
        "verification/index.html",
        user=user,
        url_input=url_input,
        sender_input=sender_input,
        url_result=url_result,
        sender_result=sender_result
    )
