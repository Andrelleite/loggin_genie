#!/usr/bin/env python3
"""Test decryption of a single log entry"""

import json
from src.decryptor import LogDecryptor

# Test key
key = "04c8ec0929fb619f3da9151d542ef41591044245bebb0cb22f9704645a99e948"

# Read first log from the test file
with open('examples/kibana_logs_large.json', 'r') as f:
    logs = json.load(f)
    first_log = logs[0]

print("Original log:")
print(json.dumps(first_log, indent=2))
print("\n" + "="*80 + "\n")

# Get the encrypted message
source = first_log['_source']
encrypted_msg = source.get('message', '')

print(f"Encrypted message: {encrypted_msg}")
print("\n" + "="*80 + "\n")

# Decrypt
decryptor = LogDecryptor(key=key, algorithm='AES-256-CBC')

try:
    # Split IV and ciphertext
    if ':' in encrypted_msg:
        import base64
        iv_b64, ciphertext_b64 = encrypted_msg.split(':', 1)
        # Combine IV and ciphertext
        encrypted_bytes = base64.b64decode(iv_b64) + base64.b64decode(ciphertext_b64)
        # Re-encode as single base64 string
        encrypted_data = base64.b64encode(encrypted_bytes).decode('utf-8')
    else:
        encrypted_data = encrypted_msg
    
    decrypted = decryptor.decrypt(encrypted_data)
    print(f"Decrypted message: {decrypted}")
    
    # Add to source like the main script does
    source['encrypted_message'] = encrypted_msg
    source['decrypted_message'] = decrypted
    
    print("\n" + "="*80 + "\n")
    print("Updated log with decrypted field:")
    print(json.dumps(first_log, indent=2))
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
