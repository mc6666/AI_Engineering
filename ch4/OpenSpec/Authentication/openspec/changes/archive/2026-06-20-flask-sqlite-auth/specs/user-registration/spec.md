## ADDED Requirements

### Requirement: User can register a new account
The system SHALL accept a username and password via `POST /register` and create a new user record in the SQLite database with the password stored as a hash. The system SHALL reject registration if the username already exists.

#### Scenario: Successful registration
- **WHEN** a client sends `POST /register` with a unique username and a non-empty password
- **THEN** the system SHALL return HTTP 201 with a JSON body `{"message": "User registered successfully"}`

#### Scenario: Duplicate username rejected
- **WHEN** a client sends `POST /register` with a username that already exists in the database
- **THEN** the system SHALL return HTTP 409 with a JSON body `{"error": "Username already exists"}`

#### Scenario: Missing required fields
- **WHEN** a client sends `POST /register` without a username or without a password
- **THEN** the system SHALL return HTTP 400 with a JSON body `{"error": "Username and password are required"}`

#### Scenario: Password is stored hashed
- **WHEN** a user is successfully registered
- **THEN** the stored password in the database SHALL be a Werkzeug PBKDF2 hash, not the plaintext password
