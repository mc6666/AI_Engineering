## Why

The application needs a secure, self-contained user authentication system. Building it with Flask and SQLite provides a lightweight, dependency-minimal solution appropriate for a single-service backend without requiring an external database server.

## What Changes

- Introduce user registration and login endpoints in Flask
- Add password hashing using `werkzeug.security` (bcrypt-based)
- Create a SQLite database with a `users` table to persist credentials
- Implement session-based authentication using Flask-Login or JWT tokens
- Protect routes with an authentication decorator/guard
- Add logout functionality to invalidate sessions or tokens

## Capabilities

### New Capabilities

- `user-registration`: Allow new users to create an account with username/email and password
- `user-login`: Authenticate existing users and issue a session or JWT token
- `user-logout`: Invalidate the current session or token
- `protected-routes`: Restrict access to certain endpoints to authenticated users only

### Modified Capabilities

<!-- No existing specs are being modified -->

## Impact

- **New dependencies**: Flask, Flask-Login (or PyJWT), Werkzeug (already bundled with Flask)
- **New files**: `app.py`, `models.py`, `auth.py` (routes), `database.py` (SQLite init), `config.py`
- **Database**: SQLite file (`auth.db`) created at runtime — no external DB server required
- **APIs**: New endpoints `POST /register`, `POST /login`, `POST /logout`, `GET /protected`
