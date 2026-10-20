## ADDED Requirements

### Requirement: User record can be implicitly created via Google OAuth
The system SHALL auto-provision a `users` row when a Google account authenticates for the first time, without requiring the user to explicitly call `POST /register`. The auto-provisioned record SHALL be treated identically to a manually registered user for all subsequent operations.

#### Scenario: Auto-provisioned user can access protected routes
- **WHEN** a user is created implicitly via Google OAuth callback
- **THEN** the JWT issued to that user SHALL be accepted by `@token_required` on all protected routes

#### Scenario: Auto-provisioned user cannot use password login
- **WHEN** an OAuth-provisioned user (with `password_hash` NULL) attempts `POST /login` with any password
- **THEN** the system SHALL return HTTP 401 with `{"error": "Invalid credentials"}` since there is no password to verify
