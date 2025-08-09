# Arctic Ice Solutions Mobile App

Mobile application for Arctic Ice Solutions field operations, built with React, TypeScript, and Capacitor.

## Quick Start

```bash
# Install dependencies
pnpm install

# Start development server
pnpm dev

# Build for production
pnpm build

# Sync to native platforms
npx cap sync

# Build Android app
pnpm cap:build:android

# Build iOS app (macOS only)
pnpm cap:build:ios
```

## Mobile Features

### Driver App
- **GPS Tracking**: Real-time location tracking during deliveries
- **Route Management**: Optimized delivery routes with turn-by-turn navigation
- **Delivery Confirmation**: Photo capture and digital signatures
- **Receipt Printing**: Bluetooth thermal printer integration
- **Offline Support**: Works without internet connection

### Customer Portal
- **Order Tracking**: Real-time delivery status updates
- **Account Management**: View billing and payment history
- **Delivery Scheduling**: Request delivery appointments
- **Push Notifications**: Order status and delivery alerts

### Inspection Module
- **Photo Documentation**: Camera integration for inspection photos
- **Digital Forms**: Structured inspection checklists
- **GPS Coordinates**: Location tagging for inspection sites
- **Report Generation**: PDF reports with photos and data

## Architecture

### Technology Stack
- **Frontend**: React 18 + TypeScript + Vite
- **Mobile**: Capacitor 6.0 for native iOS/Android
- **PWA**: VitePWA plugin for web app capabilities
- **UI**: Tailwind CSS + Radix UI components
- **State**: React hooks and context
- **Backend**: FastAPI (Python) REST API

### Mobile-Specific Components

```
src/mobile/
├── MobileApp.tsx           # Main mobile app router
├── pages/
│   ├── MobileDriver.tsx    # Driver dashboard and tools
│   ├── MobileCustomer.tsx  # Customer portal
│   └── MobileInspection.tsx # Inspection forms
├── components/
│   ├── MobileHeader.tsx    # Mobile navigation header
│   ├── MobileNavigation.tsx # Bottom navigation
│   └── MobileLocationAuth.tsx # GPS permission handling
└── utils/
    └── capacitor.ts        # Native API abstractions
```

## Native Capabilities

### Geolocation
```typescript
import { getCurrentPosition, watchPosition } from '../utils/capacitor';

// Get current location
const position = await getCurrentPosition();

// Watch location changes
const watchId = await watchPosition((position) => {
  console.log('New position:', position.coords);
});
```

### Camera
```typescript
import { takePhoto } from '../utils/capacitor';

// Capture photo
const photoData = await takePhoto();
```

### Push Notifications
```typescript
import { initializePushNotifications } from '../utils/capacitor';

// Initialize notifications
await initializePushNotifications();
```

## Development

### Prerequisites
- Node.js 18+
- pnpm package manager
- Java JDK 17 (OpenJDK recommended)
- Android Studio (for Android development) - **Recommended approach**
- Xcode (for iOS development, macOS only)

### Environment Setup

1. **Clone and Install**:
```bash
git clone https://github.com/basitwali1x/arctic-ice-solutions.git
cd arctic-ice-solutions/frontend
pnpm install
```

2. **Configure Environment**:
```bash
# Copy environment template
cp .env.example .env.local

# Set API endpoints
VITE_API_URL=http://localhost:8000
```

3. **Start Development**:
```bash
# Start web dev server
pnpm dev

# Start backend (in separate terminal)
cd ../backend
poetry run fastapi dev app/main.py
```

### Testing Mobile Features

1. **Web Browser**: Test basic functionality at `http://localhost:5173/mobile`
2. **Android Emulator**: Use Android Studio AVD
3. **iOS Simulator**: Use Xcode Simulator (macOS only)
4. **Physical Devices**: Deploy to real devices for GPS/camera testing

### Build Process

```bash
# 1. Build web assets
pnpm build

# 2. Sync to native projects
npx cap sync

# 3. Open in native IDEs
npx cap open android  # Android Studio
npx cap open ios      # Xcode (macOS only)

# 4. Build from IDEs or command line
npx cap build android
npx cap build ios
```

## Deployment

### Web (PWA)
```bash
# Build and deploy web version
pnpm build
# Deploy dist/ folder to web server
```

### Android
1. Open in Android Studio: `npx cap open android`
2. Build → Generate Signed Bundle/APK
3. Upload to Google Play Console

### iOS
1. Open in Xcode: `npx cap open ios`
2. Product → Archive
3. Distribute to App Store Connect

## Configuration

### Capacitor Config
```typescript
// capacitor.config.ts
export default {
  appId: 'com.arcticeicesolutions.mobile',
  appName: 'Arctic Ice Solutions',
  webDir: 'dist',
  plugins: {
    Geolocation: {
      permissions: ['location']
    },
    Camera: {
      permissions: ['camera']
    },
    PushNotifications: {
      presentationOptions: ['badge', 'sound', 'alert']
    }
  }
};
```

### PWA Manifest
```json
{
  "name": "Arctic Ice Solutions",
  "short_name": "Arctic Ice",
  "start_url": "/mobile",
  "display": "standalone",
  "theme_color": "#2563eb",
  "background_color": "#ffffff"
}
```

## Troubleshooting

### Common Issues

1. **GPS Not Working**: Check location permissions in device settings
2. **Camera Access Denied**: Verify camera permissions
3. **Build Failures**: Ensure Android SDK/Xcode are properly installed
4. **Plugin Errors**: Run `npx cap sync` after adding new plugins

### Debug Commands
```bash
# Check Capacitor doctor
npx cap doctor

# View native logs
npx cap run android --livereload
npx cap run ios --livereload

# Clear caches
rm -rf node_modules/.vite
pnpm install
```

## Contributing

1. Create feature branch: `git checkout -b feature/mobile-enhancement`
2. Make changes and test on multiple devices
3. Update documentation if needed
4. Submit pull request with testing notes

## License

Copyright © 2025 Arctic Ice Solutions. All rights reserved.
