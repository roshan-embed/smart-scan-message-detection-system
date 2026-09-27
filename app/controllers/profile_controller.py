from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from app.services.user_service import UserService
from app.controllers.helpers import login_required, get_current_user

profile_bp = Blueprint("profile", __name__, url_prefix="/profile")

@profile_bp.route("/")
@login_required
def view_profile():
    """View user profile, active sessions, and security history."""
    user = get_current_user()
    sessions = UserService.get_user_sessions(user["id"])
    audit_logs = UserService.get_login_history(user["id"], limit=6)
    current_token = session.get("session_token")

    return render_template(
        "profile/view.html",
        user=user,
        sessions=sessions,
        audit_logs=audit_logs,
        current_token=current_token
    )

@profile_bp.route("/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    """Update profile details (name, phone, bio)."""
    user = get_current_user()

    if request.method == "POST":
        data = request.get_json() if request.is_json else request.form.to_dict()
        success, message, updated_user = UserService.update_profile(user["id"], data)

        if success:
            session["first_name"] = updated_user["first_name"]
            session["last_name"] = updated_user["last_name"]

            if request.is_json:
                return jsonify({"success": True, "message": message}), 200

            flash(message, "success")
            return redirect(url_for("profile.view_profile"))
        else:
            if request.is_json:
                return jsonify({"success": False, "message": message}), 400

            flash(message, "danger")
            return render_template("profile/edit.html", user=data)

    return render_template("profile/edit.html", user=user)

@profile_bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    """Handle password change."""
    user = get_current_user()

    if request.method == "POST":
        data = request.get_json() if request.is_json else request.form.to_dict()
        success, message = UserService.change_password(user["id"], data)

        if request.is_json:
            return jsonify({
                "success": success,
                "message": message,
                "redirect": url_for("profile.view_profile") if success else None
            }), (200 if success else 400)

        if success:
            flash(message, "success")
            return redirect(url_for("profile.view_profile"))
        else:
            flash(message, "danger")
            return render_template("profile/change_password.html")

    return render_template("profile/change_password.html")

@profile_bp.route("/sessions/<session_token>/terminate", methods=["POST"])
@login_required
def terminate_session(session_token):
    """Terminate a specific active login session."""
    user = get_current_user()
    current_token = session.get("session_token")

    if session_token == current_token:
        if request.is_json:
            return jsonify({"success": False, "message": "Cannot terminate current active session here. Use Sign Out instead."}), 400
        flash("You cannot terminate your current active session here. Please click Sign Out.", "warning")
        return redirect(url_for("profile.view_profile"))

    success = UserService.terminate_session(user["id"], session_token)
    if success:
        if request.is_json:
            return jsonify({"success": True, "message": "Session terminated successfully."}), 200
        flash("Selected device session has been terminated.", "success")
    else:
        if request.is_json:
            return jsonify({"success": False, "message": "Session could not be terminated."}), 400
        flash("Failed to terminate session.", "danger")

    return redirect(url_for("profile.view_profile"))

@profile_bp.route("/sessions/terminate-others", methods=["POST"])
@login_required
def terminate_all_other_sessions():
    """Terminate all active sessions except the current one."""
    user = get_current_user()
    current_token = session.get("session_token")
    UserService.terminate_all_other_sessions(user["id"], current_token)

    if request.is_json:
        return jsonify({"success": True, "message": "All other active sessions have been terminated."}), 200

    flash("All other active sessions have been terminated successfully.", "success")
    return redirect(url_for("profile.view_profile"))
