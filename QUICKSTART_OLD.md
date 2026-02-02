# Loggin Genie 🧞‍♂️ - Quick Start Guide

## Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd /Users/kalinka/Documents/Tools/loggin_genie
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   
   Or if you're using the virtual environment:
   ```bash
   source .venv/bin/activate  # On macOS/Linux
   pip install -r requirements.txt
   ```

## Configuration

### Option 1: Environment Variables (Recommended)

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your settings:
   ```bash
   ELASTICSEARCH_URL=https://your-elasticsearch.com:9200
   ELASTICSEARCH_USERNAME=your-username
   ELASTICSEARCH_PASSWORD=your-password
   ENCRYPTION_KEY=your-encryption-key
   ENCRYPTION_ALGORITHM=AES-256-CBC
   ```

### Option 2: Command Line Arguments

Pass all parameters directly via CLI (see usage examples below).

## Usage Examples

### 1. Basic Usage with Environment Variables

```bash
python loggin_genie.py --index "logs-*"
```

### 2. Fetch and Decrypt Specific Index

```bash
python loggin_genie.py \
  --elasticsearch-url "https://your-es.com:9200" \
  --index "app-logs-2024" \
  --key "your-encryption-key" \
  --username "elastic" \
  --password "your-password"
```

### 3. Filter by Query and Save to File

```bash
python loggin_genie.py \
  --index "logs-*" \
  --query '{"match": {"level": "error"}}' \
  --output decrypted_errors.json \
  --size 200
```

### 4. Decrypt Specific Field

```bash
python loggin_genie.py \
  --index "app-logs" \
  --field "encrypted_payload" \
  --algorithm "AES-256-GCM" \
  --output results.json
```

### 5. Display in Different Formats

```bash
# Table format (default)
python loggin_genie.py --index "logs-*" --format table

# JSON format
python loggin_genie.py --index "logs-*" --format json

# Plain text
python loggin_genie.py --index "logs-*" --format text
```

### 6. Using API Key Authentication

```bash
python loggin_genie.py \
  --elasticsearch-url "https://your-es.com:9200" \
  --api-key "your-api-key" \
  --index "logs-*"
```

## Advanced Queries

### Filter by Date Range

```bash
python loggin_genie.py \
  --index "logs-*" \
  --query '{
    "range": {
      "@timestamp": {
        "gte": "2024-01-01",
        "lte": "2024-01-31"
      }
    }
  }'
```

### Complex Boolean Query

```bash
python loggin_genie.py \
  --index "logs-*" \
  --query '{
    "bool": {
      "must": [
        {"match": {"level": "error"}},
        {"match": {"service": "auth"}}
      ],
      "filter": [
        {"range": {"@timestamp": {"gte": "now-24h"}}}
      ]
    }
  }'
```

## Encryption Key Formats

The tool accepts encryption keys in multiple formats:

1. **Hex string** (recommended):
   ```
   --key "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
   ```

2. **Base64 encoded**:
   ```
   --key "AQIDBAUGCQ0REQUJDQ0RFRUlNDQ0RF="
   ```

3. **Plain text** (will be hashed with SHA-256):
   ```
   --key "my-secret-key"
   ```

## Supported Encryption Algorithms

- `AES-256-CBC` (default)
- `AES-128-CBC`
- `AES-256-GCM`
- `AES-128-GCM`

## Testing

Run the test example to verify encryption/decryption:

```bash
python examples/test_decryption.py
```

## Troubleshooting

### Connection Issues

If you get SSL certificate errors:
```bash
# The tool disables SSL verification by default for development
# For production, ensure your certificates are properly configured
```

### Decryption Failures

1. Verify your encryption key is correct
2. Ensure the algorithm matches what your backend uses
3. Check that the encrypted data format matches (IV + ciphertext for CBC, IV + tag + ciphertext for GCM)

### No Logs Found

1. Verify the index name exists in Elasticsearch
2. Check your query syntax
3. Verify authentication credentials

## Getting Help

```bash
python loggin_genie.py --help
```

## Examples

Check the `examples/` directory for:
- `basic_usage.py` - Simple programmatic usage
- `advanced_queries.py` - Complex Elasticsearch queries
- `test_decryption.py` - Test encryption/decryption locally
