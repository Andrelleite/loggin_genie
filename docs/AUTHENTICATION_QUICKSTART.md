# Authentication Quick Start

## Default Credentials

```
Username: admin
Password: admin
```

⚠️ **Change these in production!**

## Quick Test

1. **Start the application**:
   ```bash
   docker-compose up -d
   ```

2. **Access the web UI**:
   ```
   http://localhost
   ```

3. **Login**:
   - You'll be automatically redirected to the login page
   - Enter username: `admin`, password: `admin`
   - Click "Sign In"
   - You'll be redirected to the main application

4. **Test API directly**:
   ```bash
   # Login and get token
   TOKEN=$(curl -X POST http://localhost:3000/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"username":"admin","password":"admin"}' \
     | jq -r '.token')
   
   # Use token to access protected endpoints
   curl http://localhost:3000/api/jobs \
     -H "Authorization: Bearer $TOKEN"
   ```

## What Changed

### Backend (Node.js API)

✅ **New Files**:
- `api/auth.js` - JWT authentication middleware
- `api/users.js` - User management with bcrypt

✅ **Updated Files**:
- `api/server.js` - Added login/logout endpoints, protected all API routes
- `api/package.json` - Added auth dependencies

✅ **New Dependencies**:
- `jsonwebtoken` - JWT token generation and verification
- `bcryptjs` - Password hashing
- `cookie-parser` - Cookie parsing for token storage
- `express-rate-limit` - Brute-force protection

### Frontend (Web UI)

✅ **New Files**:
- `web/login.html` - Beautiful login page with gradient design

✅ **Updated Files**:
- `web/index.html` - Added session management, logout button, auth checks
- All API calls now use `authenticatedFetch()` wrapper

### Configuration

✅ **New Environment Variables**:
- `JWT_SECRET` - Secret key for JWT signing (in `.env` and `docker-compose.yml`)

### Security Features

✅ **Implemented**:
- JWT-based authentication (24-hour token expiration)
- bcrypt password hashing (10 salt rounds)
- HTTP-only cookies for token storage
- Rate limiting (5 login attempts per 15 minutes)
- Auto-redirect on expired/invalid tokens
- CORS with credentials support

## Usage Examples

### Web Interface

1. **First Visit**: Redirected to `/login.html`
2. **After Login**: Shows username and logout button in header
3. **Session Active**: All API calls include auth token
4. **Token Expired**: Auto-logout and redirect to login

### API Endpoints

#### Public Endpoints

```bash
# Health check (shows auth status)
curl http://localhost:3000/health
```

#### Authentication

```bash
# Login
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'

# Check auth status
curl http://localhost:3000/api/auth/status \
  -H "Authorization: Bearer YOUR_TOKEN"

# Logout
curl -X POST http://localhost:3000/api/auth/logout
```

#### Protected Endpoints

All require `Authorization: Bearer TOKEN` header:

```bash
# Upload file for decryption
curl -X POST http://localhost:3000/api/decrypt/file \
  -H "Authorization: Bearer TOKEN" \
  -F "logFile=@logs.json" \
  -F "algorithm=AES-256-CBC" \
  -F "field=encrypted_message"

# List jobs
curl http://localhost:3000/api/jobs \
  -H "Authorization: Bearer TOKEN"

# Get job status
curl http://localhost:3000/api/jobs/JOB_ID \
  -H "Authorization: Bearer TOKEN"

# Get job result
curl http://localhost:3000/api/jobs/JOB_ID/result \
  -H "Authorization: Bearer TOKEN"

# Delete job
curl -X DELETE http://localhost:3000/api/jobs/JOB_ID \
  -H "Authorization: Bearer TOKEN"
```

## Troubleshooting

### Can't login

1. **Check server logs**:
   ```bash
   docker-compose logs api
   ```

2. **Verify default user initialized**:
   ```
   ✅ Default admin user initialized (username: admin, password: admin)
   ```

3. **Test API directly**:
   ```bash
   curl -X POST http://localhost:3000/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"username":"admin","password":"admin"}'
   ```

### Token not working

1. **Check JWT_SECRET is set**:
   ```bash
   grep JWT_SECRET .env
   ```

2. **Verify token format**:
   ```bash
   echo "YOUR_TOKEN" | cut -d. -f2 | base64 -d 2>/dev/null | jq
   ```

3. **Check token expiration** (valid for 24 hours)

### Rate limit hit

Wait 15 minutes or restart the API:
```bash
docker-compose restart api
```

### CORS errors

Update CORS origin in `.env`:
```bash
CORS_ORIGIN=http://localhost:8080
```

## Production Checklist

Before deploying to production:

- [ ] Change default admin password
- [ ] Generate new JWT_SECRET (use `openssl rand -base64 64`)
- [ ] Enable HTTPS/SSL
- [ ] Set up proper database for user storage
- [ ] Configure environment-specific CORS origins
- [ ] Enable audit logging
- [ ] Set up monitoring and alerts
- [ ] Review rate limit settings
- [ ] Add backup authentication method
- [ ] Document user management procedures

## More Information

See [AUTHENTICATION.md](./AUTHENTICATION.md) for detailed documentation.

## Test Results

✅ All authentication tests passed:
- Public health endpoint accessible
- Login with valid credentials works
- Login with invalid credentials denied
- Protected endpoints require authentication
- Token-based access works
- Auth status check works
- Logout clears session

🧞‍♂️ Your logs are now protected with authentication!
