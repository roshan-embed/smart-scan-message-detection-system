from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from app.services.auth_service import AuthService
from app.controllers.helpers import get_current_user, get_client_ip

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Handle user registration."""
    # If already logged in, redirect to dashboard
    if get_current_user():
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        data = request.get_json() if request.is_json else request.form.to_dict()
        success, message, user_id = AuthService.register_user(data)

        if request.is_json:
            return jsonify({
                "success": success,
                "message": message,
                "redirect": url_for("auth.login") if success else None
            }), (201 if success else 400)

        if success:
            flash(message, "success")
            return redirect(url_for("auth.login"))
        else:
            flash(message, "danger")
            return render_template("auth/register.html", form_data=data)

    return render_template("auth/register.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Handle user login."""
    if get_current_user():
        return redirect(url_for("dashboard.index"))

    next_url = request.args.get("next")

    if request.method == "POST":
        data = request.get_json() if request.is_json else request.form.to_dict()
        identifier = data.get("identifier", "").strip()
        password = data.get("password", "")
        remember_me = bool(data.get("remember_me"))

        ip = get_client_ip()
        ua = request.headers.get("User-Agent", "")

        success, message, user, session_token = AuthService.authenticate_user(
            identifier, password, ip_address=ip, user_agent=ua
        )

        if success:
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["email"] = user["email"]
            session["role"] = user["role"]
            session["first_name"] = user["first_name"]
            session["last_name"] = user["last_name"]
            session["session_token"] = session_token
            session.permanent = remember_me

            target = next_url if next_url and next_url.startswith("/") else url_for("dashboard.index")

            if request.is_json:
                return jsonify({
                    "success": True,
                    "message": message,
                    "redirect": target
                }), 200

            flash(f"Welcome back, {user['first_name']}!", "success")
            return redirect(target)
        else:
            if request.is_json:
                return jsonify({"success": False, "message": message}), 401

            flash(message, "danger")
            return render_template("auth/login.html", identifier=identifier)

    return render_template("auth/login.html")

@auth_bp.route("/logout")
def logout():
    """Handle user logout."""
    token = session.get("session_token")
    if token:
        AuthService.logout_session(token)
    session.clear()
    flash("You have been securely signed out.", "info")
    return redirect(url_for("auth.login"))
