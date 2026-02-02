# 🔐 Production Encryption Key Documentation

## Secure AES-256 Key Generated

**Generated:** February 2, 2026
**Algorithm:** AES-256-CBC
**Key Length:** 256 bits (32 bytes)

### Key Formats

#### Hexadecimal (Primary - use this):
```
04c8ec0929fb619f3da9151d542ef41591044245bebb0cb22f9704645a99e948
```

#### Base64 (Alternative):
```
BMjsCSn7YZ89qRUdVC70FZEEQkW+uwyyL5cEZFqZ6Ug=
```

## ⚠️ Security Notice

This is a **production-grade encryption key**. For internal tool security:

### ✅ DO:
- Store this key in your password manager
- Share only via secure channels (1Password, LastPass, encrypted email)
- Use the `.env` file for local usage (already configured)
- Keep `.env` in `.gitignore` (already done)
- Rotate the key periodically (every 6-12 months)
- Use environment variables in production deployments

### ❌ DON'T:
- Commit to version control (protected by .gitignore ✅)
- Send via unencrypted email/Slack
- Hardcode in application code
- Share publicly

## Usage

### CLI (uses .env automatically):
```bash
python loggin_genie.py --file logs.json
```

### Docker (uses .env automatically):
```bash
docker-compose up -d
```

### Manual override:
```bash
python loggin_genie.py --file logs.json --key "04c8ec0929fb619f3da9151d542ef41591044245bebb0cb22f9704645a99e948"
```

## Backend Integration

**Share this key with your backend team** to encrypt logs before sending to Kibana:

### Python Example:
```python
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes
import base64

ENCRYPTION_KEY = bytes.fromhex('04c8ec0929fb619f3da9151d542ef41591044245bebb0cb22f9704645a99e948')

def encrypt_log(message: str) -> str:
    iv = get_random_bytes(16)
    cipher = AES.new(ENCRYPTION_KEY, AES.MODE_CBC, iv)
    padded = pad(message.encode('utf-8'), AES.block_size)
    ciphertext = cipher.encrypt(padded)
    return base64.b64encode(iv + ciphertext).decode('utf-8')
```

### Node.js Example:
```javascript
const crypto = require('crypto');

const ENCRYPTION_KEY = Buffer.from('04c8ec0929fb619f3da9151d542ef41591044245bebb0cb22f9704645a99e948', 'hex');

function encryptLog(message) {
    const iv = crypto.randomBytes(16);
    const cipher = crypto.createCipheriv('aes-256-cbc', ENCRYPTION_KEY, iv);
    
    let encrypted = cipher.update(message, 'utf8', 'base64');
    encrypted += cipher.final('base64');
    
    const combined = Buffer.concat([iv, Buffer.from(encrypted, 'base64')]);
    return combined.toString('base64');
}
```

## Testing

Test that encryption/decryption works:

```bash
# Create test encrypted log
python examples/create_production_test.py

# Decrypt it
python loggin_genie.py --file examples/test-production-key.json
```

## Key Rotation

When rotating keys:

1. Generate new key: `python -c "from Crypto.Random import get_random_bytes; print(get_random_bytes(32).hex())"`
2. Update `.env` file
3. Update backend encryption configuration
4. Keep old key available for decrypting historical logs

## Storage Recommendations

### Development:
- `.env` file (local, in .gitignore)

### Production/Docker:
- Docker secrets
- Environment variables
- AWS Secrets Manager
- HashiCorp Vault
- Azure Key Vault

## Recovery

If the key is lost, **encrypted logs cannot be recovered**. Backup strategy:

1. Store key in team password manager (1Password, LastPass)
2. Document key in secure internal wiki
3. Keep encrypted backup of key file
4. Multiple team members should have access

---

**This key is now configured in your `.env` file and ready to use!** 🎉
