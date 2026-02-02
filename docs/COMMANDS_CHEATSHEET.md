# Loggin Genie - Command Cheatsheet

## 🚀 Quick Start

```bash
# Start the application
docker-compose up -d

# Stop the application
docker-compose down

# View logs
docker-compose logs -f
```

## 🌐 Access URLs

- **Web Interface**: http://localhost:8080
- **API**: http://localhost:3000
- **Health Check**: http://localhost:3000/health

## 🔐 Default Credentials

```
Username: admin
Password: admin
```

## 📦 Docker Commands

### Startup & Shutdown
```bash
# Start all services
docker-compose up -d

# Start with build
docker-compose up -d --build

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart api
```

### Logs & Debugging
```bash
# View all logs (follow)
docker-compose logs -f

# View specific service logs
docker-compose logs -f api
docker-compose logs -f web

# View last 50 lines
docker-compose logs --tail=50 api

# View logs with timestamps
docker-compose logs -f -t api
```

### Container Management
```bash
# List running containers
docker-compose ps

# View container stats
docker stats

# Execute command in container
docker-compose exec api sh
docker-compose exec python-worker bash

# Rebuild specific service
docker-compose build api
docker-compose up -d api
```

## 🔑 Authentication API

### Login
```bash
# Get JWT token
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'

# Save token to variable
TOKEN=$(curl -s -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}' \
  | jq -r '.token')
```

### Check Auth Status
```bash
curl http://localhost:3000/api/auth/status \
  -H "Authorization: Bearer $TOKEN"
```

### Logout
```bash
curl -X POST http://localhost:3000/api/auth/logout
```

## 📤 File Upload & Decryption

### Upload File via API
```bash
# Using saved token
curl -X POST http://localhost:3000/api/decrypt/file \
  -H "Authorization: Bearer $TOKEN" \
  -F "logFile=@examples/test-production-key.json" \
  -F "algorithm=AES-256-CBC" \
  -F "field=encrypted_message"
```

### CLI Decryption
```bash
# Activate virtual environment first
source .venv/bin/activate

# Decrypt from file
python loggin_genie.py --file examples/test-production-key.json

# Decrypt from file with custom field
python loggin_genie.py \
  --file examples/test-production-key.json \
  --field encrypted_message \
  --algorithm AES-256-CBC

# Decrypt from Kibana
python loggin_genie.py \
  --kibana-url "https://your-kibana.com" \
  --index "logs-*" \
  --key "your-encryption-key" \
  --query '{"match": {"level": "error"}}'

# Save output to file
python loggin_genie.py \
  --file examples/test-production-key.json \
  --output decrypted_logs.json \
  --format json
```

## 🔍 Job Management API

### List All Jobs
```bash
curl http://localhost:3000/api/jobs \
  -H "Authorization: Bearer $TOKEN"
```

### Get Job Status
```bash
curl http://localhost:3000/api/jobs/JOB_ID \
  -H "Authorization: Bearer $TOKEN"
```

### Get Job Result
```bash
curl http://localhost:3000/api/jobs/JOB_ID/result \
  -H "Authorization: Bearer $TOKEN"
```

### Download Job Result
```bash
curl http://localhost:3000/api/jobs/JOB_ID/download \
  -H "Authorization: Bearer $TOKEN" \
  -O
```

### Delete Job
```bash
curl -X DELETE http://localhost:3000/api/jobs/JOB_ID \
  -H "Authorization: Bearer $TOKEN"
```

## 🧪 Testing Commands

### Test Encrypted Log Creation
```bash
# Activate venv first
source .venv/bin/activate

# Create test logs
python examples/create_production_test.py
python examples/create_sample_encrypted_logs.py
```

### Health Check
```bash
# API health
curl http://localhost:3000/health | jq

# Container health
docker-compose ps
```

### Test Login Flow
```bash
# Test invalid login
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"wrong"}'

# Test valid login
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'

# Test protected endpoint without auth
curl http://localhost:3000/api/jobs

# Test protected endpoint with auth
TOKEN=$(curl -s -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}' \
  | jq -r '.token')

curl http://localhost:3000/api/jobs \
  -H "Authorization: Bearer $TOKEN"
```

