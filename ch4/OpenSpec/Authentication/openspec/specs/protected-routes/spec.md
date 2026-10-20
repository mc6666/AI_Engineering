### Requirement: Routes can require authentication
The system SHALL provide a `@token_required` decorator that protects any Flask route. Requests to a decorated route MUST include a valid, non-expired, non-revoked JWT in the `Authorization` header.

#### Scenario: Valid token grants access
- **WHEN** a client sends a request to a protected route with a valid, non-expired JWT in the `Authorization: Bearer <token>` header
- **THEN** the system SHALL allow the request to proceed and the route handler SHALL receive the authenticated username

#### Scenario: Missing token denied
- **WHEN** a client sends a request to a protected route without an `Authorization` header
- **THEN** the system SHALL return HTTP 401 with a JSON body `{"error": "Token is missing"}`

#### Scenario: Expired token denied
- **WHEN** a client sends a request to a protected route with a JWT whose `exp` claim is in the past
- **THEN** the system SHALL return HTTP 401 with a JSON body `{"error": "Token has expired"}`

#### Scenario: Invalid signature denied
- **WHEN** a client sends a request to a protected route with a JWT that has been tampered with or signed with a different secret
- **THEN** the system SHALL return HTTP 401 with a JSON body `{"error": "Token is invalid"}`

#### Scenario: Revoked token denied
- **WHEN** a client sends a request to a protected route with a JWT that is present in the in-memory blocklist
- **THEN** the system SHALL return HTTP 401 with a JSON body `{"error": "Token has been revoked"}`

### Requirement: Example protected endpoint exists
The system SHALL expose `GET /protected` as a demonstration of a guarded route that returns the authenticated user's username.

#### Scenario: Authenticated user accesses protected endpoint
- **WHEN** a client sends `GET /protected` with a valid JWT
- **THEN** the system SHALL return HTTP 200 with a JSON body `{"message": "Hello, <username>! This is a protected route."}`
