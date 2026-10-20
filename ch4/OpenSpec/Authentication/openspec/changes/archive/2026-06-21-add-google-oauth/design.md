## Context

The system currently has a complete JWT-based username/password authentication stack (register, login, logout, protected routes). This change layers Google OAuth 2.0 on top of that existing foundation without breaking any existing endpoints. The OAuth flow ends by issuing the same JWT token format, so `@token_required` and all protected routes work unchanged.

## Goals / Non-Goals

**Goals:**
- `GET /auth/google` — redirect to Google consent screen
- `GET /auth/google/callback` — exchange authorization code, fetch user info, auto-provision user, issue JWT
- Auto-create a `users` row on first Google login using Google's `sub` (stable user ID) and email
- Add `google_id` and `email` columns to the `users` table (backward-compatible, nullable)
- Make `password_hash` nullable so OAuth-only users are first-class records

**Non-Goals:**
- Account linking (connecting an existing password account to a Google account)
- Multiple OAuth providers (GitHub, Facebook, etc.) — architecture allows it but this change is Google-only
- Refresh token storage or silent re-authentication
- Revoking the Google OAuth grant from within the app

## Decisions

### 1. Authlib over alternatives

**Choice**: Use `Authlib` (`authlib.integrations.flask_client`) as the OAuth 2.0 client.

**Rationale**: Authlib is actively maintained, Flask-native, handles PKCE, state verification, and token exchange out of the box. It avoids writing raw OAuth plumbing.

**Alternatives considered**:
- `requests-oauthlib`: Lower-level; requires manual state management and token exchange.
- `google-auth` / `google-auth-oauthlib`: Google-specific; redundant given Authlib supports any provider.
- Raw `requests`: Too much manual work for an educational codebase; error-prone state management.

### 2. Issue the same JWT format, not a separate OAuth session

**Choice**: After successful Google callback, issue a PyJWT token identical in structure to the password login token (`{username, exp}`).

**Rationale**: All protected routes already use `@token_required` which validates JWT. Reusing the same token format means zero changes to the decorator, routes, or clients. The token is provider-agnostic.

**Alternatives considered**:
- Storing a Google access token server-side and using it as the session: Ties the session lifetime to Google's token, adds complexity.
- Separate session cookie for OAuth users: Inconsistent client experience; requires browser support.

### 3. Auto-provision users; no separate OAuth registration step

**Choice**: On first Google login, automatically insert a `users` row using a sanitized username derived from the Google email (everything before `@`), with `google_id` set and `password_hash` as `NULL`.

**Rationale**: OAuth is meant to remove registration friction. Forcing a separate registration step after Google login defeats the purpose.

**Alternatives considered**:
- Redirect to `/register` pre-filled with email after first OAuth login: More steps, more state to carry.
- Require manual linking of Google accounts to existing users: Too complex for a demo; add-on feature.

### 4. Backward-compatible schema migration

**Choice**: Add columns via `ALTER TABLE users ADD COLUMN IF NOT EXISTS` in `init_db()` so existing `auth.db` files are updated without data loss. Make `password_hash` nullable.

**Rationale**: Dropping and recreating the table would lose existing password-based users. ALTER TABLE is the minimal, safe migration path.

**Alternatives considered**:
- Separate `oauth_accounts` table with FK to `users`: Cleaner long-term but unnecessary complexity for a single provider demo.
- Version-gated `init_db()` with schema version table: Overkill for this scope.

### 5. Module layout addition

```
auth/
  oauth.py        ← Google OAuth routes (/auth/google, /auth/google/callback)
config.py         ← Add GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI
```

`oauth.py` registers a second Blueprint (`oauth_bp`) mounted at `/auth`.

## Risks / Trade-offs

- **HTTP callbacks rejected by Google** → Google OAuth requires HTTPS for production redirect URIs; `http://localhost:5000` is allowed for development via the "test" status in Google Cloud Console. Document this clearly.
- **`state` parameter CSRF protection** → Authlib handles state generation and validation automatically; manual state management is not needed but must not be bypassed.
- **Username collision on auto-provision** → If two Google users share the same email prefix (unlikely but possible across domains), the insert will fail. Mitigation: append a short UUID suffix when a collision is detected.
- **`password_hash` NULL for OAuth users** → Existing code that assumes `password_hash` is non-null (e.g., `check_password_hash`) is only called in `/login` which requires a non-null password in the request body; OAuth users simply won't match that path. No logic change needed.
- **Google credentials in environment** → `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` must never be hardcoded. Show loading from `os.environ` in `config.py` with no default fallback (fail fast if missing).

## Migration Plan

1. Install `authlib`: `pip install authlib`
2. Set environment variables: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI`
3. Create a Google Cloud OAuth 2.0 client at console.cloud.google.com; add `http://127.0.0.1:5000/auth/google/callback` as an authorized redirect URI
4. Run `python app.py` — `init_db()` will ALTER TABLE to add new columns automatically
5. Rollback: remove `auth/oauth.py`, unregister `oauth_bp` in `app.py`, revert `database.py` schema changes

## Open Questions

- Should the derived username for OAuth users use the full email or just the local part? (Recommendation: local part before `@`, with UUID suffix on collision)
- Should `GET /auth/google/callback` return JSON with the token or redirect to a frontend URL? (Recommendation: return JSON for API consistency with the existing `/login` endpoint)
