# Loggin Genie 🧞‍♂️

A Python tool for fetching and decrypting encrypted event logs from Kibana/Elasticsearch.

## Features

- 🔐 **Secure Authentication**: JWT-based login system with bcrypt password hashing
- 🌐 **Web Interface**: Beautiful, responsive web UI with real-time job tracking
- 📦 **REST API**: Full-featured API for programmatic access
- 🐳 **Docker Support**: Complete containerized deployment with docker-compose
- 🔑 **Multiple Encryption Algorithms**: AES-256-CBC, AES-128-CBC, AES-256-GCM, AES-128-GCM
- 📁 **File Input**: Read logs from JSON/NDJSON files
- 🔍 **Kibana Integration**: Direct connection to Kibana/Elasticsearch
- 📤 **Export Options**: JSON or text format output
- 🎨 **Colorful CLI**: Rich terminal output with tables and colors
- ⚡ **Background Jobs**: Async job processing with status tracking

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Create a `.env` file or pass parameters via CLI:

```
KIBANA_URL=https://your-kibana-instance.com
ELASTICSEARCH_URL=https://your-elasticsearch-instance.com
ENCRYPTION_KEY=your-encryption-key-here
ENCRYPTION_ALGORITHM=AES-256-CBC
```

## Usage

### Basic Usage

```bash
python loggin_genie.py --kibana-url "https://your-kibana.com" \
                       --index "your-log-index" \
                       --key "your-encryption-key"
```

### With Query

```bash
python loggin_genie.py --kibana-url "https://your-kibana.com" \
                       --index "your-log-index" \
                       --key "your-encryption-key" \
                       --query '{"match": {"level": "error"}}' \
                       --output decrypted_logs.json
```

### Using Environment Variables

```bash
python loggin_genie.py --index "your-log-index" --output logs.json
```

## Supported Encryption Algorithms

- AES-256-CBC
- AES-128-CBC
- AES-256-GCM
- AES-128-GCM

## Authentication

The web interface and API are protected with JWT-based authentication.

**Default Credentials**:
- Username: `admin`
- Password: `admin`

⚠️ **Change these immediately in production!**

For detailed authentication documentation, see:
- [Authentication Guide](docs/AUTHENTICATION.md) - Complete authentication documentation
- [Authentication Quick Start](docs/AUTHENTICATION_QUICKSTART.md) - Quick setup guide

## Requirements

- Python 3.11+
- Node.js 18+ (for web interface)
- Docker & Docker Compose (optional, for containerized deployment)
- Access to Kibana/Elasticsearch instance (optional)
- Encryption key used by your backend

## License

MIT
