# Arctic Ice Customer App - Mobile Deployment Guide

## Overview
The Arctic Ice Customer app is a mobile application built with React + TypeScript + Vite and Capacitor 6.0 for native platform integration. This app is specifically designed for customers to manage orders, track deliveries, and handle billing.

## App Configuration
- **App ID**: `com.arcticeicesolutions.customer`
- **App Name**: Arctic Ice Customer
- **Target Users**: Customers only
- **Key Features**: Order placement, delivery tracking, invoice management, customer portal

## Prerequisites
- Node.js 18+ and pnpm
- Android Studio (for Android builds)
- Xcode (for iOS builds, macOS only)
- Capacitor CLI: `npm install -g @capacitor/cli`

## Project Structure
```
frontend-customer/
├── src/mobile/           # Mobile-specific React components
├── android/             # Android native project
├── ios/                 # iOS native project
├── public/              # Static assets and PWA manifest
├── capacitor.config.ts  # Capacitor configuration
└── package.json         # Dependencies and build scripts
```

## Installation & Setup
1. Navigate to customer app directory:
   ```bash
   cd frontend-customer
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
- **Title**: Arctic Ice Customer
- **Description**: Customer app for Arctic Ice Solutions - order placement, delivery tracking, and billing management
- **Category**: Business
- **Keywords**: ice delivery, customer portal, order tracking, billing

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
- **Authentication**: JWT-based with customer role restriction

## Role Restrictions
- Only allows users with `customer` role
- Blocks access for staff roles (manager, dispatcher, driver, technician)
- Shows access denied message for unauthorized roles

## Testing
- Test customer login and order placement
- Verify delivery tracking functionality
- Test invoice viewing and payment features
- Ensure staff roles are properly blocked
