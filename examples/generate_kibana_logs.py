#!/usr/bin/env python3
"""
Generate realistic dummy log files as they would appear from Kibana/Elasticsearch
with encrypted fields, simulating production logs.
"""

import json
import base64
import os
from datetime import datetime, timedelta
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad

# Use production key from .env
ENCRYPTION_KEY = bytes.fromhex('04c8ec0929fb619f3da9151d542ef41591044245bebb0cb22f9704645a99e948')

def encrypt_aes_256_cbc(plaintext: str, key: bytes) -> str:
    """Encrypt using AES-256-CBC"""
    iv = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_data = pad(plaintext.encode('utf-8'), AES.block_size)
    ciphertext = cipher.encrypt(padded_data)
    return base64.b64encode(iv + ciphertext).decode('utf-8')

# Realistic log messages
LOG_TEMPLATES = [
    {
        "level": "INFO",
        "messages": [
            "User logged in successfully - user_id: {user}, ip: {ip}",
            "API request processed - endpoint: /api/users/{user}, method: GET, status: 200",
            "Database query executed - table: users, duration: {duration}ms",
            "Cache hit - key: user_session_{user}, ttl: 3600s",
            "File uploaded successfully - filename: {filename}, size: {size}KB",
        ]
    },
    {
        "level": "WARN",
        "messages": [
            "Rate limit approaching - user: {user}, requests: 85/100 in 15min",
            "Slow query detected - duration: {duration}ms, threshold: 1000ms",
            "Memory usage high - current: 85%, threshold: 80%",
            "Failed login attempt - user: {user}, ip: {ip}, reason: invalid_password",
            "API deprecated endpoint accessed - endpoint: /api/v1/old_endpoint",
        ]
    },
    {
        "level": "ERROR",
        "messages": [
            "Database connection failed - host: db-prod-01, error: connection_timeout",
            "Payment processing failed - transaction_id: TXN-{txn}, error: {error}",
            "External API call failed - service: auth_service, status: 503",
            "File processing error - file: {filename}, error: invalid_format",
            "Session validation failed - session_id: {session}, error: token_expired",
        ]
    },
    {
        "level": "DEBUG",
        "messages": [
            "Request headers - user_agent: Mozilla/5.0, accept: application/json",
            "SQL query - SELECT * FROM users WHERE email = '{user}@company.com'",
            "Cache miss - key: product_{product_id}, fetching from database",
            "Environment variable loaded - NODE_ENV: production",
            "Middleware executed - name: authentication_middleware, duration: {duration}ms",
        ]
    }
]

# Sample data for templating
USERS = ["john.doe", "jane.smith", "admin", "alice.wang", "bob.jones", "charlie.brown"]
IPS = ["192.168.1.100", "10.0.0.50", "172.16.0.10", "203.0.113.42", "198.51.100.7"]
FILENAMES = ["report_2026.pdf", "invoice_12345.xlsx", "user_data.csv", "backup.zip", "config.json"]
ERRORS = ["insufficient_funds", "network_error", "invalid_card", "timeout", "validation_failed"]
SERVICES = ["user-service", "auth-service", "payment-service", "notification-service", "analytics-service"]

