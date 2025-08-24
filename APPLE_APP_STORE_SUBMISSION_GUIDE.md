# Apple App Store Submission Guide - Arctic Ice Solutions

## Overview
Both Arctic Ice Solutions mobile applications are technically ready for Apple App Store deployment. This guide provides step-by-step instructions to complete the submission process.

## Apps Ready for Submission

### 1. Arctic Ice Customer App ✅
- **Bundle ID**: `com.arcticeicesolutions.customer`
- **App Name**: Arctic Ice Customer
- **Xcode Project**: `frontend-customer/ios/App/App.xcworkspace`
- **Target Users**: Customers only
- **Status**: Ready for deployment

### 2. Arctic Ice Staff App ✅
- **Bundle ID**: `com.arcticeicesolutions.staff`
- **App Name**: Arctic Ice Staff
- **Xcode Project**: `frontend-staff/ios/App/App.xcworkspace`
- **Target Users**: Staff (manager, dispatcher, driver, technician)
- **Status**: Ready for deployment

## Prerequisites Completed ✅
- [x] iOS projects built and synced with Capacitor
- [x] Bundle IDs configured correctly
- [x] App icons prepared (512x512 PNG format)
- [x] Privacy usage descriptions added to Info.plist
- [x] Capacitor plugins configured (6 plugins total)
- [x] Store assets and screenshots documented

## Required: Apple Developer Account Setup

### Step 1: Apple Developer Account Access
You will need:
- Apple Developer Program membership ($99/year)
- Apple ID with developer account access
- Access to App Store Connect (https://appstoreconnect.apple.com)

### Step 2: Create App Records in App Store Connect
1. Log in to App Store Connect
2. Click "My Apps" → "+" → "New App"

**For Customer App:**
- Platform: iOS
- Name: Arctic Ice Customer
- Primary Language: English (U.S.)
- Bundle ID: com.arcticeicesolutions.customer
- SKU: AIC-PROD-1.0 (unique identifier)

**For Staff App:**
- Platform: iOS
- Name: Arctic Ice Staff
- Primary Language: English (U.S.)
- Bundle ID: com.arcticeicesolutions.staff
- SKU: AIS-PROD-1.0 (unique identifier)

## Xcode Configuration and Upload Process

### Step 3: Open Projects in Xcode (Requires macOS)

**Customer App:**
```bash
cd frontend-customer
npx cap open ios
```

**Staff App:**
```bash
cd frontend-staff
npx cap open ios
```

### Step 4: Configure Signing & Capabilities
For each app in Xcode:
1. Select the project target → "Signing & Capabilities" tab
2. Select your Apple Developer Team
3. Enable "Automatically manage signing"
4. Verify bundle identifier matches App Store Connect
5. Ensure these capabilities are enabled:
   - Location Services
   - Camera
   - Push Notifications

### Step 5: Update App Icons
1. Navigate to `ios/App/App/Assets.xcassets/AppIcon.appiconset/`
2. Replace with icons from:
   - Customer: `store-assets/customer/app-icon-512.png`
   - Staff: `store-assets/staff/app-icon-512.png`
3. Let Xcode generate all required sizes

### Step 6: Build and Archive
For each app:
1. Select "Generic iOS Device" as target
2. Product → Build (⌘+B) to verify no errors
3. Product → Archive to create archive
4. Wait for Organizer to open with completed archive

### Step 7: Upload to App Store Connect
For each archive in Organizer:
1. Click "Distribute App"
2. Select "App Store Connect"
3. Choose "Upload"
4. Use automatic signing
5. Click "Upload" and wait for completion

## App Store Connect Metadata Configuration

### Step 8: Complete App Store Listings

**Customer App Metadata:**
- App Name: Arctic Ice Customer
- Subtitle: Customer Portal for Ice Delivery
- Description: "Professional customer app for Arctic Ice Solutions. Place orders, track deliveries, manage invoices, and access your account information with ease."
- Keywords: ice delivery, customer portal, order tracking, billing, delivery management
- Category: Business
- Content Rating: 4+ (No objectionable content)

**Staff App Metadata:**
- App Name: Arctic Ice Staff
- Subtitle: Field Operations Management
- Description: "Professional staff app for Arctic Ice Solutions field operations. Manage work orders, optimize routes, track deliveries, and coordinate team activities."
- Keywords: field operations, work orders, route management, delivery tracking, fleet management
- Category: Business
- Content Rating: 4+ (No objectionable content)

### Step 9: Required URLs and Information
For both apps:
- **Privacy Policy URL**: https://arcticicesolutions.com/privacy-policy
- **Support URL**: https://arcticicesolutions.com/support
- **Marketing URL**: https://arcticicesolutions.com

### Step 10: Upload Screenshots
Screenshots are documented in `STORE_ASSETS_READY.md`. Required sizes:
- iPhone 6.5" (1284 x 2778 pixels)
- iPhone 5.5" (1242 x 2208 pixels)
- iPad Pro 12.9" (2048 x 2732 pixels)

### Step 11: Select Builds and Submit
1. In App Store Connect, go to each app's version
2. In the "Build" section, select the uploaded build
3. Complete all required metadata fields
4. Click "Submit for Review"

## Verification Checklist

### Before Submission:
- [ ] Both apps build without errors in Xcode
- [ ] Archives created successfully for both apps
- [ ] Uploads completed to App Store Connect
- [ ] All metadata fields completed
- [ ] Screenshots uploaded for all required sizes
- [ ] Privacy policy URL accessible
- [ ] App icons properly configured

### After Submission:
- [ ] Both apps show "Waiting for Review" status
- [ ] Build version numbers recorded
- [ ] App Store Connect links saved

## Expected Timeline
- **Upload Processing**: 15-30 minutes per app
- **Apple Review**: 24-48 hours (typical)
- **Review Response**: Address any feedback within 7 days

## Troubleshooting Common Issues

### Build Errors:
- Run `pod install` in `ios/App/` directory if CocoaPods issues
- Verify Apple Developer account and certificates
- Ensure all required capabilities are enabled

### Upload Issues:
- Verify app exists in App Store Connect
- Bundle ID must match exactly
- Increment version number for updates

## Success Criteria
✅ Both apps successfully submitted to Apple App Store
✅ "Waiting for Review" status in App Store Connect
✅ All required metadata and assets uploaded
✅ Build version numbers documented

## Contact Information
For technical support during deployment:
- Repository: https://github.com/basitwali1x/arctic-ice-solutions
- Documentation: See XCODE_DEPLOYMENT_CHECKLIST.md for detailed steps

---
*This guide ensures both Arctic Ice Solutions mobile apps are properly deployed to the Apple App Store following all required procedures and best practices.*
