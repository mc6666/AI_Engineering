## ADDED Requirements

### Requirement: User can initiate Google OAuth login
The system SHALL expose `GET /auth/google` which redirects the client to Google's OAuth 2.0 authorization endpoint with the correct client ID, scopes (`openid email profile`), and a CSRF state parameter.

#### Scenario: OAuth redirect initiated
- **WHEN** a client sends `GET /auth/google`
- **THEN** the system SHALL respond with HTTP 302 redirecting to Google's authorization URL with `client_id`, `redirect_uri`, `scope`, and `state` parameters set

### Requirement: System handles Google OAuth callback and issues JWT
The system SHALL expose `GET /auth/google/callback` which accepts the authorization code from Google, exchanges it for an access token, retrieves the user's Google profile, auto-provisions a local user record if needed, and returns a signed JWT.

#### Scenario: Successful first-time Google login (new user)
- **WHEN** Google redirects to `/auth/google/callback` with a valid `code` and matching `state` for a Google account not previously seen
- **THEN** the system SHALL create a new `users` row with `google_id`, `email`, and a derived username (local part of email), and return HTTP 200 with a JSON body `{"token": "<jwt>"}`

#### Scenario: Successful returning Google login (existing user)
- **WHEN** Google redirects to `/auth/google/callback` with a valid `code` and matching `state` for a `google_id` already in the database
- **THEN** the system SHALL NOT create a duplicate user, and SHALL return HTTP 200 with a JSON body `{"token": "<jwt>"}`

#### Scenario: Invalid or missing state rejected
- **WHEN** Google redirects to `/auth/google/callback` without a matching state parameter (potential CSRF)
- **THEN** the system SHALL return HTTP 400 with a JSON body `{"error": "Invalid OAuth state"}`

#### Scenario: Google authorization denied by user
- **WHEN** the user denies consent on Google's authorization screen and Google redirects back with an `error` parameter
- **THEN** the system SHALL return HTTP 400 with a JSON body `{"error": "Google authorization denied"}`

#### Scenario: Derived username collision resolved
- **WHEN** auto-provisioning a new OAuth user whose derived username already exists in the database
- **THEN** the system SHALL append a short unique suffix to the username and create the record without error

#### Scenario: Issued JWT contains user identity
- **WHEN** a JWT is issued after successful Google OAuth callback
- **THEN** the token payload SHALL include the `username` and an `exp` claim, identical in structure to the password login token, and SHALL be accepted by `@token_required` on protected routes
