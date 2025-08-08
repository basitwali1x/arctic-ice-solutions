#!/bin/bash

echo "🚀 Deploying Arctic Ice Solutions Reverse Proxy"
echo "================================================"

if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    echo "✅ Docker installed. Please log out and back in to use Docker without sudo."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose not found. Installing..."
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

echo "🔧 Starting reverse proxy services..."
docker-compose up -d

echo "✅ Reverse proxy deployed!"
echo ""
echo "📋 Next Steps:"
echo "1. Configure DNS records:"
echo "   - Point arcticicesolutions.com A record to this server's IP"
echo "   - Point employee.arcticicesolutions.com A record to this server's IP"
echo ""
echo "2. Test the proxy:"
echo "   curl -H 'Host: arcticicesolutions.com' http://localhost"
echo ""
echo "3. Monitor logs:"
echo "   docker-compose logs -f"
echo ""
echo "🌐 Target: https://employee-dashboard-qygeggpo.devinapps.com"
