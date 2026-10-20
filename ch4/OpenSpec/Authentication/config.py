import os

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
DATABASE_PATH = os.environ.get("DATABASE_PATH", "auth.db")
TOKEN_EXPIRY_MINUTES = int(os.environ.get("TOKEN_EXPIRY_MINUTES", "60"))

# Google OAuth 2.0 — must be set via environment variables before using /auth/google
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.environ.get("GOOGLE_REDIRECT_URI", "http://127.0.0.1:5000/auth/google/callback")