## 🔧 Maintenance Commands

### View Disk Usage
```bash
# Container sizes
docker-compose ps --format "table {{.Name}}\t{{.Size}}"

# Image sizes
docker images | grep loggin_genie

# Volume sizes
docker volume ls
```

### Clean Up
```bash
# Remove stopped containers
docker-compose rm

# Remove unused images
docker image prune

# Remove unused volumes
docker volume prune

# Full cleanup (careful!)
docker system prune -a
```

### Backup
```bash
# Backup volumes
docker-compose down
tar -czf backup-$(date +%Y%m%d).tar.gz uploads/ output/

# Restore volumes
tar -xzf backup-20260202.tar.gz
docker-compose up -d
```

## 📊 Monitoring

### Resource Usage
```bash
# Container stats (real-time)
docker stats

# Specific container
docker stats loggin-genie-api

# Disk usage
docker system df
```

### Logs Analysis
```bash
# Error logs
docker-compose logs | grep -i error

# Warning logs
docker-compose logs | grep -i warn

# Authentication logs
docker-compose logs api | grep -i "login\|auth"
```

## 🐛 Debugging

### Enter Container Shell
```bash
# API container
docker-compose exec api sh

# Python worker
docker-compose exec python-worker bash

# Web container
docker-compose exec web sh
```

### Check Environment Variables
```bash
# In API container
docker-compose exec api env | grep -E "JWT|ENCRYPTION"

# From host
docker-compose config
```

### Network Debugging
```bash
# Check port bindings
docker-compose port api 3000
docker-compose port web 80

# Test connectivity
docker-compose exec api wget -O- http://localhost:3000/health
```

## 📝 Environment Variables

```bash
# View current .env
cat .env

# Update encryption key
sed -i '' 's/ENCRYPTION_KEY=.*/ENCRYPTION_KEY=new-key-here/' .env

# Reload environment
docker-compose down
docker-compose up -d
```

## 🔒 Security Commands

### Generate New Keys
```bash
# Generate JWT secret
openssl rand -base64 64

# Generate encryption key (32 bytes for AES-256)
openssl rand -hex 32
```

### Check Rate Limits
```bash
# Trigger rate limit (run 6 times quickly)
for i in {1..6}; do
  curl -X POST http://localhost:3000/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username":"admin","password":"wrong"}'
done
```

## 📱 One-Liners

```bash
# Full restart
docker-compose down && docker-compose up -d && docker-compose logs -f

# Quick test
curl -s http://localhost:3000/health | jq .status

# Get token and list jobs
TOKEN=$(curl -s -X POST http://localhost:3000/api/auth/login -H "Content-Type: application/json" -d '{"username":"admin","password":"admin"}' | jq -r '.token') && curl -s http://localhost:3000/api/jobs -H "Authorization: Bearer $TOKEN" | jq

# Watch logs
watch -n 2 'docker-compose logs --tail=10 api'

# Check if all services running
docker-compose ps | grep Up | wc -l
```

## 🎯 Common Workflows

### Development Workflow
```bash
# 1. Make code changes
# 2. Rebuild and restart
docker-compose build api
docker-compose up -d api
docker-compose logs -f api

# 3. Test changes
curl http://localhost:3000/health
```

### Production Deployment
```bash
# 1. Pull latest code
git pull

# 2. Rebuild images
docker-compose build --no-cache

# 3. Stop old containers
docker-compose down

# 4. Start new containers
docker-compose up -d

# 5. Verify deployment
docker-compose ps
docker-compose logs --tail=50
```

### Troubleshooting Workflow
```bash
# 1. Check container status
docker-compose ps

# 2. View recent logs
docker-compose logs --tail=100

# 3. Check specific service
docker-compose logs api | grep -i error

# 4. Restart if needed
docker-compose restart api

# 5. Verify fix
curl http://localhost:3000/health
```

---

**Quick Reference**: Save this file for fast access to common commands!
