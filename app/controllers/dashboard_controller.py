import datetime
from flask import Blueprint, render_template, redirect, url_for, session
from app.controllers.helpers import login_required, get_current_user
from app.models.db import db
from app.models.message_model import MessageModel
from app.services.user_service import UserService
from app.services.scanner_service import ScannerService

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/")
def root():
    """Root redirect."""
    if get_current_user():
        return redirect(url_for("dashboard.index"))
    return redirect(url_for("auth.login"))

@dashboard_bp.route("/dashboard")
@login_required
def index():
    """Operational dashboard overview matching enterprise mockup."""
    user = get_current_user()
    sessions = UserService.get_user_sessions(user["id"])
    active_db = db.get_active_db_type()
    stats = MessageModel.get_user_stats(user["id"])
    samples = ScannerService.get_sample_templates()

    # Time-based greeting
    hour = datetime.datetime.now().hour
    if hour < 12:
        greeting = "Good Morning"
    elif hour < 17:
        greeting = "Good Afternoon"
    else:
        greeting = "Good Evening"
    
    # 12 Modules Roadmap definition matching revised architecture
    modules = [
        {"id": 1, "title": "User Account & Authentication 🔐", "status": "active", "badge": "Operational", "desc": "Manage user accounts: registration, login, logout, profile, change password, and account settings."},
        {"id": 2, "title": "Smart Message Scanner 📩", "status": "active", "badge": "Operational", "desc": "Message submission portal for SMS, WhatsApp, and Email with live character counters, clear, and scan actions."},
        {"id": 3, "title": "Screenshot & Image Message Scanner 🖼️", "status": "active", "badge": "Operational", "desc": "Upload screenshot or drag & drop, local OCR text extraction, preview/edit text verification, and direct analysis."},
        {"id": 4, "title": "URL & Sender Verification 🔗", "status": "active", "badge": "Operational", "desc": "Investigates message origin: HTTPS check, shortened URLs, raw IPs, domain patterns, and sender validation."},
        {"id": 5, "title": "AI Scam Detection 🤖", "status": "active", "badge": "Operational", "desc": "Local DistilBERT model predicting SAFE, SUSPICIOUS, or SCAM with confidence score and zero cloud API dependencies."},
        {"id": 6, "title": "Threat Level Assessment 📊", "status": "active", "badge": "Operational", "desc": "Converts detection outputs (AI result, Suspicious URL, Urgency, KYC request) into overall score and threat level."},
        {"id": 7, "title": "Hybrid Threat Scoring & Fusion", "status": "pending", "badge": "Planned", "desc": "Ensemble weighting combining rule heuristics with DistilBERT logits to yield calibrated threat confidence."},
        {"id": 8, "title": "Scam Category & Intent Classifier", "status": "pending", "badge": "Planned", "desc": "Taxonomy classifier (Banking fraud, Lottery scam, Phishing, Tech support fraud, Impersonation)."},
        {"id": 9, "title": "Detection Results & Explanations", "status": "pending", "badge": "Planned", "desc": "Granular risk assessment cards, highlighted threat tokens, and safety recommendations."},
        {"id": 10, "title": "Threat Blacklist & Pattern Registry", "status": "pending", "badge": "Planned", "desc": "Local threat intel repository for malicious domains, phone numbers, and known scam phrases."},
        {"id": 11, "title": "System Security & Audit Trail", "status": "pending", "badge": "Planned", "desc": "Tamper-evident logs of detection queries, authentication events, and administrative operations."},
        {"id": 12, "title": "Engine Settings & Admin Controls", "status": "pending", "badge": "Planned", "desc": "Configurable risk thresholds, offline model weight selector, and local cache controls."}
    ]

    return render_template(
        "dashboard/index.html",
        user=user,
        greeting=greeting,
        stats=stats,
        samples=samples,
        active_sessions_count=len(sessions),
        active_db=active_db.upper() if active_db else "SQL",
        modules=modules
    )

