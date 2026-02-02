# Authentication Guide

This document describes the authentication system implemented in Loggin Genie.

## Overview

Loggin Genie uses JWT (JSON Web Token) authentication to protect the web interface and API endpoints. This ensures that only authorized users can decrypt and view sensitive log data.

## Features

- **JWT-based authentication**: Secure token-based auth with 24-hour expiration
- **Password hashing**: bcrypt with salt rounds for secure password storage
- **HTTP-only cookies**: Tokens stored in secure cookies to prevent XSS attacks
- **Rate limiting**: Protection against brute-force attacks
- **Session management**: Automatic logout on token expiration
- **Default admin user**: Pre-configured admin account for quick setup

## Default Credentials

```
Username: admin
Password: admin
```

⚠️ **IMPORTANT**: Change the default password in production!

## Architecture

### Components

1. **api/auth.js** - JWT token generation and verification middleware
2. **api/users.js** - User management with bcrypt password hashing
3. **web/login.html** - Login page with form validation
4. **web/index.html** - Protected main application with session checks

### Authentication Flow

```
1. User visits application → Redirected to /login.html
2. User enters credentials → POST /api/auth/login
3. Server validates with bcrypt → Generates JWT token
4. Token stored in cookie + localStorage → Redirect to /
5. All API calls include token → Validated by authMiddleware
6. Token expires after 24h → Automatic logout
```

## API Endpoints

### Public Endpoints

- `GET /health` - Health check (shows auth status)

### Authentication Endpoints

- `POST /api/auth/login` - Login with username/password
- `POST /api/auth/logout` - Clear authentication token
- `GET /api/auth/status` - Check current authentication status

### Protected Endpoints

All decryption and job management endpoints require authentication:

- `POST /api/decrypt/file` - Upload and decrypt log file
- `POST /api/decrypt/kibana` - Decrypt from Kibana/Elasticsearch
- `GET /api/jobs` - List all jobs
- `GET /api/jobs/:jobId` - Get job status
- `GET /api/jobs/:jobId/result` - Get job result
- `GET /api/jobs/:jobId/download` - Download job result
- `DELETE /api/jobs/:jobId` - Delete job

## Configuration

### Environment Variables

Add to your `.env` file:

```bash
# JWT Secret for authentication
# Generate a new one with: openssl rand -base64 32
JWT_SECRET=your-super-secret-jwt-key-change-in-production
```

### Docker Compose

The JWT_SECRET is automatically passed to the API container:

```yaml
api:
  environment:
    - JWT_SECRET=${JWT_SECRET:-your-super-secret-jwt-key-change-in-production}
```

## Security Features

### 1. Password Hashing

Passwords are hashed using bcrypt with 10 salt rounds:

```javascript
const hashedPassword = await bcrypt.hash(password, 10);
```

### 2. JWT Tokens

- 24-hour expiration
- Signed with HS256 algorithm
- Contains user ID, username, and role

### 3. HTTP-Only Cookies

Tokens are stored in secure cookies:

```javascript
res.cookie('token', token, {
  httpOnly: true,
  secure: process.env.NODE_ENV === 'production',
  maxAge: 24 * 60 * 60 * 1000, // 24 hours
  sameSite: 'lax'
});
```

### 4. Rate Limiting

- **API endpoints**: 100 requests per 15 minutes
- **Login endpoint**: 5 attempts per 15 minutes

### 5. CORS Protection

Configured to accept credentials only from trusted origins.

## User Management

### In-Memory User Store

Current implementation uses an in-memory Map for user storage. For production, consider:

- Database integration (PostgreSQL, MongoDB)
- User registration endpoint
- Password reset functionality
- Role-based access control (RBAC)

### Adding Users

Edit `api/users.js` to add more users:

```javascript
async function initializeDefaultUsers() {
  const defaultUsers = [
    { username: 'admin', password: 'admin', role: 'admin' },
    { username: 'user1', password: 'password123', role: 'user' }
  ];
  
  for (const userData of defaultUsers) {
    await addUser(userData.username, userData.password, userData.role);
  }
}
```

## Frontend Integration

### Authentication Check

The main application checks authentication on load:

```javascript
async function checkAuth() {
  const response = await fetch(`${API_URL}/api/auth/status`, {
    credentials: 'include'
  });
  
  if (response.ok) {
    const data = await response.json();
    if (data.authenticated) {
      // Show user info
      return true;
    }
  }
  
  // Redirect to login
  window.location.href = '/login.html';
  return false;
}
```

