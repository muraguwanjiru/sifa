# SIFA API Authentication Guide

## Overview
The SIFA API requires authentication for protected endpoints (device management). The login endpoint returns a Bearer token that must be included in all subsequent requests.

**Security Note:** The access token is returned in the `Authorization` response header (not in the response body), keeping it hidden from the Swagger UI schema for security purposes.

---

## Step-by-Step Guide to Using SIFA API in Swagger UI

### Step 1: Register a New User
1. Go to `/auth/signup` endpoint
2. Click "Try it out"
3. Enter JSON:
   ```json
   {
     "email": "myuser@sifa.com",
     "full_name": "My Name",
     "password": "MySecurePassword123"
   }
   ```
4. Click "Execute"
5. You'll get a 201 response with your user information

### Step 2: Login to Get Token
1. Go to `/auth/login` endpoint
2. Click "Try it out"
3. Enter JSON:
   ```json
   {
     "email": "myuser@sifa.com",
     "password": "MySecurePassword123"
   }
   ```
4. Click "Execute"
5. Check the **Response headers** (at the bottom)
6. Look for the `authorization` header containing: `Bearer <your_token>`
7. **Copy the entire value** (e.g., `Bearer eyJhbGciOiJIUzI1NiIs...`)

### Step 3: Authorize in Swagger UI
1. Click the green "Authorize" button at the top of the Swagger page
2. In the popup dialog, find the "Bearer (HTTP)" field
3. Paste your token in the format:
   ```
   Bearer <your_token>
   ```
4. Click "Authorize"
5. Click "Close"

### Step 4: Access Protected Device Endpoints
Now you can use these endpoints without getting 401 errors:

- **POST /devices/** - Create a new device
  - Input: `{"name": "MyDevice", "status": "online"}`
  
- **GET /devices/** - List all your devices
  - No parameters needed

- **GET /devices/{device_id}** - Get a specific device
  - Parameter: device_id (from the list above)

- **PUT /devices/{device_id}** - Update a device
  - Input: `{"name": "UpdatedName", "status": "offline"}`

- **DELETE /devices/{device_id}** - Delete a device
  - Parameter: device_id

---

## Alternative: Using cURL

If you prefer command line or need to test programmatically:

### 1. Login and get token
```bash
curl -X POST "http://127.0.0.1:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"myuser@sifa.com","password":"MySecurePassword123"}' \
  -i
```

Extract the `authorization` header value (e.g., `Bearer abc123...`)

### 2. Use token to access device endpoints
```bash
curl -X GET "http://127.0.0.1:8000/devices/" \
  -H "Authorization: Bearer <your_token>"
```

---

## Security Features

✅ **Tokens in Headers** - Access token is transmitted in response header, not in response body (hidden from Swagger schema)

✅ **Bearer Token Auth** - Industry-standard Bearer token authentication

✅ **Ownership Verification** - Each user can only access their own devices

✅ **Token Expiration** - Tokens expire after 15 minutes by default

✅ **Secure Password Hashing** - Passwords use PBKDF2-SHA256 with salt

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| 401 Unauthorized | Make sure you've logged in and authorized in Swagger UI |
| 404 Device Not Found | You can only access your own devices |
| 403 Forbidden | Authorization header is missing or invalid |
| Invalid Token | Token may have expired (15 min). Login again |

---

## API Response Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created successfully |
| 400 | Bad request (invalid input) |
| 401 | Unauthorized (invalid/missing token) |
| 404 | Not found (device doesn't exist or not owned by user) |
| 405 | Method not allowed |

---

## Important Notes

- **Email Format**: Must be a valid email address (e.g., `user@example.com`)
- **Unique Emails**: Each user must have a unique email address
- **Token Storage**: Store tokens securely (not in plain text)
- **Password Requirements**: Recommend minimum 8 characters with mixed case
- **HTTPS**: Use HTTPS in production (not HTTP)

