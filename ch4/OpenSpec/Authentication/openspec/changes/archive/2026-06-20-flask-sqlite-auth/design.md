## Context

We are building a standalone Flask authentication backend using SQLite as the persistence layer. There is no existing authentication system — this is a greenfield implementation. The stack is intentionally minimal: no ORM, no external database server, no message broker. The target audience is a single-service backend suitable for a book chapter demonstrating authentication fundamentals.

## Goals / Non-Goals

**Goals:**
- User registration with hashed passwords stored in SQLite
- Login endpoint that validates credentials and returns a JWT token
- Logout support (client-side token discard + optional server-side blocklist)
- A protected route that requires a valid token to access
- Clean module separation: routes, models, database initialization, config

**Non-Goals:**
- OAuth2 / social login (Google, GitHub, etc.)
- Role-based access control (RBAC)
- Email verification or password reset flows
- Production-grade token revocation (a simple in-memory blocklist is sufficient for demo purposes)
- Deployment configuration (Docker, gunicorn, nginx)

## Decisions

### 1. JWT over Flask sessions

**Choice**: Use PyJWT to issue stateless JSON Web Tokens instead of Flask's server-side session cookies.

**Rationale**: JWTs are API-friendly and stateless, making them easier to demonstrate in a book context. They also work naturally with REST clients (curl, Postman) without browser cookie mechanics.

**Alternatives considered**:
- Flask-Login + sessions: Requires browser cookies, less illustrative of the token exchange pattern.
- Flask-Session with Redis: Adds an external dependency, contradicts the SQLite-only goal.

### 2. Raw SQLite via `sqlite3` module (no ORM)

**Choice**: Use Python's built-in `sqlite3` module directly.

**Rationale**: Keeps the implementation transparent and dependency-free. Readers see every SQL statement, which is appropriate for an educational codebase.

**Alternatives considered**:
- SQLAlchemy Core: More robust but adds a non-trivial dependency and abstracts SQL away from the reader.
- Flask-SQLAlchemy: ORM convenience hides the schema and query details.

### 3. Password hashing via Werkzeug

**Choice**: Use `werkzeug.security.generate_password_hash` / `check_password_hash` (PBKDF2-HMAC-SHA256).

**Rationale**: Werkzeug is already a Flask dependency — zero additional installs. The functions are well-tested and follow current OWASP recommendations.

**Alternatives considered**:
- `bcrypt` library: Slightly stronger default cost factor but requires a separate C extension install.
- `passlib`: More flexible but heavyweight for this use case.

### 4. Module layout

```
auth.db              ← SQLite file (runtime-generated)
app.py               ← Flask app factory + main entry
config.py            ← SECRET_KEY, DB path, JWT expiry
database.py          ← SQLite connection helper + schema init
models.py            ← User data class + DB queries
auth/
  __init__.py
  routes.py          ← /register, /login, /logout, /protected
  decorators.py      ← @token_required decorator
```

## Risks / Trade-offs

- **In-memory token blocklist is not persistent** → Restarting the server clears logged-out tokens; acceptable for a demo, document the limitation explicitly.
- **SQLite concurrent writes** → SQLite WAL mode is not configured; under concurrent load this will lock. Out of scope for a single-user demo but noted.
- **JWT secret in config.py** → Must not be committed with a real secret in production. Book chapter should show loading from environment variable.
- **No HTTPS enforcement** → Tokens sent over plain HTTP can be intercepted. Out of scope for local demo; note it in the README.

## Migration Plan

1. Install dependencies: `pip install flask pyjwt`
2. Run `python app.py` — `database.py` initializes `auth.db` automatically on first run
3. No schema migrations needed (greenfield)
4. Rollback: delete `auth.db` to reset all state

## Open Questions

- Should token expiry be configurable via environment variable or hardcoded in `config.py`? (Recommendation: env var with a sensible default of 60 minutes)
- Should the `/protected` route return user profile data or just a confirmation message? (Recommendation: return the current user's username for demonstration clarity)
