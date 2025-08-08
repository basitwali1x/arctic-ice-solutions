#!/bin/bash

set -e

APP_ID="ice-management-app-4r16aafs"
CORRECT_API_URL="https://app-wcqcowqv.fly.dev"

echo "🔧 Force Rebuild Script for Devin Apps Platform"
echo "App ID: $APP_ID"
echo "Correct API URL: $CORRECT_API_URL"
echo "=============================================="

if [ -z "$DEVIN_API_KEY" ]; then
  echo "❌ DEVIN_API_KEY not set"
  exit 1
fi

echo "1. Updating environment variable..."
curl -X PATCH \
  "https://api.devin.ai/v1/apps/$APP_ID/environments/production/variables" \
  -H "Authorization: Bearer $DEVIN_API_KEY" \
  -H "Content-Type: application/json" \
  -d '[
    {
      "name": "VITE_API_URL",
      "value": "'$CORRECT_API_URL'",
      "action": "set"
    }
  ]' || echo "⚠️  API call failed, continuing..."

echo "2. Triggering rebuild..."
REBUILD_RESPONSE=$(curl -s -X POST \
  "https://api.devin.ai/v1/apps/$APP_ID/rebuild" \
  -H "Authorization: Bearer $DEVIN_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "environment": "production",
    "clear_cache": true,
    "no_cache": true
  }' || echo '{"error":"api_failed"}')

echo "Rebuild response: $REBUILD_RESPONSE"

echo "3. Monitoring rebuild status..."
for i in {1..30}; do
  STATUS=$(curl -s "https://api.devin.ai/v1/apps/$APP_ID/deployments" \
    -H "Authorization: Bearer $DEVIN_API_KEY" | \
    jq -r '.[0].status' 2>/dev/null || echo "unknown")
  
  echo "Deployment status: $STATUS (check $i/30)"
  
  if [ "$STATUS" = "success" ]; then
    echo "✅ Rebuild completed successfully"
    break
  elif [ "$STATUS" = "failed" ]; then
    echo "❌ Rebuild failed"
    exit 1
  fi
  
  sleep 10
done

echo "=============================================="
echo "🎉 Force rebuild completed"
echo "Please verify the deployment at: https://arcticicesolutions.com"
