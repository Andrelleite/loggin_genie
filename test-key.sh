#!/bin/bash

# Quick test script to verify encryption key is working

echo "🔐 Testing Loggin Genie Encryption Key..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "   Run: cp .env.docker .env"
    exit 1
fi

# Check if key is configured
KEY=$(grep "^ENCRYPTION_KEY=" .env | cut -d= -f2)
if [ -z "$KEY" ] || [ "$KEY" = "your-encryption-key-here" ]; then
    echo "❌ Encryption key not configured in .env"
    echo "   The key should be: 04c8ec0929fb619f3da9151d542ef41591044245bebb0cb22f9704645a99e948"
    exit 1
fi

echo "✅ Encryption key found in .env"
echo "   Key (first 20 chars): ${KEY:0:20}..."
echo ""

# Test decryption
echo "🧪 Testing decryption with production key..."
.venv/bin/python loggin_genie.py --file examples/test-production-key.json --format json > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Decryption test PASSED!"
    echo ""
    echo "🎉 Your tool is ready to use with the production key!"
    echo ""
    echo "Usage:"
    echo "  python loggin_genie.py --file your-logs.json"
    echo "  docker-compose up -d"
else
    echo "❌ Decryption test FAILED"
    echo "   Check your .env configuration"
    exit 1
fi
