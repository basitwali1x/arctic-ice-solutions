# Deployment Guide for Arctic Ice Solutions

This guide provides multiple deployment options for the Arctic Ice Solutions application.

## Architecture
- **Frontend**: React + TypeScript + Vite (Static Site)
- **Backend**: FastAPI + Python (API Server)

## Deployment Options

### Option 1: Vercel (Frontend) + Fly.io (Backend) - Recommended

#### Deploy Backend to Fly.io
1. Install Fly CLI: `curl -L https://fly.io/install.sh | sh`
2. Login: `fly auth login`
3. Deploy backend:
   ```bash
   cd backend
   fly launch --name arctic-ice-backend
   fly deploy
   ```
4. Get backend URL: `fly status`

#### Deploy Frontend to Vercel
1. Install Vercel CLI: `npm i -g vercel`
2. Update `vercel.json` with your backend URL
3. Deploy frontend:
   ```bash
   cd frontend
   vercel --prod
   ```
4. Set custom domain in Vercel dashboard

### Option 2: Netlify (Frontend) + Railway (Backend)

#### Deploy Backend to Railway
1. Connect GitHub repo to Railway
2. Select backend folder as root
3. Set environment variables if needed
4. Deploy automatically

#### Deploy Frontend to Netlify
1. Connect GitHub repo to Netlify
2. Update `netlify.toml` with your backend URL
3. Set build directory to `frontend/`
4. Deploy automatically
5. Set custom domain in Netlify dashboard

### Option 3: All-in-One with Railway

1. Create two Railway services:
   - Backend service (root: `backend/`)
   - Frontend service (root: `frontend/`)
2. Set environment variables
3. Connect custom domain

### Option 4: Self-Hosted with Docker

#### Build and Run Backend
```bash
docker build -t arctic-ice-backend .
docker run -p 8000:8000 arctic-ice-backend
```

#### Build and Serve Frontend
```bash
cd frontend
npm run build
npx serve -s dist -l 3000
```

## Environment Variables

### Frontend (.env)
```
VITE_API_URL=https://your-backend-url.com
```

### Backend
```
FRONTEND_URL=https://your-frontend-url.com
```

## Custom Domain Setup

### For Vercel:
1. Go to Vercel dashboard → Project → Settings → Domains
2. Add your custom domain
3. Update DNS records as instructed

### For Netlify:
1. Go to Netlify dashboard → Site → Domain settings
2. Add custom domain
3. Update DNS records as instructed

### For Railway:
1. Go to Railway dashboard → Service → Settings → Domains
2. Add custom domain
3. Update DNS records as instructed

## CORS Configuration

Make sure your backend allows requests from your frontend domain. Update the CORS settings in `backend/app/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Testing Deployment

1. Verify backend health: `https://your-backend-url.com/healthz`
2. Test frontend: `https://your-frontend-domain.com`
3. Test API integration: Login and use features

## Troubleshooting

- **CORS errors**: Update backend CORS settings
- **API not found**: Check VITE_API_URL environment variable
- **Build failures**: Ensure all dependencies are in package.json/pyproject.toml
- **Database issues**: This app uses in-memory storage, data will reset on backend restart

## Cost Estimates

- **Vercel + Fly.io**: ~$5-10/month
- **Netlify + Railway**: ~$5-15/month
- **Self-hosted**: Variable based on server costs

Choose the option that best fits your technical expertise and budget!
