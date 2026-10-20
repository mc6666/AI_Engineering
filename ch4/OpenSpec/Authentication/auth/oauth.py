from datetime import datetime, timedelta, timezone

import jwt
from authlib.integrations.base_client import OAuthError
from authlib.integrations.flask_client import OAuth
from flask import Blueprint, jsonify, request

import config
import models

oauth = OAuth()
google = oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

oauth_bp = Blueprint("oauth_bp", __name__, url_prefix="/auth")


@oauth_bp.route("/google")
def google_login():
    return google.authorize_redirect(config.GOOGLE_REDIRECT_URI)


@oauth_bp.route("/google/callback")
def google_callback():
    if request.args.get("error"):
        return jsonify({"error": "Google authorization denied"}), 400

    try:
        token = google.authorize_access_token()
    except OAuthError:
        return jsonify({"error": "Invalid OAuth state"}), 400

    user_info = token.get("userinfo") or google.userinfo()
    google_id = user_info["sub"]
    email = user_info.get("email", "")

    user = models.get_user_by_google_id(google_id)
    if user is None:
        base = email.split("@")[0] if email else f"user_{google_id[:8]}"
        username = models.generate_unique_username(base)
        models.create_oauth_user(username, google_id, email)
    else:
        username = user["username"]

    expiry = datetime.now(timezone.utc) + timedelta(minutes=config.TOKEN_EXPIRY_MINUTES)
    jwt_token = jwt.encode(
        {"username": username, "exp": expiry},
        config.SECRET_KEY,
        algorithm="HS256",
    )
    return jsonify({"token": jwt_token}), 200
