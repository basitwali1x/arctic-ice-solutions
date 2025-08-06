#!/bin/bash

set -e

API_URL="https://app-rawyclbe.fly.dev"
FRONTEND_URL="https://ice-management-app-4r16aafs.devinapps.com"
TEST_TOKEN="${TEST_TOKEN:-test-token-123}"

echo "🚀 Starting AI Routing System Test"
echo "Frontend: $FRONTEND_URL"
echo "Backend: $API_URL"
echo "=================================="

echo "1. Testing frontend accessibility..."
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL")
if [ "$FRONTEND_STATUS" -eq 200 ]; then
  echo "✅ Frontend accessible (HTTP $FRONTEND_STATUS)"
else
  echo "❌ Frontend not accessible (HTTP $FRONTEND_STATUS)"
  exit 1
fi

echo "2. Testing backend connectivity..."
BACKEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/api/health" || echo "000")
if [ "$BACKEND_STATUS" -eq 200 ]; then
  echo "✅ Backend accessible (HTTP $BACKEND_STATUS)"
else
  echo "❌ Backend not accessible (HTTP $BACKEND_STATUS)"
  exit 1
fi

echo "3. Checking frontend configuration..."
CONFIG_CHECK=$(curl -s "$FRONTEND_URL/env-config.js" | grep -o "app-rawyclbe.fly.dev" || echo "")
if [ -n "$CONFIG_CHECK" ]; then
  echo "✅ Frontend configured with correct backend URL"
else
  echo "❌ Frontend not configured with correct backend URL"
  curl -s "$FRONTEND_URL/env-config.js" | head -3
fi

echo "4. Testing route optimization endpoint..."
ROUTE_RESPONSE=$(curl -s -X POST "$API_URL/api/routes/optimize" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TEST_TOKEN" \
  -d '{"location_id":"test","customers":[{"id":"test-1","address":"123 Test St"}]}' \
  2>/dev/null || echo '{"error":"connection_failed"}')

if echo "$ROUTE_RESPONSE" | grep -q "routes\|optimized\|success"; then
  echo "✅ Route optimization endpoint responding"
else
  echo "❌ Route optimization endpoint failed"
  echo "Response: $ROUTE_RESPONSE"
fi

echo "5. Testing Google Maps integration..."
MAPS_TEST=$(curl -s "$FRONTEND_URL" | grep -o "google.*maps" || echo "")
if [ -n "$MAPS_TEST" ]; then
  echo "✅ Google Maps integration detected"
else
  echo "⚠️  Google Maps integration not detected (may be loaded dynamically)"
fi

echo "6. Final connectivity verification..."
FINAL_TEST=$(curl -s -X GET "$FRONTEND_URL/api/health" 2>/dev/null || echo "failed")
if echo "$FINAL_TEST" | grep -q "200\|ok\|healthy"; then
  echo "✅ Frontend-to-backend proxy working"
else
  echo "❌ Frontend-to-backend proxy failed"
  echo "Response: $FINAL_TEST"
fi

echo "=================================="
echo "🎉 AI Routing System Test Complete"
echo "Check individual test results above"
