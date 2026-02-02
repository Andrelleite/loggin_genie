"""
Log decryption module supporting multiple encryption algorithms
"""

import base64
import json
from typing import Union
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import hashlib


class LogDecryptor:
    """Decrypt encrypted log data"""
    
    SUPPORTED_ALGORITHMS = [
        'AES-256-CBC',
        'AES-128-CBC',
        'AES-256-GCM',
        'AES-128-GCM',
    ]
    
    def __init__(self, key: str, algorithm: str = 'AES-256-CBC'):
        """
        Initialize decryptor
        
        Args:
            key: Encryption key (hex string or base64)
            algorithm: Encryption algorithm
        """
        
        if algorithm not in self.SUPPORTED_ALGORITHMS:
            raise ValueError(f"Unsupported algorithm: {algorithm}. "
                           f"Supported: {', '.join(self.SUPPORTED_ALGORITHMS)}")
        
        self.algorithm = algorithm
        self.key = self._parse_key(key, algorithm)
    
    def _parse_key(self, key: str, algorithm: str) -> bytes:
        """
        Parse and validate encryption key
        
        Args:
            key: Key as string
            algorithm: Algorithm name
        
        Returns:
            Key as bytes
        """
        
        # Determine expected key length
        if '256' in algorithm:
            key_length = 32  # 256 bits
        elif '128' in algorithm:
            key_length = 16  # 128 bits
        else:
            key_length = 32
        
        # Try to decode key
        try:
            # Try hex
            if len(key) == key_length * 2:
                return bytes.fromhex(key)
            # Try base64
            decoded = base64.b64decode(key)
            if len(decoded) == key_length:
                return decoded
        except Exception:
            pass
        
        # If key is plain text, derive key using SHA-256
        if isinstance(key, str):
            key_bytes = key.encode('utf-8')
            # Use SHA-256 or SHA-512 to derive proper key length
            if key_length == 32:
                return hashlib.sha256(key_bytes).digest()
            elif key_length == 16:
                return hashlib.sha256(key_bytes).digest()[:16]
        
        raise ValueError(f"Invalid key format or length. Expected {key_length} bytes.")
    
    def decrypt(self, encrypted_data: str) -> Union[str, dict]:
        """
        Decrypt encrypted data
        
        Args:
            encrypted_data: Base64 encoded encrypted data
        
        Returns:
            Decrypted string or JSON object
        """
        
        try:
            # Decode base64
            encrypted_bytes = base64.b64decode(encrypted_data)
            
            # Decrypt based on algorithm
            if 'CBC' in self.algorithm:
                decrypted = self._decrypt_cbc(encrypted_bytes)
            elif 'GCM' in self.algorithm:
                decrypted = self._decrypt_gcm(encrypted_bytes)
            else:
                raise ValueError(f"Unsupported algorithm: {self.algorithm}")
            
            # Try to parse as JSON
            try:
                return json.loads(decrypted)
            except json.JSONDecodeError:
                return decrypted
        
        except Exception as e:
            raise Exception(f"Decryption failed: {str(e)}")
    
    def _decrypt_cbc(self, encrypted_bytes: bytes) -> str:
        """
        Decrypt using AES-CBC mode
        
        Format: IV (16 bytes) + ciphertext
        """
        
        # Extract IV (first 16 bytes)
        iv = encrypted_bytes[:16]
        ciphertext = encrypted_bytes[16:]
        
        # Create cipher
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        
        # Decrypt and unpad
        decrypted_padded = cipher.decrypt(ciphertext)
        decrypted = unpad(decrypted_padded, AES.block_size)
        
        return decrypted.decode('utf-8')
    
    def _decrypt_gcm(self, encrypted_bytes: bytes) -> str:
        """
        Decrypt using AES-GCM mode
        
        Format: IV (12 bytes) + tag (16 bytes) + ciphertext
        """
        
        # Extract components
        iv = encrypted_bytes[:12]
        tag = encrypted_bytes[12:28]
        ciphertext = encrypted_bytes[28:]
        
        # Create cipher
        cipher = Cipher(
            algorithms.AES(self.key),
            modes.GCM(iv, tag),
            backend=default_backend()
        )
        
        decryptor = cipher.decryptor()
        
        # Decrypt
        decrypted = decryptor.update(ciphertext) + decryptor.finalize()
        
        return decrypted.decode('utf-8')
    
    def decrypt_batch(self, encrypted_data_list: list) -> list:
        """
        Decrypt multiple encrypted data items
        
        Args:
            encrypted_data_list: List of base64 encoded encrypted data
        
        Returns:
            List of decrypted data
        """
        
        decrypted_list = []
        
        for encrypted_data in encrypted_data_list:
            try:
                decrypted = self.decrypt(encrypted_data)
                decrypted_list.append({
                    'success': True,
                    'data': decrypted
                })
            except Exception as e:
                decrypted_list.append({
                    'success': False,
                    'error': str(e),
                    'original': encrypted_data
                })
        
        return decrypted_list
