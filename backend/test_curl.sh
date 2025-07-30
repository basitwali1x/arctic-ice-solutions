#!/bin/bash

echo "Testing Excel import API endpoint..."

echo "Logging in..."
LOGIN_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "manager", "password": "dev-password-change-in-production"}')

echo "Login response: $LOGIN_RESPONSE"

TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
echo "Token: $TOKEN"

if [ -z "$TOKEN" ]; then
    echo "Failed to get token"
    exit 1
fi

echo "Testing Excel import..."
EXCEL_FILE="/home/ubuntu/attachments/29eaa1ae-7e6d-4a83-9bcf-a0d8177d108c/West+La+Ice+Customer+List.xlsx"

if [ ! -f "$EXCEL_FILE" ]; then
    echo "Excel file not found: $EXCEL_FILE"
    exit 1
fi

echo "File exists, size: $(ls -lh "$EXCEL_FILE")"

curl -v -X POST "http://localhost:8000/api/import/excel" \
  -H "Authorization: Bearer $TOKEN" \
  -F "files=@$EXCEL_FILE"

echo "Import test completed"
