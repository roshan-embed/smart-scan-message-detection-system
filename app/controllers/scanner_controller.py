from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.controllers.helpers import login_required, get_current_user
from app.services.scanner_service import ScannerService
from app.models.message_model import MessageModel

scanner_bp = Blueprint("scanner", __name__, url_prefix="/scanner")

@scanner_bp.route("/", methods=["GET"])
@login_required
def index():
    """Main Smart Message Scanner view."""
    user = get_current_user()
    recent_scans = MessageModel.get_recent_by_user(user["id"], limit=6)
    samples = ScannerService.get_sample_templates()

    return render_template(
        "scanner/index.html",
        user=user,
        recent_scans=recent_scans,
        samples=samples
    )

@scanner_bp.route("/scan", methods=["POST"])
@login_required
def scan():
    """Handles message submission and ingestion."""
    user = get_current_user()
    data = request.get_json() if request.is_json else request.form.to_dict()

    success, message, result = ScannerService.ingest_message(user["id"], data)

    if request.is_json:
        return jsonify({
            "success": success,
            "message": message,
            "data": result
        }), (200 if success else 400)

    if success:
        flash("Message successfully ingested and parsed! Ready for Detection Engine.", "success")
        recent_scans = MessageModel.get_recent_by_user(user["id"], limit=6)
        samples = ScannerService.get_sample_templates()
        return render_template(
            "scanner/index.html",
            user=user,
            recent_scans=recent_scans,
            samples=samples,
            scan_result=result,
            form_data=data
        )
    else:
        flash(message, "danger")
        recent_scans = MessageModel.get_recent_by_user(user["id"], limit=6)
        samples = ScannerService.get_sample_templates()
        return render_template(
            "scanner/index.html",
            user=user,
            recent_scans=recent_scans,
            samples=samples,
            form_data=data
        )

@scanner_bp.route("/sample/<msg_type>", methods=["GET"])
@login_required
def get_sample(msg_type):
    """API endpoint providing realistic scam message samples."""
    samples = ScannerService.get_sample_templates()
    sample = samples.get(msg_type.lower())
    if sample:
        return jsonify({"success": True, "sample": sample})
    return jsonify({"success": False, "message": "Sample type not found"}), 404

@scanner_bp.route("/history", methods=["GET"])
@login_required
def history():
    """Scan History view with search and filter controls."""
    user = get_current_user()
    search_query = request.args.get("q", "").strip()
    filter_result = request.args.get("result", "all").strip()

    messages = MessageModel.get_history(
        user["id"],
        search_query=search_query,
        filter_result=filter_result
    )

    return render_template(
        "scanner/history.html",
        user=user,
        messages=messages,
        search_query=search_query,
        filter_result=filter_result
    )

@scanner_bp.route("/analysis/<int:msg_id>", methods=["GET"])
@login_required
def analysis_detail(msg_id):
    """Dedicated Analysis Result view matching bottom-left mockup screen."""
    user = get_current_user()
    msg = MessageModel.get_by_id(msg_id)
    if not msg or msg.get("user_id") != user["id"]:
        flash("Message not found or unauthorized.", "danger")
        return redirect(url_for("scanner.history"))

    from app.services.risk_scoring_service import RiskScoringService
    assessment = RiskScoringService.assess_risk(msg["sanitized_content"])

    return render_template(
        "scanner/analysis.html",
        user=user,
        msg=msg,
        assessment=assessment
    )

@scanner_bp.route("/delete/<int:msg_id>", methods=["POST"])
@login_required
def delete(msg_id):
    """Deletes an ingested message from user scan history."""
    user = get_current_user()
    MessageModel.delete_by_id(msg_id, user["id"])
    flash("Scanned message record removed from history.", "info")
    return redirect(url_for("scanner.history"))

