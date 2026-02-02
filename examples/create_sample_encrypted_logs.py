"""
Create sample encrypted logs for testing
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
from datetime import datetime, timedelta
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes
import base64
import hashlib


def get_key(password: str, key_size: int = 32) -> bytes:
    """Derive key from password"""
    return hashlib.sha256(password.encode()).digest()[:key_size]


def encrypt_aes_cbc(plaintext: str, key: bytes) -> str:
    """Encrypt with AES-CBC"""
    iv = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded = pad(plaintext.encode('utf-8'), AES.block_size)
    ciphertext = cipher.encrypt(padded)
    return base64.b64encode(iv + ciphertext).decode('utf-8')


def encrypt_aes_gcm(plaintext: str, key: bytes) -> str:
    """Encrypt with AES-GCM"""
    iv = get_random_bytes(12)
    cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode('utf-8'))
    return base64.b64encode(iv + tag + ciphertext).decode('utf-8')


def create_sample_logs():
    """Create sample encrypted log files"""
    
    password = "my-secret-encryption-key-32bytes"
    key = get_key(password)
    
    # Sample log messages
    log_messages = [
        "User authentication successful for user_id: 12345",
        "Database query executed in 45ms: SELECT * FROM users WHERE active=true",
        "API request received: POST /api/v1/orders with payload size 2.5KB",
        "Error: Connection timeout to service payment-processor after 30s",
        "Warning: High memory usage detected - 85% of available RAM",
        "Info: Background job completed successfully - processed 1500 records",
        "Debug: Cache miss for key 'user_session_abc123', fetching from database",
        "Critical: Failed to send notification email - SMTP server unreachable",
    ]
    
    levels = ["info", "warn", "error", "debug", "critical"]
    services = ["api", "database", "auth-service", "payment-processor", "notification-service"]
    
    # Generate AES-CBC encrypted logs
    cbc_logs = []
    base_time = datetime.now() - timedelta(hours=2)
    
    for i, message in enumerate(log_messages):
        encrypted_message = encrypt_aes_cbc(message, key)
        log = {
            "_id": str(i + 1),
            "_index": "app-logs-2024",
            "_source": {
                "@timestamp": (base_time + timedelta(minutes=i * 15)).isoformat() + "Z",
                "level": levels[i % len(levels)],
                "service": services[i % len(services)],
                "message": encrypted_message,
                "host": f"server-{(i % 3) + 1}",
                "environment": "production"
            }
        }
        cbc_logs.append(log)
    
    # Generate AES-GCM encrypted logs
    gcm_logs = []
    
    for i, message in enumerate(log_messages):
        encrypted_message = encrypt_aes_gcm(message, key)
        log = {
            "_id": str(i + 1),
            "_index": "app-logs-2024",
            "_source": {
                "@timestamp": (base_time + timedelta(minutes=i * 15)).isoformat() + "Z",
                "level": levels[i % len(levels)],
                "service": services[i % len(services)],
                "message": encrypted_message,
                "host": f"server-{(i % 3) + 1}",
                "environment": "production"
            }
        }
        gcm_logs.append(log)
    
    # Save to files
    output_dir = Path(__file__).parent
    
    with open(output_dir / "sample-encrypted-aes-cbc.json", "w") as f:
        json.dump(cbc_logs, f, indent=2)
    
    with open(output_dir / "sample-encrypted-aes-gcm.json", "w") as f:
        json.dump(gcm_logs, f, indent=2)
    
    print("✅ Sample encrypted log files created:")
    print(f"   - {output_dir / 'sample-encrypted-aes-cbc.json'}")
    print(f"   - {output_dir / 'sample-encrypted-aes-gcm.json'}")
    print()
    print("🔑 Encryption key (password): my-secret-encryption-key-32bytes")
    print()
    print("Test decryption with:")
    print(f"python loggin_genie.py --file examples/sample-encrypted-aes-cbc.json --key 'my-secret-encryption-key-32bytes' --algorithm AES-256-CBC")


if __name__ == '__main__':
    create_sample_logs()
