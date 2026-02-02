# Create Sample Encrypted Logs

This script creates sample encrypted log files for testing Loggin Genie.

## Usage

```bash
python examples/create_sample_encrypted_logs.py
```

This will create:
- `sample-encrypted-aes-cbc.json` - Logs encrypted with AES-256-CBC
- `sample-encrypted-aes-gcm.json` - Logs encrypted with AES-256-GCM

## Test Decryption

```bash
# Decrypt AES-CBC logs
python loggin_genie.py \
  --file examples/sample-encrypted-aes-cbc.json \
  --key "my-secret-encryption-key-32bytes" \
  --algorithm "AES-256-CBC" \
  --format table

# Decrypt AES-GCM logs  
python loggin_genie.py \
  --file examples/sample-encrypted-aes-gcm.json \
  --key "my-secret-encryption-key-32bytes" \
  --algorithm "AES-256-GCM" \
  --format table
```
