### Requirement: Authenticated user can log out
The system SHALL accept `POST /logout` with a valid JWT in the `Authorization` header, add the token to an in-memory blocklist, and confirm the logout. Subsequent requests using the same token SHALL be rejected.

#### Scenario: Successful logout
- **WHEN** a client sends `POST /logout` with a valid, non-expired JWT in the `Authorization: Bearer <token>` header
- **THEN** the system SHALL return HTTP 200 with a JSON body `{"message": "Logged out successfully"}` and add the token to the blocklist

#### Scenario: Blocked token rejected after logout
- **WHEN** a client sends any authenticated request using a token that has been added to the blocklist
- **THEN** the system SHALL return HTTP 401 with a JSON body `{"error": "Token has been revoked"}`

#### Scenario: Logout without token rejected
- **WHEN** a client sends `POST /logout` without an `Authorization` header
- **THEN** the system SHALL return HTTP 401 with a JSON body `{"error": "Token is missing"}`

#### Scenario: Blocklist is in-memory only
- **WHEN** the Flask application process is restarted
- **THEN** the blocklist SHALL be cleared; previously issued tokens will be accepted again until they expire naturally
