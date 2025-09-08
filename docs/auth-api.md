<div align="center">

# 🔒 Chitthi Authentication API

### _Secure • Fast • Reliable_

---

**Professional API Documentation for E2E Encrypted Chat Platform**

</div>

<br>

## 📋 Table of Contents

- [🚀 Quick Start](#-quick-start)
- [🔐 Authentication Endpoints](#-authentication-endpoints)
- [👤 User Management](#-user-management)
- [🔑 Password Management](#-password-management)
- [📊 API Reference](#-api-reference)
- [⚡ Rate Limits](#-rate-limits)
- [🛡️ Security](#️-security)

---

## 🚀 Quick Start

### Base URL

```
https://api.chitthi.com/v1
```

### Authentication Header

```http
Authorization: Bearer <your-jwt-token>
```

### Quick Test

```bash
# Test your token
curl -X POST "https://api.chitthi.com/v1/login/test-token" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

<br>

---

## 🔐 Authentication Endpoints

<br>

### 🎯 **Login Access Token**

> **`POST`** `/login/access-token`

**OAuth2 compatible token authentication for secure API access**

<details>
<summary><strong>📝 Request Details</strong></summary>

```http
POST /v1/login/access-token
Content-Type: application/x-www-form-urlencoded
```

**Parameters:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `username` | string | ✅ | User's email address |
| `password` | string | ✅ | User's password |
| `grant_type` | string | ❌ | OAuth2 grant type (default: password) |

</details>

<details>
<summary><strong>✅ Success Response</strong></summary>

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

</details>

<details>
<summary><strong>🚨 Error Responses</strong></summary>

| Status | Description         | Response                                    |
| ------ | ------------------- | ------------------------------------------- |
| `400`  | Invalid credentials | `{"detail": "Incorrect email or password"}` |
| `422`  | Validation error    | `{"detail": "Invalid input format"}`        |

</details>

<details>
<summary><strong>🛠️ Example Usage</strong></summary>

```bash
curl -X POST "https://api.chitthi.com/v1/login/access-token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=alice@example.com&password=secure123"
```

**Response:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhbGljZUBleGFtcGxlLmNvbSIsImV4cCI6MTYzOTk4ODgwMH0.signature",
  "token_type": "bearer"
}
```

</details>

<br>

---

### 🔍 **Token Validation**

> **`POST`** `/login/test-token`

**Verify token validity and retrieve current user information**

<details>
<summary><strong>📝 Request Details</strong></summary>

```http
POST /v1/login/test-token
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Headers:**
| Field | Value | Required |
|-------|-------|----------|
| `Authorization` | Bearer `<token>` | ✅ |

</details>

<details>
<summary><strong>✅ Success Response</strong></summary>

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "username": "alice_smith",
  "email": "alice@example.com",
  "display_name": "Alice Smith",
  "is_active": true,
  "is_superuser": false
}
```

</details>

<br>

---

## 👤 User Registration

### POST `/users/signup`

**Register a new user account**

Create a new user account without requiring authentication.

#### Request

```json
{
  "username": "alice_smith",
  "email": "alice@example.com",
  "password": "secure_password123",
  "display_name": "Alice Smith",
  "about": "Software engineer passionate about privacy"
}
```

**Schema:**

- `username` (string, required): Unique username (max 64 chars)
- `email` (string, required): Valid email address (max 255 chars)
- `password` (string, required): Password (8-128 chars)
- `display_name` (string, optional): Display name (max 128 chars)
- `about` (string, optional): User bio/description
- `phone` (string, optional): Phone number (max 32 chars)
- `avatar_url` (string, optional): Profile picture URL
- `locale` (string, optional): Language preference (max 16 chars)
- `timezone` (string, optional): Timezone (max 64 chars)

#### Response

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "username": "alice_smith",
  "email": "alice@example.com",
  "display_name": "Alice Smith",
  "about": "Software engineer passionate about privacy",
  "avatar_url": null,
  "locale": null,
  "timezone": null,
  "is_active": true,
  "is_bot": false,
  "is_superuser": false
}
```

#### Status Codes

- `200` - User created successfully
- `400` - Email already exists
- `422` - Validation error

#### Example

```bash
curl -X POST "https://api.example.com/api/v1/users/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice_smith",
    "email": "alice@example.com",
    "password": "secure_password123",
    "display_name": "Alice Smith"
  }'
```

---

## 🔑 Password Management

### POST `/password-recovery/{email}`

**Request password recovery**

Send a password reset email to the specified email address.

#### Request

```http
POST /api/v1/password-recovery/alice@example.com
```

#### Response

```json
{
  "message": "Password recovery email sent"
}
```

#### Status Codes

- `200` - Recovery email sent
- `404` - User with email not found

---

### POST `/reset-password/`

**Reset password with token**

Reset user password using the token received via email.

#### Request

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "new_password": "new_secure_password123"
}
```

**Schema:**

- `token` (string, required): Password reset token from email
- `new_password` (string, required): New password (8-40 chars)

#### Response

```json
{
  "message": "Password updated successfully"
}
```

#### Status Codes

- `200` - Password updated successfully
- `400` - Invalid token or inactive user
- `404` - User not found

---

## 👥 User Management (Admin)

### GET `/users/`

**List all users** _(Superuser only)_

Retrieve a paginated list of all users.

#### Request

```http
GET /api/v1/users/?skip=0&limit=100
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Query Parameters:**

- `skip` (integer, optional): Number of records to skip (default: 0)
- `limit` (integer, optional): Maximum records to return (default: 100, max: 100)

#### Response

```json
{
  "data": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "username": "alice_smith",
      "email": "alice@example.com",
      "display_name": "Alice Smith",
      "is_active": true,
      "is_superuser": true
    }
  ],
  "count": 1
}
```

---

### POST `/users/`

**Create user** _(Superuser only)_

Create a new user account with admin privileges.

#### Request

```json
{
  "username": "bob_admin",
  "email": "bob@example.com",
  "password": "admin_password123",
  "display_name": "Bob Admin",
  "is_superuser": true,
  "is_active": true
}
```

---

### GET `/users/{user_id}`

**Get user by ID**

Retrieve specific user information. Users can only see their own profile unless they're a superuser.

#### Request

```http
GET /api/v1/users/123e4567-e89b-12d3-a456-426614174000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### Response

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "username": "alice_smith",
  "email": "alice@example.com",
  "display_name": "Alice Smith",
  "about": "Software engineer passionate about privacy",
  "is_active": true,
  "is_superuser": false
}
```

---

## 🔧 User Profile Management

### PATCH `/users/me`

**Update current user profile**

Update the authenticated user's profile information.

#### Request

```json
{
  "display_name": "Alice Smith Updated",
  "about": "Senior software engineer specializing in cryptography",
  "avatar_url": "https://example.com/avatar.jpg",
  "locale": "en",
  "timezone": "UTC"
}
```

**Schema (all fields optional):**

- `display_name` (string): Display name
- `about` (string): User bio
- `avatar_url` (string): Profile picture URL
- `locale` (string): Language preference
- `timezone` (string): User timezone

#### Response

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "username": "alice_smith",
  "email": "alice@example.com",
  "display_name": "Alice Smith Updated",
  "about": "Senior software engineer specializing in cryptography",
  "avatar_url": "https://example.com/avatar.jpg",
  "locale": "en",
  "timezone": "UTC",
  "is_active": true,
  "is_superuser": false
}
```

---

### PATCH `/users/me/password`

**Update current user password**

Change the authenticated user's password.

#### Request

```json
{
  "current_password": "current_password123",
  "new_password": "new_secure_password456"
}
```

**Schema:**

- `current_password` (string, required): Current password
- `new_password` (string, required): New password (8-40 chars)

#### Response

```json
{
  "message": "Password updated successfully"
}
```

---

## 🔒 Authentication Headers

All protected endpoints require authentication via Bearer token:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Error Responses

### Standard Error Format

```json
{
  "detail": "Error description"
}
```

### Validation Error Format

```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "password"],
      "msg": "String should have at least 8 characters",
      "input": "123"
    }
  ]
}
```

## HTTP Status Codes

| Code  | Description                          |
| ----- | ------------------------------------ |
| `200` | Success                              |
| `400` | Bad Request (invalid data)           |
| `401` | Unauthorized (invalid/missing token) |
| `403` | Forbidden (insufficient permissions) |
| `404` | Not Found                            |
| `422` | Validation Error                     |
| `500` | Internal Server Error                |

---

## Authentication Schemas

### Token Schema

```json
{
  "access_token": "string",
  "token_type": "bearer"
}
```

### User Registration Schema

```json
{
  "username": "string (required, max 64)",
  "email": "string (required, max 255, valid email)",
  "password": "string (required, 8-128 chars)",
  "display_name": "string (optional, max 128)",
  "about": "string (optional)",
  "phone": "string (optional, max 32)",
  "avatar_url": "string (optional)",
  "locale": "string (optional, max 16)",
  "timezone": "string (optional, max 64)"
}
```

### User Public Schema

```json
{
  "id": "uuid",
  "username": "string",
  "email": "string",
  "display_name": "string",
  "about": "string",
  "avatar_url": "string",
  "locale": "string",
  "timezone": "string",
  "is_active": "boolean",
  "is_bot": "boolean",
  "is_superuser": "boolean"
}
```

---

## Security Notes

1. **Password Requirements**: Minimum 8 characters, maximum 128 characters
2. **Token Expiration**: Access tokens expire based on server configuration
3. **Rate Limiting**: API may implement rate limiting on authentication endpoints
4. **HTTPS Required**: All authentication endpoints should only be used over HTTPS
5. **Password Reset Tokens**: Reset tokens have limited validity and single use
6. **User Permissions**: Regular users can only access their own data; superusers have full access

---

## Example Integration

### JavaScript/TypeScript Example

```typescript
class AuthAPI {
  private baseURL = "https://api.example.com/api/v1";
  private token: string | null = null;

  async login(email: string, password: string): Promise<string> {
    const response = await fetch(`${this.baseURL}/login/access-token`, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: `username=${encodeURIComponent(
        email
      )}&password=${encodeURIComponent(password)}`,
    });

    if (!response.ok) {
      throw new Error("Login failed");
    }

    const data = await response.json();
    this.token = data.access_token;
    return this.token;
  }

  async register(userData: RegisterData): Promise<User> {
    const response = await fetch(`${this.baseURL}/users/signup`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(userData),
    });

    if (!response.ok) {
      throw new Error("Registration failed");
    }

    return await response.json();
  }

  async getCurrentUser(): Promise<User> {
    if (!this.token) {
      throw new Error("Not authenticated");
    }

    const response = await fetch(`${this.baseURL}/login/test-token`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${this.token}`,
      },
    });

    if (!response.ok) {
      throw new Error("Failed to get current user");
    }

    return await response.json();
  }
}
```

This documentation provides a comprehensive guide to all authentication-related endpoints in your E2E encrypted chat backend. The API follows RESTful principles and includes proper error handling, validation, and security considerations.
