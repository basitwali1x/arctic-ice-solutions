#!/bin/bash

echo "🔍 Validating SSL certificates..."

if openssl x509 -in certs/demo/demo-san.crt -noout -checkend 86400; then
    echo "✅ Certificate is valid and not expiring within 24 hours"
else
    echo "⚠️  Certificate is expiring soon or invalid"
fi

cert_hash=$(openssl x509 -noout -modulus -in certs/demo/demo-san.crt | openssl md5)
key_hash=$(openssl rsa -noout -modulus -in certs/demo/demo.key | openssl md5)

if [ "$cert_hash" = "$key_hash" ]; then
    echo "✅ Certificate and private key match"
else
    echo "❌ Certificate and private key do not match"
fi

echo "📅 Certificate expires on:"
openssl x509 -in certs/demo/demo-san.crt -noout -enddate

echo ""
echo "🌐 Testing HTTPS connection..."
if curl -k -s -o /dev/null -w "%{http_code}" https://localhost:5174/ | grep -q "200"; then
    echo "✅ HTTPS connection successful"
else
    echo "⚠️  HTTPS connection failed (server may not be running)"
fi
