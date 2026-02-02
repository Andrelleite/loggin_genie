"""
Example: Testing decryption with sample encrypted data
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes
from src.decryptor import LogDecryptor
import json


def encrypt_sample_data(plaintext: str, key: bytes, algorithm: str = 'AES-256-CBC') -> str:
    """
    Encrypt sample data for testing
    
    Args:
        plaintext: Data to encrypt
        key: Encryption key (32 bytes for AES-256)
        algorithm: Encryption algorithm
    
    Returns:
        Base64 encoded encrypted data
    """
    
    if 'CBC' in algorithm:
        # Generate random IV
        iv = get_random_bytes(16)
        
        # Create cipher
        cipher = AES.new(key, AES.MODE_CBC, iv)
        
        # Encrypt with padding
        padded_data = pad(plaintext.encode('utf-8'), AES.block_size)
        ciphertext = cipher.encrypt(padded_data)
        
        # Combine IV + ciphertext
        encrypted = iv + ciphertext
        
        # Encode as base64
        return base64.b64encode(encrypted).decode('utf-8')
    
    elif 'GCM' in algorithm:
        # Generate random IV
        iv = get_random_bytes(12)
        
        # Create cipher
        cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
        
        # Encrypt
        ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode('utf-8'))
        
        # Combine IV + tag + ciphertext
        encrypted = iv + tag + ciphertext
        
        # Encode as base64
        return base64.b64encode(encrypted).decode('utf-8')
    
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")


def main():
    # Generate a sample encryption key (32 bytes for AES-256)
    key = get_random_bytes(32)
    key_hex = key.hex()
    
    print("=== Encryption/Decryption Test ===\n")
    print(f"Generated Key (hex): {key_hex}\n")
    
    # Sample log messages
    sample_logs = [
        "User login successful: user_id=12345",
        "Database connection failed: timeout after 30s",
        '{"event": "payment_processed", "amount": 99.99, "currency": "USD"}',
        "Error: Null pointer exception in module auth.service.ts line 42"
    ]
    
    # Test with AES-256-CBC
    print("=== Testing AES-256-CBC ===\n")
    
    for i, log_message in enumerate(sample_logs, 1):
        print(f"Test {i}:")
        print(f"Original: {log_message}")
        
        # Encrypt
        encrypted = encrypt_sample_data(log_message, key, 'AES-256-CBC')
        print(f"Encrypted: {encrypted[:50]}..." if len(encrypted) > 50 else f"Encrypted: {encrypted}")
        
        # Decrypt
        decryptor = LogDecryptor(key=key_hex, algorithm='AES-256-CBC')
        decrypted = decryptor.decrypt(encrypted)
        print(f"Decrypted: {decrypted}")
        
        # Verify
        if isinstance(decrypted, dict):
            original = json.loads(log_message) if log_message.startswith('{') else log_message
            if decrypted == original:
                print("✓ Success: Decryption matches original")
            else:
                print("✗ Error: Decryption does not match")
        else:
            if decrypted == log_message:
                print("✓ Success: Decryption matches original")
            else:
                print("✗ Error: Decryption does not match")
        
        print()
    
    # Test with AES-256-GCM
    print("\n=== Testing AES-256-GCM ===\n")
    
    log_message = sample_logs[0]
    print(f"Original: {log_message}")
    
    # Encrypt
    encrypted = encrypt_sample_data(log_message, key, 'AES-256-GCM')
    print(f"Encrypted: {encrypted[:50]}..." if len(encrypted) > 50 else f"Encrypted: {encrypted}")
    
    # Decrypt
    decryptor = LogDecryptor(key=key_hex, algorithm='AES-256-GCM')
    decrypted = decryptor.decrypt(encrypted)
    print(f"Decrypted: {decrypted}")
    
    # Verify
    if decrypted == log_message:
        print("✓ Success: Decryption matches original")
    else:
        print("✗ Error: Decryption does not match")


if __name__ == '__main__':
    main()
