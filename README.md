# SIFA - Smart IoT Farm Agriculture API

SIFA is a FastAPI-based backend system for managing IoT devices in a smart agriculture environment. The system provides secure user authentication, device management, and access control—designed to operate over a private network with zero cloud dependencies.

---

##  Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [API Documentation](#api-documentation)
- [Authentication](#authentication)
- [Database Schema](#database-schema)
- [Testing](#testing)
- [Docker Deployment](#docker-deployment)

---

##  Features

### Authentication & Security
- **OAuth2 Bearer Token Authentication** - JWT-based token system with 15-minute expiration
- **Password Hashing** - PBKDF2-SHA256 with salted passwords
- **User Registration & Login** - Secure signup and authentication endpoints
- **Swagger UI Integration** - Built-in interactive API documentation with token authorization

### Device Management
- **CRUD Operations** - Create, Read, Update, Delete devices
- **Access Control** - Users can only manage their own devices
- **Device Tracking** - Monitor device status and last seen timestamps
- **User Isolation** - Devices are strictly associated with their owner

### Data Persistence
- **SQLAlchemy ORM** - Robust database abstraction layer
- **SQLite Development** - Lightweight file-based database for testing
- **PostgreSQL Production** - Full relational database for deployments
- **Automatic Schema** - Database tables created on startup

### Testing & Quality
- **Comprehensive Test Suite** - 31+ tests covering auth, devices, and integration flows
- **100% Test Pass Rate** - All endpoints tested and validated
- **In-Memory Test Database** - Isolated tests with no side effects
- **Pytest Integration** - Professional testing framework

---

##  Architecture

### Technology Stack
- **Framework:** FastAPI 0.141.1 (async web framework)
- **ORM:** SQLAlchemy 2.0+ (database abstraction)
- **Database:** SQLite (dev) / PostgreSQL (prod)
- **Authentication:** python-jose JWT + OAuth2PasswordBearer
- **Testing:** pytest + TestClient
- **Containerization:** Docker & Docker Compose
- **Python:** 3.10+

### Request Flow
```
Client Request
    ↓
OAuth2PasswordBearer (Extract Bearer token from header)
    ↓
get_current_user_email() (Validate JWT & verify user exists)
    ↓
Endpoint Handler (Database operations with authenticated user)
    ↓
JSON Response
```

### Authentication Flow
```
1. POST /auth/signup → Register new user (password hashed)
2. POST /auth/login → Validate credentials → Return JWT token
3. Client adds: Authorization: Bearer <token>
4. Endpoints validate token → Extract user email → Verify ownership
5. Token expires after 15 minutes (requires re-login)
```

---

##  Project Structure

```
sifa/
├── app/
│   ├── core/
│   │   └── security.py           # JWT creation/validation, password hashing
│   ├── models/
│   │   ├── device.py             # Device ORM model
│   │   ├── user.py               # User ORM model
│   │   └── __init__.py
│   ├── repositories/
│   │   ├── device.py             # Device database operations
│   │   ├── user.py               # User database operations
│   │   └── __init__.py
│   ├── routers/
│   │   ├── device.py             # Device endpoints (GET, POST, PUT, DELETE)
│   │   ├── user.py               # Auth endpoints (signup, login)
│   │   └── __init__.py
│   ├── schemas/
│   │   ├── device.py             # Device request/response schemas
│   │   ├── user.py               # User & auth schemas
│   │   └── __init__.py
│   └── services/
│       ├── auth_security.py       # OAuth2 dependency for protected routes
│       └── __init__.py
├── tests/
│   ├── test_user.py              # 6 tests: user registration & auth
│   ├── test_device.py            # 15 tests: device CRUD & access control
│   └── test_api_integration.py    # 10 tests: end-to-end auth flows
├── main.py                        # FastAPI app entry point
├── database.py                    # SQLAlchemy setup & session management
├── conftest.py                    # Pytest configuration & fixtures
├── docker-compose.yml             # Docker services (API + PostgreSQL)
├── Dockerfile                     # Container image definition
├── requirements.txt               # Python dependencies
├── .env                           # Environment variables (SECRET_KEY, etc.)
├── schema.sql                     # Database ERD & design documentation
└── README.md                      # This file
```

---

##  Quick Start

### 1. Prerequisites
- Python 3.10+
- Virtual environment (recommended)
- PostgreSQL (optional, for production)

### 2. Installation

```bash
# Clone or navigate to project
cd sifa

# Create virtual environment
python3 -m venv env
source env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (if not exists)
cat > .env << EOF
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
DATABASE_URL=sqlite:///./test.db
EOF
```

### 3. Run the Server

```bash
# Development with auto-reload
uvicorn main:app --reload

# Production
uvicorn main:app --host 0.0.0.0 --port 8000
```

**Server running at:** http://localhost:8000  
**Swagger UI:** http://localhost:8000/docs  
**ReDoc:** http://localhost:8000/redoc

### 4. Run Tests


pytest tests/ -v


# With coverage
pytest tests/ --cov=app
```

---

##  API Documentation

### Authentication Endpoints

#### Register User
```http
POST /auth/signup
Content-Type: application/json

{
  "email": "user@sifa.com",
  "password": "securepassword123",
  "full_name": "John Doe"
}
```

**Response (201):**
```json
{
  "id": 1,
  "email": "user@sifa.com",
  "full_name": "John Doe",
  "is_active": true
}
```

#### Login
```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@sifa.com",
  "password": "securepassword123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

### Device Endpoints

**All device endpoints require authentication.** Include token in header:
```
Authorization: Bearer <access_token>
```

#### Create Device
```http
POST /devices/
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Greenhouse A - Sensor 1",
  "status": "online"
}
```

**Response (201):**
```json
{
  "id": 1,
  "name": "Greenhouse A - Sensor 1",
  "status": "online",
  "last_seen": "2026-10-10T12:00:00",
  "owner_id": 1
}
```

#### List User's Devices
```http
GET /devices/
Authorization: Bearer <token>
```

**Response (200):**
```json
[
  {
    "id": 1,
    "name": "Greenhouse A - Sensor 1",
    "status": "online",
    "last_seen": "2026-10-10T12:00:00",
    "owner_id": 1
  },
  {
    "id": 2,
    "name": "Greenhouse A - Sensor 2",
    "status": "offline",
    "last_seen": "2026-10-10T11:30:00",
    "owner_id": 1
  }
]
```

#### Get Device by ID
```http
GET /devices/{device_id}
Authorization: Bearer <token>
```

**Response (200):** Single device object  
**Response (404):** "Device not found or unauthorized access" (if not owner)

#### Update Device
```http
PUT /devices/{device_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Greenhouse B - Sensor 1",
  "status": "offline"
}
```

**Response (200):** Updated device object

#### Delete Device
```http
DELETE /devices/{device_id}
Authorization: Bearer <token>
```

**Response (204):** No content (success)  
**Response (404):** Device not found

---

##  Authentication

### How to Use with Python Requests

```python
import requests

# Login
response = requests.post(
    "http://localhost:8000/auth/login",
    json={"email": "user@sifa.com", "password": "pass123"}
)
token = response.json()["access_token"]

# Access protected endpoint
headers = {"Authorization": f"Bearer {token}"}
devices = requests.get(
    "http://localhost:8000/devices/",
    headers=headers
).json()

print(devices)
```

### Token Details
- **Algorithm:** HS256 (HMAC with SHA-256)
- **Expiration:** 15 minutes
- **Claim:** Contains user email (`sub`), issuance time (`iat`), expiration (`exp`)
- **Validation:** Verified against SECRET_KEY from `.env`

---



### Relationships
- **1:N** - One user → Many devices
- **Cascade Delete** - Deleting a user also deletes all their devices

See `schema.sql` for complete database design with ERD.

---

## Testing

### Test Coverage

| File | Tests | Coverage |
|------|-------|----------|
| `test_user.py` | 6 | User registration & authentication |
| `test_device.py` | 15 | Device CRUD & access control |
|| **Total** | **31** | **100% Pass Rate** |

### Test Categories

#### User Authentication Tests
- User registration (valid & duplicate emails)
- Login with valid/invalid credentials
-  Token extraction and validation

#### Device Repository Tests
- Get user devices (isolation & exclusion)
-  Get device by ID (ownership verification)
-  Create devices (multiple per user)
- Update devices (persistence)
-  Access control (prevent cross-user access)


### Running Tests

```bash
# All tests with verbose output
pytest tests/ -v

# Run specific test class
pytest tests/test_device.py::TestGetUserDevices -v

# Run with detailed failure info
pytest tests/ -v --tb=long

# Run with coverage report
pytest tests/ --cov=app --cov-report=html
```

---

## Docker Deployment

### With Docker Compose

```bash
# Start all services (API + PostgreSQL)
docker compose up --build

# Stop services
docker compose down

# View logs
docker compose logs -f api
```

### Environment Variables (for Docker)

Create `.env` for container configuration:
```env
SECRET_KEY=your-production-secret-key
ALGORITHM=HS256
DATABASE_URL=DATABASE_URL

### Services

- **API:** http://localhost:8000 (FastAPI)
- **Database:** localhost:5432 (PostgreSQL)
- **Swagger UI:** http://localhost:8000/docs

---

## 🔧 Troubleshooting

### "Not authenticated" on device endpoints

**Problem:** Token not being accepted  
**Solution:** 
1. Verify token format: `Authorization: Bearer <token>` (with space)
2. Check token expiration (15 min limit)
3. Ensure token from same login session
4. Try new login: `POST /auth/login`

### Token extraction fails in Swagger UI

**Problem:** Authorize button not working  
**Solution:**
1. Verify token is copied from response body (not manually entered)
2. Paste ONLY the token value, no "Bearer " prefix
3. Refresh page if button seems stuck
4. Check browser console for errors (F12)

### "User not found" error

**Problem:** Token is valid but user doesn't exist  
**Solution:**
1. User was deleted from database
2. Register new user: `POST /auth/signup`
3. Check database connection

### Database locked or not created

**Problem:** SQLite database file issues  
**Solution:**
```bash
# Remove old database
rm test.db

# Restart server (will create new database)
uvicorn main:app --reload
```

### PostgreSQL connection failed (Docker)

**Problem:** Cannot connect to DB container  
**Solution:**
```bash
# Verify containers are running
docker compose ps

# Check database logs
docker compose logs db

# Restart containers
docker compose restart db
```

---




