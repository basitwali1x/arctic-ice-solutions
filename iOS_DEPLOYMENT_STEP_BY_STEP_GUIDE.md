# iOS App Store Deployment - Step-by-Step Guide

## Prerequisites Checklist ✅
- [x] Apple Developer Account (active membership)
- [x] macOS environment with Xcode installed
- [x] All store assets prepared (icons, screenshots, feature graphics)
- [x] Bundle IDs configured: `com.arcticeicesolutions.customer` and `com.arcticeicesolutions.staff`

## Step 1: Get Project Files on Mac

### Option A: Clone Repository
```bash
git clone https://github.com/basitwali1x/arctic-ice-solutions.git
cd arctic-ice-solutions
```

### Option B: Download and Transfer
- Download project files from GitHub
- Transfer to Mac via USB, cloud storage, or network

## Step 2: Install Dependencies

```bash
# Customer App
cd frontend-customer
npm install
npx cap sync ios

# Staff App  
cd ../frontend-staff
npm install
npx cap sync ios
```

## Step 3: Open Projects in Xcode

```bash
# Customer App (open first)
cd frontend-customer
npx cap open ios

# Staff App (open in separate Xcode window)
cd ../frontend-staff
npx cap open ios
```

## Step 4: Configure Code Signing (For Each App)

1. **Select Project Target**
   - Click project name in navigator (left panel)
   - Select "App" target (not "App (iOS)")

2. **Configure Signing**
   - Go to "Signing & Capabilities" tab
   - Select your Apple Developer Team from dropdown
   - ✅ Enable "Automatically manage signing"
   - Verify Bundle Identifier matches:
     - Customer: `com.arcticeicesolutions.customer`
     - Staff: `com.arcticeicesolutions.staff`

3. **Verify Capabilities**
   - Ensure these capabilities are enabled:
     - Location Services
     - Camera
     - Push Notifications

## Step 5: Update App Icons

### Customer App Icons
1. Navigate to: `ios/App/App/Assets.xcassets/AppIcon.appiconset/`
2. Use icon from: `store-assets/customer/app-icon-512.png`
3. Drag 1024x1024 version into AppIcon slot in Xcode
4. Let Xcode generate all required sizes

### Staff App Icons
1. Navigate to: `ios/App/App/Assets.xcassets/AppIcon.appiconset/`
2. Use icon from: `store-assets/staff/app-icon-512.png`
3. Drag 1024x1024 version into AppIcon slot in Xcode
4. Let Xcode generate all required sizes

## Step 6: Build and Test (For Each App)

1. **Select Target Device**
   - Choose "Generic iOS Device" (not simulator)
   - Do NOT select a specific device

2. **Build Project**
   - Press ⌘+B or Product → Build
   - ✅ Verify no build errors
   - Fix any issues before proceeding

3. **Clean if Needed**
   - If build fails: Product → Clean Build Folder
   - Try building again

## Step 7: Archive Apps (For Each App)

1. **Create Archive**
   - Ensure "Generic iOS Device" is selected
   - Product → Archive
   - Wait for archive process to complete

2. **Organizer Opens**
   - Xcode Organizer will open automatically
   - Your archive should appear in the list
   - Note the version and build number

## Step 8: Upload to App Store Connect

### For Each Archive:
1. **Start Distribution**
   - Select your archive in Organizer
   - Click "Distribute App"

2. **Choose Distribution Method**
   - Select "App Store Connect"
   - Click "Next"

3. **Upload Options**
   - Select "Upload"
   - Click "Next"

4. **Signing Options**
   - Choose "Automatically manage signing"
   - Click "Next"

5. **Review and Upload**
   - Review app information
   - Click "Upload"
   - Wait for upload to complete (may take several minutes)

## Step 9: Create App Records in App Store Connect

1. **Login to App Store Connect**
   - Go to: https://appstoreconnect.apple.com
   - Login with Apple Developer credentials

2. **Create Customer App**
   - Click "My Apps" → "+" → "New App"
   - **Name**: "Arctic Ice Customer"
   - **Bundle ID**: `com.arcticeicesolutions.customer`
   - **SKU**: `AIC-PROD-1.0`
   - **User Access**: Full Access

3. **Create Staff App**
   - Click "My Apps" → "+" → "New App"
   - **Name**: "Arctic Ice Staff"
   - **Bundle ID**: `com.arcticeicesolutions.staff`
   - **SKU**: `AIS-PROD-1.0`
   - **User Access**: Full Access

## Step 10: Complete Store Listings

### Customer App Listing:
- **App Name**: "Arctic Ice Customer"
- **Subtitle**: "Customer Portal for Ice Delivery"
- **Category**: Business
- **Content Rating**: 4+
- **Privacy Policy URL**: https://arcticicesolutions.com/privacy
- **Support URL**: https://arcticicesolutions.com/support

### Staff App Listing:
- **App Name**: "Arctic Ice Staff"
- **Subtitle**: "Field Operations Management"
- **Category**: Business
- **Content Rating**: 4+
- **Privacy Policy URL**: https://arcticicesolutions.com/privacy
- **Support URL**: https://arcticicesolutions.com/support

## Step 11: Upload Store Assets

### Screenshots (Use files from store-assets/):
- iPhone 6.5": Upload all customer/staff screenshots
- iPhone 5.5": Upload all customer/staff screenshots
- iPad Pro 12.9": Upload all customer/staff screenshots

### Feature Graphics:
- **Customer**: Convert `store-assets/customer/feature-graphics/customer-feature-graphic.html` to PNG (1024x500)
- **Staff**: Convert `store-assets/staff/feature-graphics/staff-feature-graphic.html` to PNG (1024x500)

### App Icons:
- Upload 1024x1024 versions of app icons

## Step 12: Select Build and Submit

1. **Select Uploaded Build**
   - In App Store Connect, go to each app
   - Navigate to "App Store" tab
   - Click "+" next to "Build"
   - Select your uploaded build

2. **Complete Required Information**
   - Fill in any missing metadata
   - Complete export compliance questionnaire
   - Add app review information

3. **Submit for Review**
   - Click "Submit for Review"
   - Wait for "Waiting for Review" status

## Step 13: Monitor Review Process

- **Typical Review Time**: 24-48 hours
- **Check Status**: App Store Connect dashboard
- **Respond to Feedback**: Within 7 days if rejected

## Troubleshooting Common Issues

### Build Errors:
- Clean build folder: Product → Clean Build Folder
- Delete derived data: Xcode → Preferences → Locations → Derived Data → Delete
- Restart Xcode

### Code Signing Issues:
- Verify Apple Developer account is active
- Check certificate expiration dates
- Try manual signing if automatic fails

### Upload Failures:
- Check internet connection
- Verify app version/build numbers are unique
- Try uploading during off-peak hours

## Success Criteria ✅

When complete, both apps should show:
- ✅ "Waiting for Review" status in App Store Connect
- ✅ All required metadata and assets uploaded
- ✅ Build versions recorded and documented

## Support Resources

- **Repository**: https://github.com/basitwali1x/arctic-ice-solutions
- **Documentation**: All deployment guides in repository root
- **Apple Developer**: https://developer.apple.com/support/
- **App Store Connect**: https://appstoreconnect.apple.com

---

**Generated**: September 2, 2025
**Status**: Ready for execution on macOS with Xcode
