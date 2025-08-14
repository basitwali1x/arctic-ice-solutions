# Store Assets Creation Guide

## Required Assets for Google Play Console

### 1. Feature Graphic (1024 x 500 pixels)
**Purpose**: Main banner displayed in Play Store
**Requirements**:
- Dimensions: 1024 x 500 pixels
- Format: PNG or JPEG
- File size: Max 1MB
- No text overlay (Google adds app name automatically)

**Design Elements**:
- Arctic Ice Solutions branding
- Professional blue/white color scheme
- Ice/delivery truck imagery
- Clean, modern design

### 2. App Screenshots

#### Phone Screenshots (Required: minimum 2, maximum 8)
**Dimensions**: 
- 16:9 aspect ratio recommended
- Common sizes: 1080 x 1920, 1440 x 2560

**Staff App Screenshots Needed**:
1. **Login Screen**: Show role-based authentication
2. **Work Orders Dashboard**: List of active work orders
3. **Driver Dashboard**: Map with route and delivery status
4. **Vehicle Inspection**: Digital inspection form
5. **Route Optimization**: Map with optimized delivery routes

**Customer App Screenshots Needed**:
1. **Customer Dashboard**: Order history and status
2. **Place Order**: Order placement interface
3. **Delivery Tracking**: Real-time delivery tracking
4. **Invoice Management**: Billing and payment interface

#### Tablet Screenshots (Optional but recommended: minimum 2)
**Dimensions**: 
- 16:10 aspect ratio recommended
- Common sizes: 2560 x 1600, 1920 x 1200

**Content**: 
- Dashboard overview with multiple widgets
- Enhanced interface showing tablet-optimized layouts

### 3. App Icons (Already Available)
**Location**: 
- Staff App: `frontend-staff/public/icon-512.png`
- Customer App: `frontend-customer/public/icon-512.png`

**Requirements**: 512 x 512 pixels, PNG format ✅

## Asset Creation Tools

### Recommended Tools
1. **Figma** (Free) - Web-based design tool
2. **Canva** (Free/Paid) - Template-based design
3. **Adobe Photoshop** (Paid) - Professional design software
4. **GIMP** (Free) - Open-source alternative to Photoshop

### Screenshot Capture
1. **Browser Developer Tools**: 
   - Open app in browser
   - Use device emulation (F12 → Device toolbar)
   - Set to phone/tablet dimensions
   - Capture screenshots

2. **Android Emulator**:
   - Use Android Studio emulator
   - Install APK and capture screenshots
   - Various device sizes available

3. **Physical Device**:
   - Install app on actual devices
   - Use built-in screenshot functionality
   - Transfer images to computer

## Design Guidelines

### Color Scheme
- **Primary**: Arctic blue (#2196F3)
- **Secondary**: Ice white (#FFFFFF)
- **Accent**: Professional gray (#424242)
- **Success**: Green (#4CAF50)
- **Warning**: Orange (#FF9800)

### Typography
- **Headers**: Bold, sans-serif
- **Body**: Regular, readable font
- **UI Elements**: Clean, modern styling

### Branding Elements
- Arctic Ice Solutions logo
- Ice cube imagery
- Delivery truck icons
- Professional business aesthetic

## Screenshot Content Guidelines

### What to Show
- **Key Features**: Highlight main app functionality
- **User Interface**: Clean, professional design
- **Real Data**: Use realistic but anonymized data
- **Clear Navigation**: Show how users interact with app
- **Role-Based Features**: Demonstrate different user roles

### What to Avoid
- **Personal Information**: No real customer data
- **Placeholder Text**: Use realistic content
- **Error States**: Show successful, working features
- **Empty States**: Populate with sample data
- **Poor Quality**: Ensure high-resolution, clear images

## Asset Checklist

### Staff App Assets
- [ ] Feature graphic (1024 x 500)
- [ ] Phone screenshot: Login/Dashboard
- [ ] Phone screenshot: Work Orders
- [ ] Phone screenshot: Driver Dashboard
- [ ] Phone screenshot: Vehicle Inspection
- [ ] Tablet screenshot: Dashboard Overview
- [ ] Tablet screenshot: Route Management

### Customer App Assets
- [ ] Feature graphic (1024 x 500)
- [ ] Phone screenshot: Customer Dashboard
- [ ] Phone screenshot: Place Order
- [ ] Phone screenshot: Delivery Tracking
- [ ] Phone screenshot: Invoice Management
- [ ] Tablet screenshot: Customer Portal
- [ ] Tablet screenshot: Order History

## Upload Instructions

### In Google Play Console
1. Navigate to **Store listing** section
2. Scroll to **Graphics** section
3. Upload **Feature graphic**
4. Upload **Phone screenshots** (drag to reorder)
5. Upload **Tablet screenshots** (optional)
6. Preview how assets appear in store
7. Save changes

### File Naming Convention
- `feature-graphic-staff.png`
- `phone-screenshot-1-login.png`
- `phone-screenshot-2-workorders.png`
- `tablet-screenshot-1-dashboard.png`

## Quality Assurance

### Before Upload
- [ ] Check image dimensions and file sizes
- [ ] Verify no personal/sensitive information visible
- [ ] Ensure high quality and professional appearance
- [ ] Test how images look on different screen sizes
- [ ] Confirm branding consistency across all assets

### After Upload
- [ ] Preview store listing appearance
- [ ] Check asset display on mobile and desktop
- [ ] Verify all images load correctly
- [ ] Confirm proper ordering of screenshots

## Notes
- Screenshots should represent current app functionality
- Update assets when major UI changes are made
- Consider A/B testing different feature graphics
- Monitor store listing performance and optimize assets accordingly