### Authenticated Requests

All API calls use the `authenticatedFetch` wrapper:

```javascript
async function authenticatedFetch(url, options = {}) {
  const token = localStorage.getItem('token');
  
  const defaultOptions = {
    credentials: 'include',
    headers: {
      ...options.headers,
      'Authorization': token ? `Bearer ${token}` : ''
    }
  };

  const response = await fetch(url, { ...options, ...defaultOptions });

  // Auto-redirect on 401
  if (response.status === 401) {
    localStorage.removeItem('token');
    window.location.href = '/login.html';
    throw new Error('Unauthorized');
  }

  return response;
}
```

### Logout

```javascript
async function handleLogout() {
  await fetch(`${API_URL}/api/auth/logout`, {
    method: 'POST',
    credentials: 'include'
  });
  
  localStorage.removeItem('token');
  window.location.href = '/login.html';
}
```

## Testing

### Manual Testing

1. **Login Flow**:
   ```bash
   # Start the application
   docker-compose up -d
   
   # Visit http://localhost
   # Should redirect to /login.html
   
   # Login with admin/admin
   # Should redirect to /
   ```

2. **API Authentication**:
   ```bash
   # Try accessing protected endpoint without auth
   curl http://localhost:3000/api/jobs
   # Should return 401 Unauthorized
   
   # Login
   TOKEN=$(curl -X POST http://localhost:3000/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"username":"admin","password":"admin"}' \
     | jq -r '.token')
   
   # Access with token
   curl http://localhost:3000/api/jobs \
     -H "Authorization: Bearer $TOKEN"
   # Should return jobs list
   ```

3. **Token Expiration**:
   ```bash
   # Wait 24 hours or modify JWT_EXPIRES_IN in auth.js
   # Token should expire and require re-login
   ```

## Production Recommendations

### 1. Change Default Credentials

Update the default admin password immediately:

```javascript
// api/users.js
async function initializeDefaultUsers() {
  await addUser('admin', 'your-strong-password-here', 'admin');
}
```

### 2. Use Strong JWT Secret

Generate a cryptographically secure secret:

```bash
openssl rand -base64 64
```

Add to `.env`:

```bash
JWT_SECRET=<generated-secret>
```

### 3. Enable HTTPS

Update nginx configuration for SSL:

```nginx
server {
    listen 443 ssl http2;
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    # ... rest of config
}
```

### 4. Add Database Storage

Replace in-memory user store with a database:

```javascript
// Example with PostgreSQL
const { Pool } = require('pg');
const pool = new Pool({ connectionString: process.env.DATABASE_URL });

async function authenticateUser(username, password) {
  const result = await pool.query(
    'SELECT * FROM users WHERE username = $1',
    [username]
  );
  
  if (result.rows.length === 0) return null;
  
  const user = result.rows[0];
  const isValid = await bcrypt.compare(password, user.password_hash);
  
  return isValid ? { username: user.username, role: user.role } : null;
}
```

### 5. Implement Audit Logging

Log authentication events:

```javascript
// Log successful logins
logger.info(`User ${username} logged in from ${ip}`);

// Log failed attempts
logger.warn(`Failed login attempt for ${username} from ${ip}`);

// Log API access
logger.info(`User ${username} accessed ${endpoint}`);
```

### 6. Add Multi-Factor Authentication (MFA)

Consider implementing TOTP-based MFA for enhanced security.

### 7. Session Management

Add features like:
- Remember me functionality
- Active session list
- Force logout from all devices
- Session timeout warnings

## Troubleshooting

### Issue: "Invalid credentials" on correct password

**Solution**: Check that bcrypt is properly installed and passwords are hashed:

```bash
cd api
npm list bcryptjs
```

### Issue: Token not persisted across page reloads

**Solution**: Ensure cookies are enabled and localStorage is accessible:

```javascript
// Check in browser console
console.log(localStorage.getItem('token'));
console.log(document.cookie);
```

### Issue: CORS errors on login

**Solution**: Update CORS configuration in server.js:

```javascript
app.use(cors({
  origin: process.env.CORS_ORIGIN || true,
  credentials: true
}));
```

### Issue: Rate limit hit too quickly

**Solution**: Adjust rate limit settings in server.js:

```javascript
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 200 // Increase from 100
});
```

## Support

For issues or questions about authentication:

1. Check the [main README](../README.md)
2. Review server logs: `docker-compose logs api`
3. Check browser console for frontend errors
4. Verify JWT_SECRET is set in .env

## License

See main project LICENSE file.
