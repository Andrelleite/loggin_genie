# Loggin Genie 🧞‍♂️

## Project Overview

**Loggin Genie** is a Python tool designed to fetch and decrypt encrypted event logs from Kibana/Elasticsearch. It's perfect for scenarios where your backend encrypts log data before storing it in Elasticsearch, and you need a convenient way to decrypt and analyze those logs.

## ✨ Features

- 🔌 **Easy Kibana/Elasticsearch Integration** - Connect using basic auth or API keys
- 🔐 **Multiple Encryption Algorithms** - Supports AES-256-CBC, AES-128-CBC, AES-256-GCM, AES-128-GCM
- 🔍 **Flexible Querying** - Use Elasticsearch Query DSL to filter logs
- 📊 **Multiple Output Formats** - Display as table, JSON, or plain text
- 💾 **Export Capabilities** - Save decrypted logs to JSON or text files
- 🎨 **Beautiful CLI** - Rich terminal interface with colored output
- 🛠️ **Programmatic API** - Use as a library in your Python projects

## 📁 Project Structure

```
loggin_genie/
├── loggin_genie.py          # Main CLI application
├── requirements.txt          # Python dependencies
├── setup.py                  # Package setup
├── README.md                 # This file
├── QUICKSTART.md            # Quick start guide
├── .env.example             # Environment variables template
├── .gitignore               # Git ignore patterns
├── src/
│   ├── __init__.py          # Package initialization
│   ├── kibana_client.py     # Elasticsearch/Kibana client
│   ├── decryptor.py         # Encryption/decryption logic
│   └── formatter.py         # Output formatting
└── examples/
    ├── basic_usage.py       # Simple usage example
    ├── advanced_queries.py  # Advanced Elasticsearch queries
    └── test_decryption.py   # Test encryption/decryption
```

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- Access to Kibana/Elasticsearch instance
- Encryption key used by your backend

### Install Dependencies

```bash
# Clone or navigate to the project
cd /Users/kalinka/Documents/Tools/loggin_genie

# Install required packages
pip install -r requirements.txt

# Or install in development mode
pip install -e .
```

## ⚙️ Configuration

### Method 1: Environment Variables (Recommended)

Create a `.env` file:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
ELASTICSEARCH_URL=https://your-elasticsearch.com:9200
ELASTICSEARCH_USERNAME=your-username
ELASTICSEARCH_PASSWORD=your-password
ENCRYPTION_KEY=your-encryption-key
ENCRYPTION_ALGORITHM=AES-256-CBC
```

### Method 2: Command Line Arguments

Pass parameters directly via CLI (see usage examples below).

## 📖 Usage

### Basic Command

```bash
python loggin_genie.py --index "logs-*"
```

### Common Use Cases

#### 1. Fetch and decrypt error logs

```bash
python loggin_genie.py \
  --index "app-logs-*" \
  --query '{"match": {"level": "error"}}' \
  --size 50
```

#### 2. Decrypt logs from last 24 hours

```bash
python loggin_genie.py \
  --index "logs-*" \
  --query '{"range": {"@timestamp": {"gte": "now-24h"}}}' \
  --output last_24h.json
```

#### 3. Decrypt specific encrypted field

```bash
python loggin_genie.py \
  --index "secure-logs" \
  --field "encrypted_payload" \
  --algorithm "AES-256-GCM"
```

#### 4. Export to file

```bash
python loggin_genie.py \
  --index "logs-*" \
  --output decrypted_logs.json \
  --format json
```

## 🔐 Encryption Support

### Supported Algorithms

- **AES-256-CBC** (default) - Most common
- **AES-128-CBC** - Lighter encryption
- **AES-256-GCM** - Authenticated encryption
- **AES-128-GCM** - Lighter authenticated encryption

### Key Formats

The tool accepts keys in multiple formats:

1. **Hexadecimal** (64 chars for AES-256, 32 for AES-128):
   ```
   0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
   ```

2. **Base64 encoded**:
   ```
   AQIDBAUGCQ0REQUJDQ0RFRUlNDQ0RF==
   ```

3. **Plain text** (will be hashed using SHA-256):
   ```
   my-secret-key
   ```

### Expected Data Format

#### AES-CBC Mode
```
Base64(IV (16 bytes) + Ciphertext)
```

#### AES-GCM Mode
```
Base64(IV (12 bytes) + Tag (16 bytes) + Ciphertext)
```

## 🔌 Programmatic Usage

You can use Loggin Genie as a library in your Python code:

```python
from src.kibana_client import KibanaClient
from src.decryptor import LogDecryptor
from src.formatter import LogFormatter