def generate_kibana_logs(count=50, filename="kibana_logs_sample.json"):
    """Generate realistic Kibana/Elasticsearch formatted logs"""
    logs = []
    base_time = datetime.now() - timedelta(hours=2)
    
    for i in range(count):
        # Select random log template
        import random
        log_category = random.choice(LOG_TEMPLATES)
        message_template = random.choice(log_category["messages"])
        
        # Fill in template variables
        message = message_template.format(
            user=random.choice(USERS),
            ip=random.choice(IPS),
            duration=random.randint(50, 2000),
            filename=random.choice(FILENAMES),
            size=random.randint(100, 50000),
            txn=f"{random.randint(10000, 99999)}",
            error=random.choice(ERRORS),
            session=f"sess_{random.randint(100000, 999999)}",
            product_id=random.randint(1000, 9999)
        )
        
        # Encrypt the message
        encrypted_message = encrypt_aes_256_cbc(message, ENCRYPTION_KEY)
        
        # Create Elasticsearch/Kibana format document
        timestamp = base_time + timedelta(seconds=i * 60)
        log_entry = {
            "_index": "application-logs-2026.02.02",
            "_type": "_doc",
            "_id": f"log_{i+1:04d}",
            "_score": 1.0,
            "_source": {
                "@timestamp": timestamp.isoformat() + "Z",
                "level": log_category["level"],
                "service": random.choice(SERVICES),
                "host": f"app-server-{random.randint(1, 5)}",
                "environment": "production",
                "encrypted_message": encrypted_message,
                "message_length": len(message),
                "correlation_id": f"corr-{random.randint(100000, 999999)}",
                "tags": ["encrypted", "sensitive", log_category["level"].lower()],
                "version": "1.0",
                "pid": random.randint(1000, 9999)
            }
        }
        logs.append(log_entry)
    
    # Save as Kibana export format
    with open(filename, 'w') as f:
        json.dump(logs, f, indent=2)
    
    print(f"✅ Generated {count} Kibana-formatted logs")
    print(f"   File: {filename}")
    print(f"   Format: Elasticsearch JSON with _index, _type, _id, _source")
    print(f"\n📋 Log distribution:")
    for category in LOG_TEMPLATES:
        level_count = sum(1 for log in logs if log["_source"]["level"] == category["level"])
        print(f"   {category['level']}: {level_count} logs")
    
    # Show sample
    print(f"\n📝 Sample encrypted message:")
    print(f"   Original: {message}")
    print(f"   Encrypted: {encrypted_message[:80]}...")
    
    return filename

def generate_ndjson_logs(count=50, filename="kibana_logs_sample.ndjson"):
    """Generate NDJSON format (newline-delimited JSON) - another common Kibana export format"""
    import random
    base_time = datetime.now() - timedelta(hours=2)
    
    with open(filename, 'w') as f:
        for i in range(count):
            log_category = random.choice(LOG_TEMPLATES)
            message_template = random.choice(log_category["messages"])
            
            message = message_template.format(
                user=random.choice(USERS),
                ip=random.choice(IPS),
                duration=random.randint(50, 2000),
                filename=random.choice(FILENAMES),
                size=random.randint(100, 50000),
                txn=f"{random.randint(10000, 99999)}",
                error=random.choice(ERRORS),
                session=f"sess_{random.randint(100000, 999999)}",
                product_id=random.randint(1000, 9999)
            )
            
            encrypted_message = encrypt_aes_256_cbc(message, ENCRYPTION_KEY)
            timestamp = base_time + timedelta(seconds=i * 60)
            
            log_entry = {
                "@timestamp": timestamp.isoformat() + "Z",
                "level": log_category["level"],
                "service": random.choice(SERVICES),
                "host": f"app-server-{random.randint(1, 5)}",
                "environment": "production",
                "encrypted_message": encrypted_message,
                "correlation_id": f"corr-{random.randint(100000, 999999)}",
                "tags": ["encrypted", "sensitive"]
            }
            
            # Write as NDJSON (one JSON object per line)
            f.write(json.dumps(log_entry) + '\n')
    
    print(f"\n✅ Generated {count} logs in NDJSON format")
    print(f"   File: {filename}")
    print(f"   Format: Newline-delimited JSON (NDJSON)")
    
    return filename

if __name__ == "__main__":
    print("🧞‍♂️ Generating realistic Kibana/Elasticsearch log samples...\n")
    
    # Generate both formats
    json_file = generate_kibana_logs(50, "examples/kibana_logs_elasticsearch.json")
    ndjson_file = generate_ndjson_logs(50, "examples/kibana_logs_stream.ndjson")
    
    print(f"\n🎉 Done! You can now test with these files:")
    print(f"   python loggin_genie.py --file {json_file}")
    print(f"   python loggin_genie.py --file {ndjson_file}")
    print(f"\n💡 Or upload via web UI at http://localhost:8080")
