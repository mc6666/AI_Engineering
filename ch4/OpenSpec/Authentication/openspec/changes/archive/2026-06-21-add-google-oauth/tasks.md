## 1. Dependencies and Configuration

- [x] 1.1 Add `authlib` to `requirements.txt` and install via `pip install authlib`
- [x] 1.2 Add `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, and `GOOGLE_REDIRECT_URI` to `config.py`, loaded from environment variables with no default (raise error if missing in production)
- [x] 1.3 Add `FLASK_SECRET_KEY` config used by Flask's session (required by Authlib for state storage); set `app.secret_key = config.SECRET_KEY` in `app.py`

## 2. Database Schema Migration

- [x] 2.1 Update `database.py` `init_db()` to ALTER TABLE and add `google_id TEXT UNIQUE` column if it does not already exist
- [x] 2.2 Update `database.py` `init_db()` to ALTER TABLE and add `email TEXT` column if it does not already exist
- [x] 2.3 Update the `CREATE TABLE IF NOT EXISTS users` statement in `init_db()` to include `google_id TEXT UNIQUE` and `email TEXT`, and make `password_hash TEXT` nullable (for new databases)

## 3. User Model Updates

- [x] 3.1 Add `get_user_by_google_id(google_id)` function to `models.py` that returns the user row or `None`
- [x] 3.2 Add `create_oauth_user(username, google_id, email)` function to `models.py` that inserts a user row with `password_hash = NULL`
- [x] 3.3 Add `username_exists(username)` is already present — add a helper `generate_unique_username(base)` that appends a short UUID4 suffix when `base` is taken

## 4. Google OAuth Routes

- [x] 4.1 Create `auth/oauth.py` with a Blueprint named `oauth_bp` mounted at `/auth`
- [x] 4.2 Register the Google OAuth remote app in `oauth.py` using `Authlib`'s `OAuth` class with `server_metadata_url` pointing to Google's discovery endpoint
- [x] 4.3 Implement `GET /auth/google`: call `google.authorize_redirect(redirect_uri)` to initiate the OAuth flow (Authlib handles state generation)
- [x] 4.4 Implement `GET /auth/google/callback`: call `google.authorize_access_token()` to exchange the code, handle `OAuthError` for denied/invalid state, retrieve user info via `google.parse_id_token()` or `userinfo` endpoint
- [x] 4.5 In the callback: look up user by `google_id`; if not found, call `generate_unique_username` and `create_oauth_user` to auto-provision
- [x] 4.6 In the callback: issue a JWT token (same `{username, exp}` payload as `/login`) and return `{"token": "<jwt>"}` with HTTP 200
- [x] 4.7 In the callback: return HTTP 400 with `{"error": "Google authorization denied"}` when Google returns an error parameter

## 5. App Wiring

- [x] 5.1 Register `oauth_bp` in `app.py` alongside the existing `auth_bp`
- [x] 5.2 Initialize the Authlib `OAuth` object with `app` in `app.py` (or use `oauth.init_app(app)` pattern)
- [x] 5.3 Set `app.secret_key` from `config.SECRET_KEY` in `create_app()` (required for Authlib session-based state storage)

## 6. Verification

- [x] 6.1 Start the app and confirm `GET /auth/google` returns a 302 redirect to `accounts.google.com`
- [ ] 6.2 Complete a full Google login flow in a browser and confirm a JWT token is returned in the response
- [ ] 6.3 Use the JWT from step 6.2 to call `GET /protected` and confirm HTTP 200 with greeting
- [ ] 6.4 Confirm the new user row exists in `auth.db` with `google_id` and `email` populated and `password_hash` NULL
- [ ] 6.5 Repeat the Google login for the same account and confirm no duplicate user is created
- [x] 6.6 Confirm existing `POST /login` and `POST /register` still work correctly (no regression)
