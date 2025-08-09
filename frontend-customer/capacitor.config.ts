import { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.arcticeicesolutions.customer',
  appName: 'Arctic Ice Customer',
  webDir: 'dist',
  server: {
    androidScheme: 'https'
  },
  plugins: {
    SplashScreen: {
      launchShowDuration: 2000,
      launchAutoHide: true,
      backgroundColor: "#2563eb",
      androidSplashResourceName: "splash",
      androidScaleType: "CENTER_CROP",
      showSpinner: false,
      androidSpinnerStyle: "large",
      iosSpinnerStyle: "small",
      spinnerColor: "#ffffff",
      splashFullScreen: true,
      splashImmersive: true,
      layoutName: "launch_screen",
      useDialog: true,
    },
    StatusBar: {
      style: 'DARK',
      backgroundColor: '#2563eb'
    },
    PushNotifications: {
      presentationOptions: ["badge", "sound", "alert"]
    },
    Geolocation: {
      permissions: {
        location: "always"
      }
    },
    Camera: {
      permissions: {
        camera: true,
        photos: "add-only"
      }
    }
  },
  ios: {
    scheme: 'Arctic Ice Customer'
  },
  android: {
    allowMixedContent: true
  }
};

export default config;
