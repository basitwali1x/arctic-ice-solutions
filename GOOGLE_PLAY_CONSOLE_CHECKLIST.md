# Google Play Console Setup Checklist

## Overview
This checklist covers all remaining Google Play Console setup tasks for both Arctic Ice Solutions mobile apps.

## App Information
- **Customer App**: `com.arcticeicesolutions.customer` (Arctic Ice Customer)
- **Staff App**: `com.arcticeicesolutions.staff` (Arctic Ice Staff)
- **Privacy Policy URL**: https://arcticicesolutions.com/privacy-policy

## Customer App Status
✅ **SUBMITTED FOR REVIEW** - Monitor status and respond to any reviewer feedback

### Monitoring Tasks
- [ ] Check review status daily in Play Console dashboard
- [ ] Respond to any reviewer questions or feedback within 7 days
- [ ] Prepare for production release once approved

## Staff App - Complete Setup Required

### 1. Store Listing Requirements
- [ ] **App Name**: Arctic Ice Staff
- [ ] **Short Description**: Staff app for Arctic Ice Solutions field operations
- [ ] **Full Description**: 
  ```
  Arctic Ice Staff is the official mobile application for Arctic Ice Solutions field personnel. Designed specifically for managers, dispatchers, drivers, and technicians to streamline field operations, work order management, and route optimization.

  Key Features:
  • Work Order Management - Create, assign, and track maintenance requests
  • Route Optimization - AI-powered delivery route planning and navigation
  • Driver Dashboard - Real-time vehicle tracking and delivery status
  • Vehicle Inspections - Digital inspection forms and photo documentation
  • Field Operations - Mobile access to customer data and order information
  • Role-Based Access - Customized features based on staff role (Manager, Dispatcher, Driver, Technician)

  This app requires staff credentials and is restricted to authorized Arctic Ice Solutions personnel only.
  ```
- [ ] **Category**: Business
- [ ] **Tags**: field operations, work orders, route management, delivery tracking, business management

### 2. Graphics and Assets
- [ ] **App Icon**: Upload 512x512 PNG (available at `frontend-staff/public/icon-512.png`)
- [ ] **Feature Graphic**: Create 1024x500 banner image
- [ ] **Screenshots**: Upload phone and tablet screenshots (minimum 2, maximum 8)
  - Phone screenshots: 16:9 aspect ratio
  - Tablet screenshots: 16:10 aspect ratio
  - Show key features: work orders, driver dashboard, route management

### 3. Store Settings
- [ ] **App Category**: Business
- [ ] **Content Rating**: Complete questionnaire
  - Target Age Group: 18+ (business app)
  - Violence: None
  - Sexual Content: None
  - Profanity: None
  - Drugs/Alcohol: None
  - Gambling: None
  - User-Generated Content: None
- [ ] **Target Audience**: Adults (18+)
- [ ] **Ads**: No ads present

### 4. Privacy and Data Safety
- [ ] **Privacy Policy URL**: https://arcticicesolutions.com/privacy-policy
- [ ] **Data Safety Section**: Complete data collection disclosure
  - **Data Collected**:
    - Personal Info: Name, email address, phone number
    - Location: Precise location (for GPS tracking during deliveries)
    - App Activity: App interactions and in-app search history
    - Device Info: Device identifiers
  - **Data Usage**:
    - App functionality (account management, order processing)
    - Analytics (app performance monitoring)
    - Communication (customer support, notifications)
  - **Data Sharing**: No data shared with third parties
  - **Security**: Data encrypted in transit and at rest

### 5. App Content
- [ ] **Target Audience**: Business professionals
- [ ] **Content Guidelines**: Complies with Google Play policies
- [ ] **Restricted Content**: None

### 6. Testing and Release
- [ ] **Internal Testing**: Currently active (Release 1.0)
- [ ] **Closed Testing**: Set up track for broader staff testing
  - Add test users: Arctic Ice Solutions staff emails
  - Testing instructions: "Test all role-based features for your assigned role"
- [ ] **Pre-launch Report**: Review and address any issues
- [ ] **Release Notes**: 
  ```
  Initial release of Arctic Ice Staff mobile app featuring:
  - Work order management system
  - Route optimization and navigation
  - Driver dashboard with real-time tracking
  - Vehicle inspection tools
  - Role-based access control
  ```

### 7. App Signing
- [ ] **App Signing**: Google Play App Signing enabled
- [ ] **Upload Key**: Configured via CI/CD (keystore already set up)

### 8. Pricing and Distribution
- [ ] **Price**: Free
- [ ] **Countries**: United States (Louisiana, Texas regions)
- [ ] **Device Categories**: Phone and Tablet
- [ ] **Android Version**: API 21+ (Android 5.0+)

## Required Assets to Create

### Feature Graphic (1024x500)
Create a banner image featuring:
- Arctic Ice Solutions branding
- "Staff App" text
- Key feature icons (work orders, routes, dashboard)
- Professional blue/white color scheme

### Screenshots Needed
**Phone Screenshots (minimum 4):**
1. Login screen with staff role selection
2. Work orders list with status indicators
3. Driver dashboard with map and route
4. Vehicle inspection form

**Tablet Screenshots (minimum 2):**
1. Dashboard overview with multiple widgets
2. Route optimization interface with map

## Content Rating Questionnaire Answers
- **Violence**: None
- **Blood**: None
- **Sexual Content**: None
- **Nudity**: None
- **Profanity**: None
- **Crude Humor**: None
- **Drug/Alcohol/Tobacco**: None
- **Gambling**: None
- **Illegal Activities**: None
- **User-Generated Content**: None
- **Location Sharing**: Yes (for GPS tracking during deliveries)
- **Personal Information**: Yes (staff credentials and work data)

## Data Safety Declarations

### Data Types Collected
1. **Personal Info**
   - Name ✓
   - Email address ✓
   - Phone number ✓
   - User IDs ✓

2. **Location**
   - Approximate location ✓
   - Precise location ✓

3. **App Activity**
   - App interactions ✓
   - In-app search history ✓

4. **Device or Other IDs**
   - Device or other IDs ✓

### Data Usage Purposes
- **App functionality** (Required)
- **Analytics** (Optional)
- **Developer communications** (Optional)

### Data Sharing
- **No data shared with third parties**

### Security Practices
- **Data encrypted in transit** ✓
- **Data encrypted at rest** ✓
- **Users can request data deletion** ✓

## Submission Checklist
Before submitting Staff App for review:
- [ ] All store listing fields completed
- [ ] All required graphics uploaded
- [ ] Content rating questionnaire completed
- [ ] Data safety section completed
- [ ] Privacy policy accessible at provided URL
- [ ] Internal testing completed successfully
- [ ] App complies with Google Play policies

## Post-Submission
- [ ] Monitor review status (typically 1-3 days)
- [ ] Respond to any reviewer feedback
- [ ] Plan production release strategy
- [ ] Set up app update process via CI/CD

## Support Information
- **Developer Contact**: Arctic Ice Solutions
- **Support Email**: support@arcticicesolutions.com
- **Website**: https://arcticicesolutions.com
- **Privacy Policy**: https://arcticicesolutions.com/privacy-policy

## Notes
- Both apps use automated deployment via GitHub Actions
- Keystore and signing configured in CI/CD pipeline
- Apps are restricted to authorized users only (staff vs customer roles)
- Location permissions required for delivery tracking functionality
