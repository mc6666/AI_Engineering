from datetime import datetime, timedelta, timezone

import jwt
from flask import Blueprint, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

import config
import models
from auth import token_blocklist
from auth.decorators import token_required

auth_bp = Blueprint("auth_bp", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = (data.get("password") or "").strip()

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    if models.username_exists(username):
        return jsonify({"error": "Username already exists"}), 409

    models.create_user(username, generate_password_hash(password))
    return jsonify({"message": "User registered successfully"}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = (data.get("password") or "").strip()

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    user = models.get_user_by_username(username)
    if user is None or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Invalid credentials"}), 401

    expiry = datetime.now(timezone.utc) + timedelta(minutes=config.TOKEN_EXPIRY_MINUTES)
    token = jwt.encode({"username": username, "exp": expiry}, config.SECRET_KEY, algorithm="HS256")
    return jsonify({"token": token}), 200


@auth_bp.route("/logout", methods=["POST"])
@token_required
def logout(username):
    token = request.headers.get("Authorization", "").split(" ", 1)[1]
    token_blocklist.add(token)
    return jsonify({"message": "Logged out successfully"}), 200


@auth_bp.route("/protected", methods=["GET"])
@token_required
def protected(username):
    return jsonify({"message": f"Hello, {username}! This is a protected route."}), 200
