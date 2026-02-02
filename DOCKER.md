# Loggin Genie - Docker Deployment Guide 🐳

Complete guide for deploying Loggin Genie as a containerized web application.

## 📦 Architecture

```
┌─────────────────┐
│   Web UI        │
│   (Nginx:80)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   REST API      │
│  (Node.js:3000) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Python Worker  │
│  (Decryption)   │
└─────────────────┘
```

## 🚀 Quick Start

### 1. Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- 2GB RAM minimum
- 5GB disk space

### 2. Clone and Configure

```bash
cd /Users/kalinka/Documents/Tools/loggin_genie

# Copy environment file
cp .env.docker .env

# Edit with your settings
nano .env
```

### 3. Build and Run

```bash
# Build all containers
docker-compose build

# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### 4. Access the Application

- **Web UI**: http://localhost:8080
- **API**: http://localhost:3000
- **Health Check**: http://localhost:3000/health

## 📋 API Endpoints

### Health Check
```bash
curl http://localhost:3000/health
```

### Upload and Decrypt File
```bash
curl -X POST http://localhost:3000/api/decrypt/file \
  -F "logFile=@logs.json" \
  -F "encryptionKey=your-key" \
  -F "algorithm=AES-256-CBC" \
  -F "field=message"
```

### Decrypt from Kibana
```bash
curl -X POST http://localhost:3000/api/decrypt/kibana \
  -H "Content-Type: application/json" \
  -d '{
    "elasticsearchUrl": "https://your-es.com:9200",
    "index": "logs-*",
    "encryptionKey": "your-key",
    "algorithm": "AES-256-CBC",
    "username": "elastic",
    "password": "password",
    "size": 100
  }'
```

### Check Job Status
```bash
curl http://localhost:3000/api/jobs/{jobId}
```

### Get Job Result
```bash
curl http://localhost:3000/api/jobs/{jobId}/result
```

### Download Result
```bash
curl http://localhost:3000/api/jobs/{jobId}/download -O
```

### List All Jobs
```bash
curl http://localhost:3000/api/jobs
```

### Delete Job
```bash
curl -X DELETE http://localhost:3000/api/jobs/{jobId}
```

## 🔧 Configuration

### Environment Variables

Edit `.env` file:

```env
# Ports
API_PORT=3000
WEB_PORT=8080

# Encryption
ENCRYPTION_KEY=your-default-key
ENCRYPTION_ALGORITHM=AES-256-CBC

# Optional: Elasticsearch
ELASTICSEARCH_URL=https://your-es.com:9200
ELASTICSEARCH_USERNAME=elastic
ELASTICSEARCH_PASSWORD=changeme
```

### Custom Ports

```bash
# Use different ports
API_PORT=5000 WEB_PORT=9090 docker-compose up -d
```

## 🛠️ Development

### Run in Development Mode

```bash
# API with hot reload
cd api
npm install
npm run dev

# Python tool
cd ..
source .venv/bin/activate
python loggin_genie.py --help
```

### Build Individual Services

```bash
# Build Python worker only
docker build -f Dockerfile.python -t loggin-genie-python .

# Build API only
docker build -f Dockerfile.api -t loggin-genie-api .

# Build Web UI only
docker build -f Dockerfile.web -t loggin-genie-web .
```

## 📊 Monitoring

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f python-worker
docker-compose logs -f web
```

### Check Resource Usage

```bash
docker stats
```

### Health Checks

```bash
# API health
curl http://localhost:3000/health

# Container health
docker-compose ps
```

## 🔐 Security

### Production Checklist

- [ ] Change default encryption key
- [ ] Use HTTPS with SSL certificates
- [ ] Set strong passwords for Elasticsearch
- [ ] Limit API rate limiting
- [ ] Enable authentication
- [ ] Use secrets management
- [ ] Regular security updates

### Enable HTTPS

```bash
# Add SSL certificates to nginx config
# Update web/nginx.conf with SSL settings
```

## 🧪 Testing

### Test the CLI Tool

```bash
# Enter Python container
docker exec -it loggin-genie-python bash

# Run test
python examples/test_decryption.py
```

### Test the API

```bash
# Test file upload
curl -X POST http://localhost:3000/api/decrypt/file \
  -F "logFile=@examples/sample-logs.json" \
  -F "encryptionKey=test-key" \
  -F "algorithm=AES-256-CBC"

# Check response
{
  "jobId": "uuid-here",
  "status": "processing",
  "statusUrl": "/api/jobs/uuid-here"
}
```

## 📦 Production Deployment

### Docker Compose Production

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  api:
    restart: always
    environment:
      - NODE_ENV=production
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '1'
          memory: 1G
```

### Deploy to Cloud

#### AWS ECS
```bash
# Build and push to ECR
aws ecr get-login-password | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com
docker tag loggin-genie-api:latest <account>.dkr.ecr.us-east-1.amazonaws.com/loggin-genie-api:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/loggin-genie-api:latest
```

#### Kubernetes
```bash
# Create deployment
kubectl apply -f k8s/deployment.yaml
```

## 🔄 Backup & Restore

### Backup Jobs Data

```bash
# Backup output directory
docker cp loggin-genie-api:/app/output ./backup/output
docker cp loggin-genie-api:/app/uploads ./backup/uploads
```

### Restore

```bash
docker cp ./backup/output loggin-genie-api:/app/output
docker cp ./backup/uploads loggin-genie-api:/app/uploads
```

## 🐛 Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Change ports in .env
API_PORT=3001
WEB_PORT=8081
```

#### Container Won't Start
```bash
# Check logs
docker-compose logs api

# Rebuild
docker-compose build --no-cache api
```

#### Permission Errors
```bash
# Fix volume permissions
sudo chown -R $(whoami):$(whoami) uploads output
```

#### Out of Memory
```bash
# Increase Docker memory limit
# Docker Desktop > Settings > Resources > Memory
```

### Reset Everything

```bash
# Stop and remove containers
docker-compose down -v

# Remove images
docker rmi $(docker images 'loggin-genie*' -q)

# Clean up
rm -rf uploads output

# Rebuild
docker-compose up --build -d
```

## 📈 Scaling

### Horizontal Scaling

```bash
# Scale API workers
docker-compose up -d --scale api=3
```

### Load Balancing

```nginx
upstream api_backend {
    server api1:3000;
    server api2:3000;
    server api3:3000;
}
```

## 🔄 Updates

### Update Containers

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d
```

### Rolling Updates

```bash
# Update one service at a time
docker-compose up -d --no-deps --build api
```

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- [Node.js Best Practices](https://github.com/goldbergyoni/nodebestpractices)

## 💡 Tips

1. **Use volumes for persistent data**
2. **Monitor container health regularly**
3. **Set up log rotation**
4. **Use environment-specific configs**
5. **Implement rate limiting**
6. **Add authentication for production**

## 🆘 Support

For issues and questions:
- Check logs: `docker-compose logs -f`
- Review documentation
- Check GitHub issues
