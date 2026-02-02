# Quick Start Guide - LogGin Genie 🧞‍♂️

## 🚀 Access the Application

**URL:** http://localhost:8080

## 🔐 Login

- **Username:** `admin`
- **Password:** `admin`

## 📁 Test with Sample Data

### Step 1: Navigate to File Upload
Click on the **"📁 File Upload"** tab (should be active by default)

### Step 2: Select Log File
Click "Choose File" and select:
```
examples/kibana_logs_elasticsearch.json
```

### Step 3: Enter Encryption Key

**Option A - Direct Text Input:**
```
04c8ec0929fb619f3da9151d542ef41591044245bebb0cb22f9704645a99e948
```

**Option B - Create and Upload Key File:**
```bash
# Create key file
echo "04c8ec0929fb619f3da9151d542ef41591044245bebb0cb22f9704645a99e948" > encryption_key.txt

# Then upload encryption_key.txt using the "Key File" input field
```

### Step 4: Configure Settings
- **Algorithm:** `AES-256-CBC` (default)
- **Encrypted Field Name:** `message` (default)

### Step 5: Decrypt
Click the **"🔓 Decrypt Logs"** button

## 🎨 What You'll See

### Diff View
Each log entry shows a side-by-side comparison:

**Left Side (Red):** 🔒 Encrypted message
```
AES:BASE64:iv:encrypted_data_here...
```

**Right Side (Green):** 🔓 Decrypted message
```
User john.doe logged in successfully
```

### Log Levels
Color-coded badges:
- 🔴 **ERROR** - Red badge
- 🟡 **WARN** - Yellow badge
- 🔵 **INFO** - Blue badge
- 🟢 **DEBUG** - Green badge

### Sample Log Content
The test file contains 50 logs from 5 microservices:
- **user-service** - Login, registration, profile updates
- **auth-service** - Token validation, session management
- **payment-service** - Transactions, payment processing
- **notification-service** - Email, push notifications
- **analytics-service** - User behavior, event tracking

## 🎯 Alternative: NDJSON Format

You can also test with the NDJSON (newline-delimited JSON) format:
```
examples/kibana_logs_stream.ndjson
```

Same key and settings apply!

## ⚙️ Docker Commands

### Check Container Status
```bash
docker-compose ps
```

### View API Logs
```bash
docker-compose logs -f api
```

### View All Logs
```bash
docker-compose logs -f
```

### Restart Services
```bash
docker-compose restart
```

### Stop Services
```bash
docker-compose down
```

### Rebuild and Restart
```bash
docker-compose build && docker-compose up -d
```

## 🔍 API Health Check
```bash
curl http://localhost:3000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2026-02-02T20:28:00.000Z",
  "version": "1.0.0"
}
```

## 📊 Features Overview

### ✅ Implemented
- **Dark Blue/Green Theme** - Cyberpunk aesthetic with fog effects
- **Diff View** - Side-by-side encrypted vs decrypted comparison
- **Key File Upload** - Support for both text input and file upload
- **Sample Data** - 50 realistic Kibana logs for testing
- **Fixed Containers** - All containers running stably
- **JWT Authentication** - Secure login with token-based auth
- **Rate Limiting** - Protected API endpoints
- **Job Management** - Background processing with job queue

### 🎨 UI Features
- Animated fog effects
- Glassmorphism cards
- Green glow on hover
- Smooth transitions
- Responsive design
- Color-coded status messages

## 🐛 Troubleshooting

### Login Not Working
1. Check API is running: `docker-compose ps`
2. Test login directly: `curl -X POST http://localhost:3000/api/auth/login -H "Content-Type: application/json" -d '{"username":"admin","password":"admin"}'`
3. Check browser console for errors (F12)

### Container Restarting
```bash
# Check logs
docker-compose logs python-worker

# Should see: Running tail -f /dev/null (not restarting)
```

### Decryption Fails
1. Verify key is correct (64 hex characters)
2. Check algorithm matches (AES-256-CBC for sample data)
3. Verify field name is correct (`message`)

### Can't Access UI
1. Check web container: `docker-compose ps`
2. Verify port 8080 is not in use: `lsof -i :8080`
3. Try restarting: `docker-compose restart web`

## 📚 Additional Documentation
- `ARCHITECTURE.md` - System architecture and design
- `DEPLOYMENT_STATUS.md` - Deployment details
- `AUTHENTICATION.md` - Security implementation
- `COMMANDS_CHEATSHEET.md` - Complete command reference
- `UPDATES_SUMMARY.md` - Latest changes and features
- `QUICKSTART_OLD.md` - Original CLI-based quickstart (deprecated)

## 🌐 Web Interface vs CLI

This application now features a modern web interface. The original CLI tool is still available but the web interface is recommended for ease of use.

### Using CLI (Advanced)
If you prefer command-line usage, see `QUICKSTART_OLD.md` for CLI commands.

---

**Happy Decrypting!** 🔓✨
