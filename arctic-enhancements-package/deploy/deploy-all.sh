#!/bin/bash

echo "=== Arctic Ice Solutions - Enhanced Features Deployment ==="
echo "Deploying all services to arcticicesolutions.com..."
echo ""

set -e

command_exists() {
    command -v "$1" >/dev/null 2>&1
}

echo "Checking deployment tools..."
if ! command_exists vercel; then
    echo "ERROR: Vercel CLI not found. Install with: npm i -g vercel"
    exit 1
fi

if ! command_exists fly; then
    echo "ERROR: Fly CLI not found. Install from: https://fly.io/docs/hands-on/install-flyctl/"
    exit 1
fi

echo "✓ All required tools found"
echo ""

echo "1. Deploying Employee Onboarding Portal..."
cd onboarding
if [ -f "package.json" ]; then
    echo "  Installing dependencies..."
    npm install --silent
    echo "  Building project..."
    npm run build
    echo "  Deploying to Vercel..."
    vercel --prod --scope arcticicesolutions --yes
    echo "  ✓ Employee onboarding deployed"
else
    echo "  ⚠ Skipping onboarding - no package.json found"
fi
cd ..
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

echo "3. Deploying Customer Portal..."
cd customer-portal
if [ -f "package.json" ]; then
    echo "  Installing dependencies..."
    npm install --silent
    echo "  Building project..."
    npm run build
    echo "  Deploying to Vercel..."
    vercel --prod --confirm --yes
    echo "  ✓ Customer portal deployed"
else
    echo "  ⚠ Skipping customer portal - no package.json found"
fi
cd ..
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
echo "All services deployed to arcticicesolutions.com!"
echo ""
echo "Next steps:"
echo "1. Configure environment variables in Fly.io and Vercel dashboards"
echo "2. Set up DNS records for api.arcticicesolutions.com"
echo "3. Run post-deployment validation:"
echo "   curl -I https://arcticicesolutions.com/api/health"
echo "   curl https://api.arcticicesolutions.com/weather/forecast?lat=32.7767&lon=-96.7970"
echo "   curl https://api.arcticicesolutions.com/monitoring/ssl-check"
echo ""
echo "Deployment completed at: $(date)"
