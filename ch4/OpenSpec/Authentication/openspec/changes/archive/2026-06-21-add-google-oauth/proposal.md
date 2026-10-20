## Why

The existing system only supports password-based authentication, which requires users to manually register and remember credentials. Adding Google OAuth 2.0 lets users sign in with their existing Google account — reducing friction and eliminating the need for password management on our side.

## What Changes

- Add a Google OAuth 2.0 login flow: `GET /auth/google` initiates the redirect, `GET /auth/google/callback` handles the response
- Auto-provision users on first Google login (create a `users` row if the Google account has not been seen before)
- Issue the same JWT token format used by the existing `/login` endpoint so `@token_required` works unchanged
- Store `google_id` and `email` on the user row to link Google accounts to local records
- Add `Authlib` as a new dependency for OAuth client handling

## Capabilities

### New Capabilities

- `google-oauth`: Full OAuth 2.0 flow with Google — initiate redirect, handle callback, auto-provision user record, and issue a JWT token

### Modified Capabilities

- `user-registration`: Google OAuth introduces a second path for user creation (auto-registration on first OAuth login); the `POST /register` requirement is unchanged but a new scenario for implicit creation is added

## Impact

- **New dependency**: `Authlib` (OAuth 2.0 client) and `requests` (for token exchange fallback)
- **New env vars**: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI`
- **Database change**: `users` table gains `google_id TEXT` and `email TEXT` columns (nullable, backward-compatible)
- **New files**: `auth/oauth.py` (Google OAuth routes), update `database.py` for schema migration
- **New endpoints**: `GET /auth/google`, `GET /auth/google/callback`
- **Existing endpoints unchanged**: `POST /register`, `POST /login`, `POST /logout`, `GET /protected` all remain as-is
