### Requirement: User can log in with valid credentials
The system SHALL accept a username and password via `POST /login`, validate them against the stored hash, and return a signed JWT token on success.

#### Scenario: Successful login
- **WHEN** a client sends `POST /login` with a username and correct password for an existing user
- **THEN** the system SHALL return HTTP 200 with a JSON body containing a `token` field holding a signed JWT

#### Scenario: Wrong password rejected
- **WHEN** a client sends `POST /login` with a valid username but incorrect password
- **THEN** the system SHALL return HTTP 401 with a JSON body `{"error": "Invalid credentials"}`

#### Scenario: Unknown username rejected
- **WHEN** a client sends `POST /login` with a username that does not exist in the database
- **THEN** the system SHALL return HTTP 401 with a JSON body `{"error": "Invalid credentials"}`

#### Scenario: Missing fields rejected
- **WHEN** a client sends `POST /login` without a username or without a password
- **THEN** the system SHALL return HTTP 400 with a JSON body `{"error": "Username and password are required"}`

#### Scenario: Issued token contains user identity
- **WHEN** a JWT is issued on successful login
- **THEN** the token payload SHALL include the `username` and an `exp` (expiry) claim set to the configured expiry duration from the time of login
