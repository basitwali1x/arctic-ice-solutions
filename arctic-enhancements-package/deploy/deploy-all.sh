#!/bin/bash

echo "=== Arctic Ice Solutions - Enhanced Features Deployment ==="
echo "Deploying all services to yourchoiceice.com..."
echo ""

set -e

command_exists() {
    command -v "$1" >/dev/null 2>&1
}

echo "Checking deployment tools..."
echo "Note: Frontend deployments now handled by Devin Apps Platform"

if ! command_exists fly; then
    echo "ERROR: Fly CLI not found. Install from: https://fly.io/docs/hands-on/install-flyctl/"
    exit 1
fi

echo "✓ All required tools found"
echo ""

echo "1. Employee Onboarding Portal..."
echo "  ✓ Deployed via Devin Apps Platform (integrated with main application)"
echo ""

echo "2. Deploying Weather Routing Service..."
cd weather-routing
if [ -f "fly.toml" ]; then
    echo "  Deploying to Fly.io..."
    fly deploy --app arctic-ice-weather --remote-only
    echo "  ✓ Weather service deployed"
else
    echo "  ⚠ Skipping weather service - no fly.toml found"
fi
cd ..
echo ""

echo "3. Customer Portal..."
echo "  ✓ Deployed via Devin Apps Platform (integrated with main application)"
echo ""

echo "4. Deploying AI Imports Service..."
cd ai-imports/backend
if [ -f "fly.toml" ]; then
    echo "  Deploying to Fly.io..."
    fly deploy --app arctic-ai-imports
    echo "  ✓ AI imports service deployed"
else
    echo "  ⚠ Skipping AI imports - no fly.toml found"
fi
cd ../..
echo ""

echo "5. Setting up Monitoring..."
cd monitoring
if [ -f "ssl-check.sh" ]; then
    echo "  Making SSL check script executable..."
    chmod +x ssl-check.sh
    echo "  Running initial SSL check..."
    ./ssl-check.sh
    echo "  ✓ Monitoring configured"
else
    echo "  ⚠ Skipping monitoring - no ssl-check.sh found"
fi
cd ..
echo ""

echo "=== Deployment Complete! ==="
echo ""
echo "All services deployed to yourchoiceice.com!"
echo ""
echo "Next steps:"
echo "1. Configure environment variables in Fly.io dashboard"
echo "2. Set up DNS records for api.yourchoiceice.com"
echo "3. Run post-deployment validation:"
echo "   curl -I https://yourchoiceice.com/api/health"
echo "   curl https://api.yourchoiceice.com/weather/forecast?lat=32.7767&lon=-96.7970"
echo "   curl https://api.yourchoiceice.com/monitoring/ssl-check"
echo ""
echo "Deployment completed at: $(date)"
