# Arctic Ice Solutions - Enhanced Features Deployment Package

This package contains all the enhanced features for Arctic Ice Solutions, configured for deployment to yourchoiceice.com.

## Components

1. **onboarding/** - Employee training portal with blockchain NFT certifications
2. **weather-routing/** - AI weather integration for route optimization  
3. **customer-portal/** - Next.js customer portal prototype
4. **monitoring/** - SSL/domain monitoring and alerts
5. **ai-imports/** - Excel/QuickBooks/Google Sheets AI-powered data importer

## Quick Deployment

```bash
chmod +x deploy/deploy-all.sh
./deploy/deploy-all.sh
```

## Individual Component Deployment

### Employee Onboarding
```bash
cd onboarding && vercel --prod --scope arcticicesolutions
```

### Weather Routing
```bash
cd weather-routing && fly deploy --app arctic-ice-weather --remote-only
```

### Customer Portal
```bash
cd customer-portal && vercel --prod --confirm
```

### AI Imports
```bash
cd ai-imports && fly deploy --app arctic-ai-imports
```

### Monitoring
```bash
cd monitoring && chmod +x ssl-check.sh && ./ssl-check.sh
```

## Post-Deployment Validation

```bash
# Check all endpoints
curl -I https://yourchoiceice.com/api/health
curl https://api.yourchoiceice.com/weather/forecast?lat=40.71&lon=-74.01
curl https://api.yourchoiceice.com/monitoring/ssl-check
openssl s_client -connect yourchoiceice.com:443 | openssl x509 -noout -dates
```

## Environment Variables Required

- `OPENWEATHER_API_KEY` - OpenWeatherMap API key
- `GEMINI_API_KEY` - Google Gemini AI API key  
- `QUICKBOOKS_CLIENT_ID` - QuickBooks OAuth client ID
- `QUICKBOOKS_CLIENT_SECRET` - QuickBooks OAuth client secret
- `VITE_GA_MEASUREMENT_ID` - Google Analytics measurement ID

## Domain Configuration

All services are configured to use:
- Frontend: `https://yourchoiceice.com`
- API: `https://api.yourchoiceice.com`
- OAuth Redirects: `https://yourchoiceice.com/auth/callback`
