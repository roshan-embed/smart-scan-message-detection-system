import os
import uuid
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
from app.controllers.helpers import login_required, get_current_user
from app.services.ocr_service import OCRService
from app.services.scanner_service import ScannerService

ocr_bp = Blueprint("ocr", __name__, url_prefix="/ocr")

@ocr_bp.route("/", methods=["GET"])
@login_required
def index():
    """Module 3: Screenshot & Image Message Scanner Studio."""
    user = get_current_user()
    samples = OCRService.get_sample_screenshots()
    return render_template(
        "ocr/index.html",
        user=user,
        samples=samples
    )

@ocr_bp.route("/extract", methods=["POST"])
@login_required
def extract():
    """
    Handles screenshot upload or preloaded sample selection.
    Extracts text using local OCR and returns editable text.
    """
    user = get_current_user()

    # Case 1: Pre-registered Sample Screenshot selected
    sample_id = request.form.get("sample_id")
    if sample_id:
        samples = OCRService.get_sample_screenshots()
        matched = next((s for s in samples if s["id"] == sample_id), None)
        if matched:
            rel_path = matched["image_url"].lstrip("/")
            full_path = os.path.join(current_app.root_path, rel_path)
            result = OCRService.extract_text(full_path, filename=matched["filename"])
            result["image_url"] = matched["image_url"]
            result["sample_title"] = matched["title"]
            return jsonify({"success": True, "data": result})

    # Case 2: File Upload via Drag & Drop or File Input
    if "screenshot" not in request.files:
        return jsonify({"success": False, "message": "No screenshot image file provided."}), 400

    file = request.files["screenshot"]
    if file.filename == "":
        return jsonify({"success": False, "message": "No file selected."}), 400

    if not OCRService.allowed_file(file.filename):
        return jsonify({
            "success": False, 
            "message": "Invalid file format. Allowed formats: PNG, JPG, JPEG, WEBP, BMP."
        }), 400

    upload_dir = os.path.join(current_app.root_path, "static", "uploads", "screenshots")
    os.makedirs(upload_dir, exist_ok=True)

    filename = f"{uuid.uuid4().hex[:12]}_{secure_filename(file.filename)}"
    save_path = os.path.join(upload_dir, filename)
    file.save(save_path)

    # Perform OCR Text Extraction
    result = OCRService.extract_text(save_path, filename=file.filename)
    result["image_url"] = f"/static/uploads/screenshots/{filename}"
    result["filename"] = filename

    return jsonify({"success": True, "data": result})

@ocr_bp.route("/analyze", methods=["POST"])
@login_required
def analyze_extracted():
    """
    Submits verified/edited OCR text directly to the scam detection pipeline.
    """
    user = get_current_user()
    content = request.form.get("content", "").strip()
    message_type = request.form.get("message_type", "sms").lower()
    sender_info = request.form.get("sender_info", "Screenshot OCR")

    if not content:
        flash("Extracted message text cannot be empty.", "danger")
        return redirect(url_for("ocr.index"))

    success, msg, result = ScannerService.ingest_message(user["id"], {
        "content": content,
        "message_type": message_type,
        "sender_info": sender_info
    })

    if success and result:
        flash("Screenshot OCR text successfully processed and analyzed!", "success")
        msg_id = result.get("message_id")
        if msg_id:
            return redirect(url_for("scanner.analysis_detail", msg_id=msg_id))
        return redirect(url_for("scanner.index"))
    else:
        flash(f"Analysis error: {msg}", "danger")
        return redirect(url_for("ocr.index"))
