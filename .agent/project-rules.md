# Your Choice Ice Platform - Project Rules (Memory)

This file serves as the core "Memory" for AI Agents working on this project. It must be followed strictly to prevent configuration regressions and deployment mix-ups.

## 🏢 Project Identity
- **Project Name**: Your Choice Ice Platform
- **Primary Domain**: [yourchoiceice.com](https://yourchoiceice.com)
- **Admin Domain**: [admin.yourchoiceice.com](https://admin.yourchoiceice.com)
- **Repository**: [github.com/basitwali1x/yourchoice-ice-platform](https://github.com/basitwali1x/yourchoice-ice-platform)

## 🚀 Deployment Infrastructure
- **Hosting Provider**: Fly.io
- **App Name (Fly.io)**: `arctic-ice-api` (Note: Currently naming refers to Arctic Ice, but it's the Your Choice Ice production app)
- **Primary API URL**: `https://api.yourchoiceice.com`

## 🛠 Critical Logic Rules (Do Not Change)
1. **Frontend Routing**: Never use `Navigate` redirects based on the `admin` subdomain inside the `RoleBasedRoute` or `App.tsx` main flow if it leads back to the dashboard. This causes infinite loops.
2. **Auth Gate**: The `AuthProvider` in `AuthContext.tsx` must ALWAYS render `{children}` so that the `ProtectedRoute` can show a loading spinner. Do not wrap the entire app in `!isLoading && children`.
3. **API URL Fallback**: The fallback URL in `urlUtils.ts` must always be `https://api.yourchoiceice.com`. Never use `app-aksfybfm.fly.dev` or other temporary agent URLs.
4. **Environment Variables**:
   - `VITE_API_URL` should always point to the production API.
   - Do not overwrite `vercel.json` or `.env` files with empty placeholders for `GOOGLE_MAPS_API_KEY`.

## 📦 Deployment Pattern
The frontend (React/Vite) is built and served as static files by the FastPI backend.
1. Build frontend: `cd frontend && npm run build`
2. Deploy backend (which serves frontend): `fly deploy` (from root)

## 📁 Repository Mix-up Note
The local folder is named `arctic-ice-solutions`, but it contains the code for the **Your Choice Ice Platform**. Do not try to separate them or rename folders without explicit user permission.
