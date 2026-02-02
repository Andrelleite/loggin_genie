#!/usr/bin/env python3
"""
Generate a sample encrypted log using the production key for testing
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes
import base64

# Use the production key
PRODUCTION_KEY = bytes.fromhex('04c8ec0929fb619f3da9151d542ef41591044245bebb0cb22f9704645a99e948')


def encrypt_message(plaintext: str, key: bytes) -> str:
    """Encrypt with AES-256-CBC"""
    iv = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded = pad(plaintext.encode('utf-8'), AES.block_size)
    ciphertext = cipher.encrypt(padded)
    return base64.b64encode(iv + ciphertext).decode('utf-8')


def main():
    """Create a test log with production key"""
    
    message = "PRODUCTION TEST: User login successful - user_id: admin@company.com"
    encrypted = encrypt_message(message, PRODUCTION_KEY)
    
    log_entry = {
        "_id": "test-1",
        "_index": "production-logs",
        "_source": {
            "@timestamp": datetime.now().isoformat() + "Z",
            "level": "info",
            "service": "auth-service",
            "message": encrypted,
            "environment": "production"
        }
    }
    
    output_file = Path(__file__).parent / "test-production-key.json"
    
    with open(output_file, 'w') as f:
        json.dump([log_entry], f, indent=2)
    
    print("✅ Test log created with production key!")
    print(f"   File: {output_file}")
    print()
    print("🔓 Test decryption:")
    print(f"   python loggin_genie.py --file examples/test-production-key.json")
    print()
    print(f"Original message: {message}")
    print(f"Encrypted: {encrypted[:50]}...")


if __name__ == '__main__':
    main()