# Connect to Elasticsearch
client = KibanaClient(
    elasticsearch_url="https://your-es.com:9200",
    username="elastic",
    password="password"
)

# Fetch logs
logs = client.fetch_logs(
    index="app-logs-*",
    query={"match": {"level": "error"}},
    size=100
)

# Decrypt logs
decryptor = LogDecryptor(
    key="your-encryption-key",
    algorithm="AES-256-CBC"
)

for log in logs:
    encrypted_msg = log['_source']['message']
    decrypted_msg = decryptor.decrypt(encrypted_msg)
    log['_source']['message'] = decrypted_msg

# Format and display
formatter = LogFormatter()
formatter.print_table(logs)
```

## 📝 Examples

Check the `examples/` directory:

- **`basic_usage.py`** - Simple programmatic usage
- **`advanced_queries.py`** - Complex Elasticsearch queries
- **`test_decryption.py`** - Test encryption/decryption locally

Run an example:

```bash
python examples/test_decryption.py
```

## 🛠️ CLI Options

```
Options:
  --kibana-url TEXT           Kibana URL (or use KIBANA_URL env var)
  --elasticsearch-url TEXT    Elasticsearch URL (or use ELASTICSEARCH_URL)
  --index TEXT                Elasticsearch index name [required]
  --key TEXT                  Encryption key [required]
  --algorithm TEXT            Encryption algorithm (default: AES-256-CBC)
  --field TEXT                Field containing encrypted data (default: message)
  --query TEXT                Elasticsearch query in JSON format
  --size INTEGER              Number of logs to fetch (default: 100)
  --output PATH               Output file path
  --format [json|text|table]  Output format (default: table)
  --username TEXT             Elasticsearch username
  --password TEXT             Elasticsearch password
  --api-key TEXT              Elasticsearch API key
  --help                      Show help message
```

## 🔍 Advanced Queries

### Filter by Multiple Conditions

```bash
python loggin_genie.py --index "logs-*" --query '{
  "bool": {
    "must": [
      {"match": {"level": "error"}},
      {"match": {"service": "auth"}}
    ]
  }
}'
```

### Date Range Query

```bash
python loggin_genie.py --index "logs-*" --query '{
  "range": {
    "@timestamp": {
      "gte": "2024-01-01",
      "lte": "2024-01-31"
    }
  }
}'
```

### Search with Keywords

```bash
python loggin_genie.py --index "logs-*" --query '{
  "bool": {
    "should": [
      {"match": {"message": "failed"}},
      {"match": {"message": "timeout"}}
    ],
    "minimum_should_match": 1
  }
}'
```

## 🐛 Troubleshooting

### Connection Issues

**Error**: `Failed to connect to Elasticsearch`

**Solution**: 
- Verify the URL is correct
- Check network connectivity
- Verify credentials

### Decryption Failures

**Error**: `Decryption failed: ...`

**Solutions**:
- Verify encryption key is correct
- Ensure algorithm matches backend encryption
- Check encrypted data format (IV + ciphertext)

### No Logs Found

**Solutions**:
- Verify index name exists
- Check query syntax
- Verify time range in query

### Import Errors

If running examples fails with `ModuleNotFoundError: No module named 'src'`:

```bash
# Run from project root or use full path
cd /Users/kalinka/Documents/Tools/loggin_genie
python examples/test_decryption.py
```

## 🧪 Testing

Run the test suite:

```bash
# Test encryption/decryption
python examples/test_decryption.py

# View CLI help
python loggin_genie.py --help
```

## 📦 Dependencies

- **elasticsearch** - Elasticsearch Python client
- **cryptography** - Modern cryptography library
- **pycryptodome** - AES encryption support
- **click** - CLI framework
- **python-dotenv** - Environment variable management
- **rich** - Beautiful terminal output
- **requests** - HTTP library
- **python-dateutil** - Date parsing

## 🤝 Contributing

Contributions are welcome! Feel free to:

1. Report bugs
2. Suggest features
3. Submit pull requests

## 📄 License

MIT License - feel free to use this tool in your projects!

## 🙏 Acknowledgments

Built with love for developers dealing with encrypted logs.

---

**Happy Log Decrypting! 🧞‍♂️✨**
