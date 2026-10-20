## 1. Project Setup

- [x] 1.1 Create project directory structure (`auth/`, `app.py`, `config.py`, `database.py`, `models.py`)
- [x] 1.2 Create `requirements.txt` with `flask` and `pyjwt` dependencies
- [x] 1.3 Install dependencies via `pip install -r requirements.txt`
- [x] 1.4 Create `config.py` with `SECRET_KEY`, `DATABASE_PATH`, and `TOKEN_EXPIRY_MINUTES` (load `SECRET_KEY` from environment variable with a default fallback)

## 2. Database Layer

- [x] 2.1 Create `database.py` with a `get_connection()` helper that returns a `sqlite3.Connection`
- [x] 2.2 Add `init_db()` function in `database.py` that creates the `users` table (`id`, `username`, `password_hash`) if it does not exist
- [x] 2.3 Call `init_db()` on app startup in `app.py`

## 3. User Model

- [x] 3.1 Create `models.py` with a `create_user(username, password_hash)` function that inserts a new user row
- [x] 3.2 Add `get_user_by_username(username)` function that returns the user row or `None`
- [x] 3.3 Add `username_exists(username)` helper that returns `True` if the username is already taken

## 4. Auth Decorator

- [x] 4.1 Create `auth/decorators.py` with a `token_required` decorator
- [x] 4.2 Decorator SHALL extract the token from the `Authorization: Bearer <token>` header
- [x] 4.3 Decorator SHALL check the token against the in-memory blocklist and return 401 `{"error": "Token has been revoked"}` if found
- [x] 4.4 Decorator SHALL decode the JWT using `config.SECRET_KEY`; return 401 `{"error": "Token has expired"}` on expiry, 401 `{"error": "Token is invalid"}` on any other decode error
- [x] 4.5 Decorator SHALL pass the decoded `username` to the wrapped route handler

## 5. Authentication Routes

- [x] 5.1 Create `auth/routes.py` and register a Flask Blueprint named `auth_bp`
- [x] 5.2 Implement `POST /register`: validate required fields, check for duplicate username, hash password with Werkzeug, insert user, return 201 or appropriate error
- [x] 5.3 Implement `POST /login`: validate required fields, retrieve user, verify password hash, issue JWT with `username` and `exp` claims, return 200 with token or appropriate error
- [x] 5.4 Implement `POST /logout`: require `@token_required`, add token to the in-memory blocklist set, return 200 confirmation
- [x] 5.5 Implement `GET /protected`: require `@token_required`, return 200 with greeting message including the authenticated username

## 6. Flask App Wiring

- [x] 6.1 Create `app.py` as the Flask application factory; call `init_db()` and register the `auth_bp` blueprint
- [x] 6.2 Create `auth/__init__.py` to make `auth` a package
- [x] 6.3 Add a `if __name__ == "__main__":` block to run Flask in debug mode on port 5000

## 7. Verification

- [x] 7.1 Test `POST /register` with valid data → expect 201
- [x] 7.2 Test `POST /register` with duplicate username → expect 409
- [x] 7.3 Test `POST /login` with valid credentials → expect 200 with token
- [x] 7.4 Test `POST /login` with wrong password → expect 401
- [x] 7.5 Test `GET /protected` with valid token → expect 200 with greeting
- [x] 7.6 Test `GET /protected` with no token → expect 401
- [x] 7.7 Test `POST /logout` then retry the same token on `/protected` → expect 401 revoked
