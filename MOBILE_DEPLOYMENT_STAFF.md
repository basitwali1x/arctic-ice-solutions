# Arctic Ice Staff App - Mobile Deployment Guide

## Overview
The Arctic Ice Staff app is a mobile application built with React + TypeScript + Vite and Capacitor 6.0 for native platform integration. This app is specifically designed for staff members to manage field operations, work orders, and route management.

## App Configuration
- **App ID**: `com.arcticeicesolutions.staff`
- **App Name**: Arctic Ice Staff
- **Target Users**: Staff only (manager, dispatcher, driver, technician)
- **Key Features**: Work orders, driver dashboard, route management, vehicle inspections

## Prerequisites
- Node.js 18+ and pnpm
- Android Studio (for Android builds)
- Xcode (for iOS builds, macOS only)
- Capacitor CLI: `npm install -g @capacitor/cli`

## Project Structure
```
frontend-staff/
├── src/mobile/           # Mobile-specific React components
├── android/             # Android native project
├── ios/                 # iOS native project
├── public/              # Static assets and PWA manifest
├── capacitor.config.ts  # Capacitor configuration
└── package.json         # Dependencies and build scripts
```

## Installation & Setup
1. Navigate to staff app directory:
   ```bash
   cd frontend-staff
   ```

2. Install dependencies:
   ```bash
   pnpm install
   ```

3. Build web assets:
   ```bash
   pnpm run build
   ```

4. Sync with native projects:
   ```bash
   npx cap sync
   ```

## Build Commands

### Android
```bash
# Development build
pnpm run cap:build:android

# Open in Android Studio for release builds
npx cap open android
```

### iOS
```bash
# Development build
pnpm run cap:build:ios

# Open in Xcode for release builds
npx cap open ios
```

## Required Store Assets

### Icons
- **Android**: 512x512 PNG (adaptive icon)
- **iOS**: 1024x1024 PNG (App Store icon)
- **PWA Icons**: 72x72, 96x96, 128x128, 144x144, 152x152, 192x192, 384x384, 512x512

### Screenshots
- **Android**: Phone (16:9), Tablet (16:10)
- **iOS**: iPhone (various sizes), iPad (various sizes)

### Store Listings
- **Title**: Arctic Ice Staff
- **Description**: Staff app for Arctic Ice Solutions - field operations, work orders, and route management
- **Category**: Business
- **Keywords**: field operations, work orders, route management, delivery tracking

## App Store Deployment

### Google Play Store
1. Generate signed AAB in Android Studio
2. Upload to Google Play Console
3. Complete store listing with assets
4. Submit for review

### iOS App Store
1. Archive and upload via Xcode
2. Complete App Store Connect listing
3. Submit for review

## Environment Configuration
- **API URL**: Configure `VITE_API_URL` in `.env.local`
- **Backend**: Connects to Arctic Ice Solutions API
- **Authentication**: JWT-based with staff role restriction

## Role Restrictions
- Only allows users with staff roles: manager, dispatcher, driver, technician
- Blocks access for customer role
- Shows access denied message for unauthorized roles

## Feature Access by Role
- **Manager**: All features (work orders, routes, driver dashboard, inspections)
- **Dispatcher**: Routes and dashboard
- **Driver**: Routes, driver dashboard, inspections
- **Technician**: Work orders, inspections, dashboard

## Testing
- Test staff login for different roles
- Verify work order management
- Test route optimization and driver features
- Test vehicle inspection functionality
- Ensure customer role is properly blocked
