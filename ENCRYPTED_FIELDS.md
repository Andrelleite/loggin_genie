# Encrypted Log Fields

## Overview
This document lists all the encrypted field names used in the Loggin Genie application.

## Standard Encrypted Fields

### Primary Field (Most Common)
- **`message`** - The main log message field that contains encrypted content
  - Format: `IV:ciphertext` (AES-CBC) or base64 encrypted data
  - Used in most log formats
  - Example: `"message": "xmhrDiSD200GTIl7QET6eA==:HxAA14FPHZVKNOFVDdTFdF26KYqkGzJf0zlNcf8Q7H4="`

### Alternative Encrypted Field Names
- **`encrypted_message`** - Explicitly named encrypted message field
  - Used in Kibana/Elasticsearch formatted logs
  - Format: Base64 encoded encrypted string
  - Example: `"encrypted_message": "VGLaOFJm8KE8tK68S/oKt81hpx+QLvhATMZ7LszK2PdGm+Wbjn066r2hrF8wG9+702ThWvGhw7xF90Bw8PEdB68ZScDhbADmjA99WPmKJWMn+z2NTCJHmtSe22/+wZyK"`

### Decrypted Output Fields
After decryption, the following fields are added to each log entry:

- **`decrypted_message`** - The decrypted plaintext of the `message` field
- **`decrypted_encrypted_message`** - The decrypted plaintext of the `encrypted_message` field

## Log Format Examples

### Format 1: Simple Log (message field)
```json
{
  "@timestamp": "2026-02-01T21:07:12.757Z",
  "level": "INFO",
  "service": "auth-service",
  "message": "xmhrDiSD200GTIl7QET6eA==:HxAA14FPHZVKNOFVDdTFdF26KYqkGzJf0zlNcf8Q7H4=",
  "host": "server-2",
  "environment": "staging"
}
```

After decryption:
```json
{
  "@timestamp": "2026-02-01T21:07:12.757Z",
  "level": "INFO",
  "service": "auth-service",
  "message": "xmhrDiSD200GTIl7QET6eA==:HxAA14FPHZVKNOFVDdTFdF26KYqkGzJf0zlNcf8Q7H4=",
  "decrypted_message": "User logged in successfully - user_id: john.doe, ip: 192.168.1.100",
  "host": "server-2",
  "environment": "staging"
}
```

### Format 2: Elasticsearch Log (encrypted_message field)
```json
{
  "_index": "application-logs-2026.02.02",
  "_type": "_doc",
  "_id": "log_0001",
  "_score": 1.0,
  "_source": {
    "@timestamp": "2026-02-02T18:20:23.631896Z",
    "level": "ERROR",
    "service": "auth-service",
    "host": "app-server-5",
    "environment": "production",
    "encrypted_message": "VGLaOFJm8KE8tK68S/oKt81hpx+QLvhATMZ7LszK2PdGm+Wbjn066r2hrF8wG9+702ThWvGhw7xF90Bw8PEdB68ZScDhbADmjA99WPmKJWMn+z2NTCJHmtSe22/+wZyK",
    "message_length": 73,
    "correlation_id": "corr-892660",
    "tags": ["encrypted", "sensitive", "error"]
  }
}
```

After decryption:
```json
{
  "_index": "application-logs-2026.02.02",
  "_type": "_doc",
  "_id": "log_0001",
  "_score": 1.0,
  "_source": {
    "@timestamp": "2026-02-02T18:20:23.631896Z",
    "level": "ERROR",
    "service": "auth-service",
    "host": "app-server-5",
    "environment": "production",
    "encrypted_message": "VGLaOFJm8KE8tK68S/oKt81hpx+QLvhATMZ7LszK2PdGm+Wbjn066r2hrF8wG9+702ThWvGhw7xF90Bw8PEdB68ZScDhbADmjA99WPmKJWMn+z2NTCJHmtSe22/+wZyK",
    "decrypted_encrypted_message": "Authentication failed: Invalid credentials for user admin from 10.0.1.50 - attempt 3/5",
    "message_length": 73,
    "correlation_id": "corr-892660",
    "tags": ["encrypted", "sensitive", "error"]
  }
}
```

## Field Configuration

### Default Field
The default field to decrypt is **`message`** if not specified.

### Custom Field Selection
You can specify which field to decrypt using the "Field to Decrypt" option in the UI:
- Default: `message`
- Alternative: `encrypted_message`
- Custom: Any field name containing encrypted data

## Encryption Formats Supported

### AES-256-CBC (Default)
- Format: `IV:ciphertext` where both are base64 encoded
- IV length: 16 bytes (24 characters base64)
- Requires padding

### AES-128-CBC
- Format: Same as AES-256-CBC
- Uses 128-bit key instead of 256-bit

### AES-256-GCM
- Format: Base64 encoded (IV + tag + ciphertext)
- IV length: 12 bytes
- Tag length: 16 bytes
- No padding required

### AES-128-GCM
- Format: Same as AES-256-GCM
- Uses 128-bit key instead of 256-bit

## Summary Table

| Field Name | Usage | Output Field | Common In |
|------------|-------|--------------|-----------|
| `message` | Primary encrypted field | `decrypted_message` | Simple logs, production logs |
| `encrypted_message` | Explicit encrypted field | `decrypted_encrypted_message` | Kibana/Elasticsearch logs |
| (custom) | User-defined field | `decrypted_<fieldname>` | Custom log formats |

## Notes

1. **Preserved Fields**: All original log fields are preserved after decryption
2. **Dual Output**: Both encrypted and decrypted versions are available
3. **Nested Support**: Encryption fields can be in nested objects (e.g., `_source.message`)
4. **Array Support**: Can decrypt arrays of log objects
5. **NDJSON Support**: Newline-delimited JSON files are fully supported
