# Loggin Genie - Command Cheatsheet 🧞‍♂️

## Quick Start

```bash
# Using the convenience script
./run.sh --index "logs-*"

# Or directly
python loggin_genie.py --index "logs-*"
```

## Authentication

### Basic Auth
```bash
python loggin_genie.py \
  --elasticsearch-url "https://es.example.com:9200" \
  --username "elastic" \
  --password "changeme" \
  --index "logs-*"
```

### API Key
```bash
python loggin_genie.py \
  --elasticsearch-url "https://es.example.com:9200" \
  --api-key "your-api-key" \
  --index "logs-*"
```

### Environment Variables
```bash
# Set in .env file
ELASTICSEARCH_URL=https://es.example.com:9200
ELASTICSEARCH_USERNAME=elastic
ELASTICSEARCH_PASSWORD=changeme
ENCRYPTION_KEY=your-key

# Then run
python loggin_genie.py --index "logs-*"
```

## Common Queries

### Get Last N Logs
```bash
python loggin_genie.py --index "logs-*" --size 50
```

### Filter by Log Level
```bash
# Error logs only
python loggin_genie.py --index "logs-*" \
  --query '{"match": {"level": "error"}}'

# Warning or Error
python loggin_genie.py --index "logs-*" \
  --query '{"bool": {"should": [{"match": {"level": "error"}}, {"match": {"level": "warn"}}]}}'
```

### Date Range
```bash
# Last 24 hours
python loggin_genie.py --index "logs-*" \
  --query '{"range": {"@timestamp": {"gte": "now-24h"}}}'

# Last 7 days
python loggin_genie.py --index "logs-*" \
  --query '{"range": {"@timestamp": {"gte": "now-7d"}}}'

# Specific date range
python loggin_genie.py --index "logs-*" \
  --query '{"range": {"@timestamp": {"gte": "2024-01-01", "lte": "2024-01-31"}}}'
```

### Filter by Service/Application
```bash
python loggin_genie.py --index "logs-*" \
  --query '{"match": {"service": "auth-service"}}'
```

### Search by Keyword
```bash
python loggin_genie.py --index "logs-*" \
  --query '{"match": {"message": "timeout"}}'
```

### Complex Boolean Query
```bash
python loggin_genie.py --index "logs-*" \
  --query '{
    "bool": {
      "must": [
        {"match": {"level": "error"}},
        {"match": {"service": "payment"}}
      ],
      "filter": [
        {"range": {"@timestamp": {"gte": "now-24h"}}}
      ]
    }
  }'
```

## Output Formats

### Table (Default)
```bash
python loggin_genie.py --index "logs-*" --format table
```

### JSON
```bash
python loggin_genie.py --index "logs-*" --format json
```

### Plain Text
```bash
python loggin_genie.py --index "logs-*" --format text
```

## Save to File

### JSON Format
```bash
python loggin_genie.py --index "logs-*" \
  --output decrypted_logs.json
```

### Text Format
```bash
python loggin_genie.py --index "logs-*" \
  --output decrypted_logs.txt \
  --format text
```

## Encryption Options

### Different Algorithm
```bash
# AES-256-GCM
python loggin_genie.py --index "logs-*" \
  --algorithm "AES-256-GCM"

# AES-128-CBC
python loggin_genie.py --index "logs-*" \
  --algorithm "AES-128-CBC"
```

### Different Field
```bash
# If encrypted data is in field other than 'message'
python loggin_genie.py --index "logs-*" \
  --field "encrypted_payload"
```

### Key Formats
```bash
# Hex key (64 chars for AES-256)
python loggin_genie.py --index "logs-*" \
  --key "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"

# Base64 key
python loggin_genie.py --index "logs-*" \
  --key "AQIDBAUGCQ0REQUJDQ0RFRUlNDQ0RF=="

# Plain text (will be hashed)
python loggin_genie.py --index "logs-*" \
  --key "my-secret-key"
```

## Production Examples

### Decrypt Production Error Logs
```bash
python loggin_genie.py \
  --elasticsearch-url "$PROD_ES_URL" \
  --username "$PROD_USERNAME" \
  --password "$PROD_PASSWORD" \
  --index "production-logs-*" \
  --key "$PROD_ENCRYPTION_KEY" \
  --query '{"bool": {"must": [{"match": {"level": "error"}}, {"range": {"@timestamp": {"gte": "now-1h"}}}]}}' \
  --output prod_errors.json
```

### Decrypt Specific Service Logs
```bash
python loggin_genie.py \
  --index "app-logs-2024-*" \
  --query '{"match": {"service": "payment-processor"}}' \
  --field "encrypted_message" \
  --size 200 \
  --output payment_logs.json
```

### Audit Trail
```bash
python loggin_genie.py \
  --index "audit-logs" \
  --query '{"bool": {"must": [{"match": {"action": "login"}}, {"match": {"status": "failed"}}]}}' \
  --size 500 \
  --output failed_logins.json
```

## Pipe to Other Tools

### Pipe to jq
```bash
python loggin_genie.py --index "logs-*" --format json | jq '.[] | ._source.message'
```

### Pipe to grep
```bash
python loggin_genie.py --index "logs-*" --format text | grep "ERROR"
```

### Count occurrences
```bash
python loggin_genie.py --index "logs-*" --format text | grep -c "timeout"
```

## Testing

### Test Decryption Locally
```bash
python examples/test_decryption.py
```

### Test with Sample Data
```bash
# Run basic usage example
python examples/basic_usage.py
```

### View Help
```bash
python loggin_genie.py --help
```

## Troubleshooting Commands

### Check Connection
```bash
# Try to fetch logs without decryption
curl -u elastic:password "https://es.example.com:9200/logs-*/_search?size=1"
```

### Verify Index Exists
```bash
curl -u elastic:password "https://es.example.com:9200/_cat/indices?v"
```

### Test Encryption Key
```bash
# Use the test script
python examples/test_decryption.py
```

## Performance Tips

### Large Result Sets
```bash
# Use smaller size and multiple queries
python loggin_genie.py --index "logs-*" --size 100

# Or use scroll for very large sets (programmatic API)
```

### Specific Indices
```bash
# Instead of wildcard, use specific index
python loggin_genie.py --index "logs-2024-02-02"
```

### Filter Early
```bash
# Add time range to reduce data
python loggin_genie.py --index "logs-*" \
  --query '{"range": {"@timestamp": {"gte": "now-1h"}}}' \
  --size 1000
```

## Environment Variables Reference

```bash
# .env file
ELASTICSEARCH_URL=https://es.example.com:9200
KIBANA_URL=https://kibana.example.com
ELASTICSEARCH_USERNAME=elastic
ELASTICSEARCH_PASSWORD=changeme
ELASTICSEARCH_API_KEY=your-api-key
ENCRYPTION_KEY=your-encryption-key
ENCRYPTION_ALGORITHM=AES-256-CBC
DEFAULT_INDEX=logs-*
DEFAULT_SIZE=100
```

## Aliases (Add to ~/.zshrc or ~/.bashrc)

```bash
# Quick decrypt
alias logdecrypt='python /path/to/loggin_genie/loggin_genie.py'

# Decrypt errors
alias decrypt-errors='logdecrypt --query "{\"match\": {\"level\": \"error\"}}"'

# Decrypt last hour
alias decrypt-1h='logdecrypt --query "{\"range\": {\"@timestamp\": {\"gte\": \"now-1h\"}}}"'
```

---

For more detailed documentation, see:
- `README.md` - Project overview
- `QUICKSTART.md` - Getting started guide
- `DOCUMENTATION.md` - Comprehensive documentation
