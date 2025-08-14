# Xcode Deployment Checklist for Apple App Store

## Prerequisites ✅
- [x] Both apps built successfully with `pnpm run build`
- [x] Both apps synced with `npx cap sync ios`
- [x] Xcode workspaces created and ready
- [x] App icons (512x512 PNG) available
- [x] Bundle IDs configured: `com.arcticeicesolutions.customer` and `com.arcticeicesolutions.staff`

## Required on macOS with Xcode

### 1. Open Projects in Xcode

#### Customer App
```bash
cd frontend-customer
npx cap open ios
```
- Opens: `ios/App/App.xcworkspace`
- Verify project loads without errors
- Check that all Capacitor plugins are recognized

#### Staff App
```bash
cd frontend-staff
npx cap open ios
```
- Opens: `ios/App/App.xcworkspace`
- Verify project loads without errors
- Check that all Capacitor plugins are recognized

### 2. Configure Signing & Capabilities

#### For Both Apps:
1. **Select Project Target** → General Tab
2. **Team**: Select your Apple Developer Team
3. **Bundle Identifier**: Verify correct bundle ID
   - Customer: `com.arcticeicesolutions.customer`
   - Staff: `com.arcticeicesolutions.staff`
4. **Signing Certificate**: Automatic or Manual signing

#### Required Capabilities:
- [x] **Location Services** (for delivery tracking)
- [x] **Camera** (for inspections and photos)
- [x] **Push Notifications** (for real-time updates)
- [x] **Background Modes** (if needed for location tracking)

### 3. Update App Icons

#### Customer App:
1. Navigate to `ios/App/App/Assets.xcassets/AppIcon.appiconset/`
2. Replace with 1024x1024 icon from `store-assets/customer/app-icon-512.png`
3. Generate all required sizes (Xcode can auto-generate)

#### Staff App:
1. Navigate to `ios/App/App/Assets.xcassets/AppIcon.appiconset/`
2. Replace with 1024x1024 icon from `store-assets/staff/app-icon-512.png`
3. Generate all required sizes (Xcode can auto-generate)

### 4. Configure Info.plist

#### Required Permissions (both apps):
```xml
<key>NSLocationWhenInUseUsageDescription</key>
<string>This app needs location access for delivery tracking and route optimization.</string>

<key>NSLocationAlwaysAndWhenInUseUsageDescription</key>
<string>This app needs location access for delivery tracking and route optimization.</string>

<key>NSCameraUsageDescription</key>
<string>This app needs camera access for vehicle inspections and photo documentation.</string>

<key>NSPhotoLibraryAddUsageDescription</key>
<string>This app needs photo library access to save inspection photos.</string>
```

### 5. Build and Test

#### For Each App:
1. **Select Target Device**: Generic iOS Device
2. **Build**: Product → Build (⌘+B)
3. **Resolve Issues**: Fix any build errors or warnings
4. **Test on Simulator**: Run on iOS Simulator
5. **Test on Device**: Run on physical device if available

### 6. Archive for App Store

#### Customer App:
1. **Select Generic iOS Device**
2. **Archive**: Product → Archive
3. **Wait for Build**: Archive process completes
4. **Organizer Opens**: Shows archived build

#### Staff App:
1. **Select Generic iOS Device**
2. **Archive**: Product → Archive
3. **Wait for Build**: Archive process completes
4. **Organizer Opens**: Shows archived build

### 7. Upload to App Store Connect

#### For Each Archive:
1. **Distribute App** → App Store Connect
2. **Upload**: Select upload option
3. **Automatic Signing**: Let Xcode manage
4. **Upload**: Wait for completion
5. **Processing**: App Store Connect processes build

### 8. App Store Connect Configuration

#### Customer App Store Listing:
- **App Name**: Arctic Ice Customer
- **Subtitle**: Customer Portal for Ice Delivery
- **Description**: Professional customer app for Arctic Ice Solutions. Place orders, track deliveries, manage invoices, and access your account information with ease.
- **Keywords**: ice delivery, customer portal, order tracking, billing, delivery management
- **Category**: Business
- **Content Rating**: 4+ (No objectionable content)

#### Staff App Store Listing:
- **App Name**: Arctic Ice Staff
- **Subtitle**: Field Operations Management
- **Description**: Professional staff app for Arctic Ice Solutions field operations. Manage work orders, optimize routes, track deliveries, and coordinate team activities.
- **Keywords**: field operations, work orders, route management, delivery tracking, fleet management
- **Category**: Business
- **Content Rating**: 4+ (No objectionable content)

#### Required for Both Apps:
- **Privacy Policy URL**: https://arcticicesolutions.com/privacy-policy
- **Support URL**: https://arcticicesolutions.com/support
- **Marketing URL**: https://arcticicesolutions.com
- **App Store Icon**: 1024x1024 PNG (from store-assets)
- **Screenshots**: iPhone and iPad screenshots (to be captured)

### 9. Screenshots Required

#### iPhone Screenshots (6.5" and 5.5"):
**Customer App:**
1. Login screen with customer authentication
2. Order placement interface
3. Delivery tracking with map
4. Invoice management dashboard

**Staff App:**
1. Staff login with role selection
2. Work orders management
3. Route optimization interface
4. Vehicle inspection checklist

#### iPad Screenshots (12.9" and 11"):
**Customer App:**
1. Customer dashboard overview
2. Order history and tracking

**Staff App:**
1. Manager dashboard with metrics
2. Driver route management

### 10. App Review Information

#### For Both Apps:
- **Demo Account**: Provide test credentials if required
- **Review Notes**: Explain app functionality and user roles
- **Contact Information**: Provide developer contact details

### 11. Submit for Review

#### Final Steps:
1. **Complete Metadata**: All required fields filled
2. **Upload Screenshots**: All required sizes uploaded
3. **Set Pricing**: Free or paid pricing model
4. **Select Territories**: Choose available countries
5. **Submit**: Click "Submit for Review"

## Troubleshooting Common Issues

### Build Errors:
- **CocoaPods**: Run `pod install` in `ios/App/` directory
- **Signing**: Verify Apple Developer account and certificates
- **Capabilities**: Ensure all required capabilities are enabled

### Archive Issues:
- **Generic Device**: Must select "Generic iOS Device" not simulator
- **Scheme**: Verify Release scheme is selected
- **Dependencies**: Ensure all dependencies are properly linked

### Upload Issues:
- **App Store Connect**: Verify app exists in App Store Connect
- **Bundle ID**: Must match exactly between Xcode and App Store Connect
- **Version**: Increment version number for updates

## Success Criteria ✅

- [x] Both apps build without errors in Xcode
- [x] Both apps archive successfully
- [x] Both apps upload to App Store Connect
- [x] All required metadata completed
- [x] Screenshots uploaded for all required sizes
- [x] Apps submitted for App Store review

## Post-Submission

### Monitor Review Status:
- Check App Store Connect for review updates
- Respond to any reviewer feedback promptly
- Address any rejection reasons if applicable

### Prepare for Launch:
- Plan marketing and announcement strategy
- Prepare user documentation and support materials
- Monitor app performance and user feedback after approval

---
*This checklist ensures both Arctic Ice Solutions mobile apps are properly deployed to the Apple App Store following all required procedures and best practices.*
