from flask import Blueprint, render_template, request, jsonify, flash
from app.controllers.helpers import login_required, get_current_user
from app.services.preprocessor_service import PreprocessorService

preprocessor_bp = Blueprint("preprocessor", __name__, url_prefix="/preprocessor")

# Curated test samples demonstrating specific preprocessing and evasion challenges
PREPROCESSOR_SAMPLES = {
    "obfuscated_phish": {
        "title": "Homoglyph & Zero-Width Obfuscation (Phishing)",
        "channel": "SMS",
        "description": "Uses Cyrillic look-alike letters (а, о, е) and invisible zero-width spaces to bypass filters.",
        "text": "U​R​G​E​N​T: Yоur bаnk аccоunt hаs been lоcked! Cоnfirm detаils аt: https://gооglе-sеcuritу-vеrifу.xyz/lоgin immediаtely or cаll +1 (800) 555-0199."
    },
    "html_email": {
        "title": "HTML Tags & Contractions (Suspension Notice)",
        "channel": "Email",
        "description": "Embedded HTML formatting, contractions (you're, don't, won't), and defanged link.",
        "text": "<html><body>Dear customer,<br><br>You're required to verify your profile immediately. If you don't act now, we won't be able to protect your funds. Click <a href='hxxps[://]verify-account-update[.]com/auth'>here</a> to update your details or write to support@account-security-alert.net.</body></html>"
    },
    "whatsapp_job": {
        "title": "WhatsApp Lottery & Foreign Phone Format",
        "channel": "WhatsApp",
        "description": "WhatsApp formatting with asterisks, multiple phone numbers, and URL shortener.",
        "text": "*Forwarded many times*\n🎉 You've been chosen for daily remote earnings ($300-$800/day). No experience needed! Contact hiring team on WhatsApp: +44 7911 123456 or Telegram: https://t.co/claim_daily_bonus. Text 'YES' to +91 98765 43210."
    }
}

@preprocessor_bp.route("/", methods=["GET"])
@login_required
def index():
    """Preprocessing & Normalization Studio view."""
    user = get_current_user()
    return render_template(
        "preprocessor/index.html",
        user=user,
        samples=PREPROCESSOR_SAMPLES,
        result=None
    )

@preprocessor_bp.route("/process", methods=["POST"])
@login_required
def process():
    """Processes message through the 5-stage preprocessing pipeline."""
    user = get_current_user()
    data = request.get_json() if request.is_json else request.form.to_dict()
    text = data.get("text", "").strip()

    if not text:
        if request.is_json:
            return jsonify({"success": False, "message": "Please provide message text to preprocess."}), 400
        flash("Please provide message text to preprocess.", "danger")
        return render_template("preprocessor/index.html", user=user, samples=PREPROCESSOR_SAMPLES, result=None)

    result = PreprocessorService.process(text)

    if request.is_json:
        return jsonify({"success": True, "data": result}), 200

    flash("Message successfully preprocessed, normalized, and tokenized!", "success")
    return render_template(
        "preprocessor/index.html",
        user=user,
        samples=PREPROCESSOR_SAMPLES,
        result=result,
        input_text=text
    )

@preprocessor_bp.route("/sample/<key>", methods=["GET"])
@login_required
def get_sample(key):
    """Retrieve sample text payload."""
    sample = PREPROCESSOR_SAMPLES.get(key)
    if sample:
        return jsonify({"success": True, "sample": sample})
    return jsonify({"success": False, "message": "Sample not found"}), 404
