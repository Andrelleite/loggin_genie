# Test Data Examples

This directory contains sample encrypted Kibana logs for testing the LogginGenie decryption tool.

## Files

### 1. **kibana_logs_large.json** (200 logs, ~90KB)
- **Format**: Elasticsearch JSON array
- **Entries**: 200 encrypted log entries
- **Services**: 8 different microservices
- **Time Range**: 24-hour period
- **Use Case**: Testing bulk decryption and UI performance

**Log Level Distribution:**
- INFO: 124 entries (62%)
- WARN: 38 entries (19%)
- ERROR: 32 entries (16%)
- DEBUG: 6 entries (3%)

**Services Included:**
1. `user-service` - User authentication and profile management
2. `auth-service` - JWT tokens, OAuth, permissions
3. `payment-service` - Payments, refunds, subscriptions
4. `notification-service` - Email, SMS, push notifications
5. `analytics-service` - Event tracking, metrics, A/B tests
6. `inventory-service` - Stock management, warehouse operations
7. `order-service` - Order lifecycle management
8. `search-service` - Search queries, indexing, autocomplete

### 2. **kibana_logs_large_stream.ndjson** (200 logs, ~75KB)
- **Format**: Newline-delimited JSON (NDJSON)
- **Same data as above**, optimized for streaming
- **Use Case**: Testing Kibana stream decryption

### 3. **kibana_logs_elasticsearch.json** (50 logs)
- **Format**: Elasticsearch JSON array
- **Entries**: 50 encrypted log entries
- **Use Case**: Quick testing and debugging

### 4. **kibana_logs_stream.ndjson** (50 logs)
- **Format**: Newline-delimited JSON
- **Same data as #3**, in NDJSON format

### 5. **encryption_key.txt**
- **Encryption Key**: `04c8ec0929fb619f3da9151d542ef41591044245bebb0cb22f9704645a99e948`
- **Algorithm**: AES-256-CBC
- **Use Case**: Upload this file or paste the key when decrypting

## Usage

### Via Web UI (http://localhost:8080)

1. **Upload the encryption key**:
   - Either upload `encryption_key.txt` as a file
   - Or paste the key directly: `04c8ec0929fb619f3da9151d542ef41591044245bebb0cb22f9704645a99e048`

2. **Upload logs**:
   - Choose either `kibana_logs_large.json` or `kibana_logs_large_stream.ndjson`
   - Set encrypted field name to: `message`

3. **Decrypt**:
   - Click "🔓 Decrypt & View" to see results in the browser
   - Click "💾 Decrypt & Download" to save decrypted logs

### Via Command Line

```bash
# Decrypt the large test file
python3 loggin_genie.py \
  --input examples/kibana_logs_large.json \
  --key 04c8ec0929fb619f3da9151d542ef41591044245bebb0cb22f9704645a99e948 \
  --field message \
  --output decrypted_output.json

# View decrypted results
cat decrypted_output.json | jq '.[0]._source | {timestamp, level, service, decrypted_message}'
```

## Sample Decrypted Messages

Here are examples of what you'll see after decryption:

**User Service:**
- "User login successful for user alice"
- "Password reset requested for user bob"
- "Email verification sent to charlie@example.com"

**Payment Service:**
- "Payment processed successfully for order ORD-1045 - Amount: $234.50"
- "Refund initiated for transaction TXN-2089"
- "Credit card added for customer diana"

**Search Service:**
- "Search query executed: \"wireless headphones\" - 287 results found"
- "Zero results query logged: \"gaming mouse\""
- "Search performance: query \"laptop deals\" took 145ms"

**Analytics Service:**
- "Event tracked: add_to_cart for user george"
- "Conversion funnel step 3 completed by user helen"
- "A/B test variant B assigned to user ivan"

## Regenerating Test Data

To create new test data with different content:

```bash
# Edit generate_large_test.py if you want to customize
python3 generate_large_test.py

# This will create:
# - examples/kibana_logs_large.json (200 entries)
```

Then create the NDJSON version:
```bash
python3 -c "import json; logs=json.load(open('examples/kibana_logs_large.json')); \
[print(json.dumps(log)) for log in logs]" > examples/kibana_logs_large_stream.ndjson
```

## Notes

- All messages are encrypted with AES-256-CBC
- Timestamps are sorted chronologically across a 24-hour period
- Log levels follow realistic distribution (INFO most common, DEBUG rare)
- Each log includes metadata: host, environment, request_id, optional duration_ms
- Services and messages represent real-world microservice scenarios
