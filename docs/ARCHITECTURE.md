# Loggin Genie - Architecture Overview

## Component Communication Flow

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         User's Browser                       │
│                     (http://localhost:8080)                  │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   │ HTTP Requests
                   │ (HTML/CSS/JS, API calls)
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                     Nginx Web Server                         │
│                    (Container: web)                          │
│                    Port: 8080 → 80                          │
├─────────────────────────────────────────────────────────────┤
│  Serves:                                                     │
│  • /login.html                                              │
│  • /index.html                                              │
│  • Static assets (CSS/JS)                                   │
│                                                              │
│  Proxies:                                                    │
│  • /api/* → http://api:3000/api/*                          │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   │ Proxy requests to API
                   │ (via Docker network)
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                   Node.js API Server                         │
│                   (Container: api)                           │
│                   Port: 3000                                 │
├─────────────────────────────────────────────────────────────┤
│  Handles:                                                    │
│  • Authentication (JWT)                                      │
│  • File uploads                                              │
│  • Job management                                            │
│  • Rate limiting                                             │
│                                                              │
│  When decryption needed:                                     │
│  1. Saves uploaded file to /app/uploads                     │
│  2. Spawns Python CLI process                               │
│  3. Monitors job status                                      │
│  4. Returns results from /app/output                        │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   │ Spawns subprocess:
                   │ python3 /app/loggin_genie.py
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│               Python Decryption Engine                       │
│               (Runs in API container)                        │
│               (No separate container needed)                 │
├─────────────────────────────────────────────────────────────┤
│  Executes:                                                   │
│  • Reads file from /app/uploads                             │
│  • Decrypts using AES algorithms                            │
│  • Writes results to /app/output                            │
│  • Exits when complete                                      │
└─────────────────────────────────────────────────────────────┘
```

---

## Detailed Communication Paths

### 1. User Login Flow

```
Browser                  Nginx                    API Server
   │                       │                          │
   │─────GET /───────────>│                          │
   │                       │                          │
   │<──index.html─────────│                          │
   │                       │                          │
   │──checkAuth()─────────>│                          │
   │                       │                          │
   │                       │──GET /api/auth/status──>│
   │                       │                          │
   │                       │<─────401 Unauthorized───│
   │                       │                          │
   │<──Redirect to login──│                          │
   │                       │                          │
   │──GET /login.html────>│                          │
   │<──login.html─────────│                          │
   │                       │                          │
   │──POST /api/auth/login>│                          │
   │  {username, password} │                          │
   │                       │──POST /api/auth/login──>│
   │                       │                          │
   │                       │                     ┌────┴────┐
   │                       │                     │ Verify  │
   │                       │                     │ bcrypt  │
   │                       │                     │ hash    │
   │                       │                     └────┬────┘
   │                       │                          │
   │                       │<─{token, cookie}─────────│
   │<──{token, cookie}────│                          │
   │                       │                          │
   │──Redirect to /───────>│                          │
```

### 2. File Upload & Decryption Flow

```
Browser              Nginx              API Server           Python CLI
   │                   │                    │                    │
   │──Upload file─────>│                    │                    │
   │  + JWT token      │                    │                    │
   │                   │                    │                    │
   │                   │──POST /api/───────>│                    │
   │                   │  decrypt/file      │                    │
   │                   │  + Bearer token    │                    │
   │                   │  + FormData        │                    │
   │                   │                    │                    │
   │                   │              ┌─────┴─────┐              │
   │                   │              │ Validate  │              │
   │                   │              │ JWT token │              │
   │                   │              └─────┬─────┘              │
   │                   │                    │                    │
   │                   │              ┌─────┴─────┐              │
   │                   │              │ Save file │              │
   │                   │              │ to volume │              │
   │                   │              │ /uploads  │              │
   │                   │              └─────┬─────┘              │
   │                   │                    │                    │
   │                   │              ┌─────┴─────┐              │
   │                   │              │ Create    │              │
   │                   │              │ job ID    │              │
   │                   │              └─────┬─────┘              │
   │                   │                    │                    │
   │                   │<─{jobId}───────────│                    │
   │<──{jobId}─────────│                    │                    │
   │                   │                    │                    │
   │                   │                    │─spawn──────────────>│
   │                   │                    │ python3 CLI        │
   │                   │                    │ --file uploads/X   │
   │                   │                    │                    │
   │                   │                    │              ┌─────┴─────┐
   │                   │                    │              │ Read file │
   │                   │                    │              │ from disk │
   │                   │                    │              └─────┬─────┘
   │                   │                    │                    │
   │                   │                    │              ┌─────┴─────┐
   │                   │                    │              │ Decrypt   │
   │                   │                    │              │ each log  │
   │                   │                    │              └─────┬─────┘
   │                   │                    │                    │
   │                   │                    │              ┌─────┴─────┐
   │                   │                    │              │ Write to  │
   │                   │                    │              │ /output/  │
   │                   │                    │              └─────┬─────┘
   │                   │                    │                    │
   │                   │                    │<─exit code 0───────│
   │                   │                    │                    │
   │──Poll status─────>│                    │                    │
   │  GET /api/jobs/X  │                    │                    │
   │                   │──GET /api/jobs/X──>│                    │
   │                   │                    │                    │
   │                   │              ┌─────┴─────┐              │
   │                   │              │ Check job │              │
   │                   │              │ status    │              │
   │                   │              └─────┬─────┘              │
   │                   │                    │                    │
   │                   │<─{status:complete}─│                    │
   │<──{status}────────│                    │                    │
   │                   │                    │                    │
   │──Get result──────>│                    │                    │
   │  /api/jobs/X/     │                    │                    │
   │  result           │──GET /api/jobs/X/─>│                    │
   │                   │  result            │                    │
   │                   │              ┌─────┴─────┐              │
   │                   │              │ Read from │              │
   │                   │              │ /output/  │              │
   │                   │              └─────┬─────┘              │
   │                   │                    │                    │
   │                   │<─{decrypted logs}──│                    │
   │<──{logs}──────────│                    │                    │
   │                   │                    │                    │
   │  Display results  │                    │                    │
```

---

## Network Communication

### Docker Network: `loggin-genie-network`

All containers are on the same Docker network and can communicate using container names:

```yaml
networks:
  loggin-genie-network:
    driver: bridge
```

**Container Hostnames**:
- `web` → nginx container
- `api` → Node.js API container  
- `python-worker` → Python container (not actively used)

### Port Mappings

```
Host Machine          Docker Network         Container
─────────────────────────────────────────────────────
localhost:8080  →→→  web:80          →→→  nginx
localhost:3000  →→→  api:3000        →→→  node.js
```

### Volume Sharing

Both API and Python CLI share the same volumes:

```yaml
volumes:
  - ./uploads:/app/uploads    # Shared file upload storage
  - ./output:/app/output      # Shared output storage
```

**How it works**:
1. API receives file → saves to `/app/uploads` → maps to `./uploads` on host
2. Python CLI reads from `/app/uploads` → same files
3. Python CLI writes to `/app/output` → maps to `./output` on host
4. API reads from `/app/output` → same files

---

## Communication Methods

### 1. HTTP/REST (Browser ↔ Nginx ↔ API)

**Protocol**: HTTP/1.1  
**Format**: JSON  
**Authentication**: JWT Bearer tokens + HTTP-only cookies

```javascript
// Example: Browser → API
fetch('http://localhost:8080/api/jobs', {
  method: 'GET',
  headers: {
    'Authorization': 'Bearer eyJhbGc...',
    'Content-Type': 'application/json'
  },
  credentials: 'include'  // Include cookies
})
```

**Nginx Proxy Configuration**:
```nginx
location /api/ {
  proxy_pass http://api:3000/api/;  # Forward to API container
  proxy_set_header Host $host;
  proxy_set_header X-Real-IP $remote_addr;
}
```

### 2. Process Spawning (API ↔ Python CLI)

**Method**: Node.js `child_process.spawn()`  
**Communication**: stdin/stdout/stderr streams  
**Working Directory**: `/app`

```javascript
// In API server.js
const { spawn } = require('child_process');

const python = spawn('python3', [
  '/app/loggin_genie.py',
  '--file', `/app/uploads/${filename}`,
  '--key', process.env.ENCRYPTION_KEY,
  '--algorithm', algorithm,
  '--field', field,
  '--output', outputPath,
  '--format', 'json'
]);

// Monitor process
python.stdout.on('data', (data) => {
  console.log(`Python: ${data}`);
});

python.on('close', (code) => {
  if (code === 0) {
    // Success - read output file
  }
});
```

### 3. File System (Shared Volumes)

**Method**: Disk I/O via Docker volumes  
**Location**: `/app/uploads` and `/app/output`

```
API writes:          /app/uploads/abc123.json
Python reads from:   /app/uploads/abc123.json
Python writes to:    /app/output/abc123.json
API reads from:      /app/output/abc123.json
```

---

## Data Flow Example: Decrypt a Log File

### Step-by-Step Communication

```
1. Browser → Nginx
   POST http://localhost:8080/api/decrypt/file
   Headers: Authorization: Bearer <token>
   Body: FormData with file

2. Nginx → API
   Proxies to: http://api:3000/api/decrypt/file
   Preserves all headers and body

3. API: Authentication
   • Extracts Bearer token from Authorization header
   • Calls verifyToken(token) from auth.js
   • Validates JWT signature with JWT_SECRET
   • Extracts user info {username, role}
   • Attaches to req.user

4. API: File Processing
   • Multer middleware intercepts multipart/form-data
   • Saves file to /app/uploads/xyz123-original.json
   • Generates unique job ID: "xyz123"
   • Creates job object in memory Map

5. API → Python CLI
   • Spawns subprocess:
     spawn('python3', [
       '/app/loggin_genie.py',
       '--file', '/app/uploads/xyz123-original.json',
       '--key', 'ENCRYPTION_KEY',
       '--algorithm', 'AES-256-CBC',
       '--field', 'encrypted_message',
       '--output', '/app/output/xyz123.json'
     ])

6. Python CLI Execution
   • Reads file from /app/uploads/xyz123-original.json
   • Parses JSON/NDJSON format
   • For each log entry:
     - Extracts encrypted_message field
     - Decrypts using AES-256-CBC
     - Replaces with decrypted text
   • Writes results to /app/output/xyz123.json
   • Exits with code 0

7. API: Job Completion
   • Detects python process exit
   • Updates job status to "completed"
   • Stores output path

8. Browser → API (Polling)
   GET http://localhost:8080/api/jobs/xyz123
   Headers: Authorization: Bearer <token>

9. API → Browser
   Response: {status: "completed", ...}

10. Browser → API (Get Results)
    GET http://localhost:8080/api/jobs/xyz123/result
    Headers: Authorization: Bearer <token>

11. API: Read Results
    • Reads /app/output/xyz123.json from disk
    • Parses JSON
    • Returns to browser

12. Browser: Display
    • Receives decrypted logs
    • Renders in UI with syntax highlighting
```

---

## Environment Variables Communication

### How Containers Share Configuration

```
.env file (host)
     ↓
docker-compose.yml reads .env
     ↓
Passes to containers as environment variables
     ↓
Containers read from process.env / os.environ
```

**Example Flow**:

```yaml
# docker-compose.yml
services:
  api:
    environment:
      - ENCRYPTION_KEY=${ENCRYPTION_KEY}    # From .env
      - JWT_SECRET=${JWT_SECRET}            # From .env
```

```javascript
// In API container (server.js)
const encryptionKey = process.env.ENCRYPTION_KEY;  // Available!
```

```python
# In Python CLI (loggin_genie.py)
encryption_key = os.getenv('ENCRYPTION_KEY')  # Available!
```

---

## Security in Communication

### 1. Authentication Layer

```
Browser → API: JWT in two places
├── HTTP Header: Authorization: Bearer <token>
└── Cookie: token=<token> (httpOnly, secure)
```

### 2. Network Isolation

```
External Network:
  - Only ports 8080 and 3000 exposed to host

Internal Docker Network:
  - All containers can talk to each other
  - Python worker not exposed externally
```

### 3. Rate Limiting

```
API applies limits:
├── Login endpoint: 5 attempts / 15 min
└── API endpoints: 100 requests / 15 min
```

---

## Common Communication Patterns

### Pattern 1: Authenticated API Call

```javascript
// 1. Browser gets token
const token = localStorage.getItem('token');

// 2. Browser makes request
const response = await fetch('/api/jobs', {
  headers: {
    'Authorization': `Bearer ${token}`
  },
  credentials: 'include'
});

// 3. Nginx proxies to API
// 4. API validates token
// 5. API processes request
// 6. API returns response
// 7. Browser receives data
```

### Pattern 2: Background Job

```javascript
// 1. API starts job
const jobId = generateJobId();
jobs.set(jobId, { status: 'processing' });

// 2. API spawns Python process
const python = spawn('python3', [...]);

// 3. API returns immediately
res.json({ jobId });

// 4. Browser polls for status
setInterval(() => {
  fetch(`/api/jobs/${jobId}`)
    .then(r => r.json())
    .then(job => {
      if (job.status === 'completed') {
        // Get results
      }
    });
}, 1000);

// 5. Python finishes in background
// 6. API detects completion
// 7. Browser gets results
```

### Pattern 3: Error Propagation

```
Python CLI error
     ↓
stderr stream
     ↓
API captures
     ↓
Updates job.error
     ↓
Browser polls
     ↓
Displays error to user
```

---

## Monitoring Communication

### View Network Traffic

```bash
# API logs show all requests
docker-compose logs -f api

# Example output:
# ::1 - - [02/Feb/2026:20:00:00 +0000] "POST /api/auth/login HTTP/1.1" 200
# ::1 - - [02/Feb/2026:20:00:05 +0000] "GET /api/jobs HTTP/1.1" 200
```

### Debug Container Communication

```bash
# Enter API container
docker-compose exec api sh

# Test connection to web container
wget -O- http://web:80/login.html

# Check if Python CLI is available
python3 /app/loggin_genie.py --help

# View shared volumes
ls -la /app/uploads
ls -la /app/output
```

### Network Inspection

```bash
# View network details
docker network inspect loggin_genie_loggin-genie-network

# Shows:
# - Container IP addresses
# - Network gateway
# - Connected containers
```

---

## Summary

### Key Communication Mechanisms

1. **HTTP/REST** → Browser ↔ Nginx ↔ API
2. **Process Spawning** → API ↔ Python CLI
3. **Shared Volumes** → API ↔ Python (file I/O)
4. **Docker Network** → Container-to-container
5. **Environment Variables** → Configuration sharing
6. **JWT Tokens** → Authentication across components

### Why This Architecture?

✅ **Separation of Concerns**: Each component has one job  
✅ **Scalability**: Can run multiple API instances  
✅ **Security**: Network isolation + authentication  
✅ **Simplicity**: Python runs in API container (no separate service needed)  
✅ **Flexibility**: Can swap Python CLI for other decryption tools  
✅ **Maintainability**: Clear boundaries between components  

---

**Questions?** Check `DEPLOYMENT_STATUS.md` or `COMMANDS_CHEATSHEET.md` for more details!
