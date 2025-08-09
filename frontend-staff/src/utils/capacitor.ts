import { Capacitor } from '@capacitor/core';
import { Geolocation } from '@capacitor/geolocation';
import { Camera, CameraResultType, CameraSource } from '@capacitor/camera';
import { PushNotifications } from '@capacitor/push-notifications';
import { StatusBar, Style } from '@capacitor/status-bar';
import { SplashScreen } from '@capacitor/splash-screen';
import { Device } from '@capacitor/device';

export const isNative = () => Capacitor.isNativePlatform();
export const isWeb = () => !Capacitor.isNativePlatform();
export const getPlatform = () => Capacitor.getPlatform();

export const initializeCapacitor = async () => {
  if (isNative()) {
    await StatusBar.setStyle({ style: Style.Dark });
    await StatusBar.setBackgroundColor({ color: '#2563eb' });
    await SplashScreen.hide();
  }
};

export const getCurrentPosition = async () => {
  if (isNative()) {
    const permissions = await Geolocation.checkPermissions();
    if (permissions.location !== 'granted') {
      const requestResult = await Geolocation.requestPermissions();
      if (requestResult.location !== 'granted') {
        throw new Error('Location permission denied');
      }
    }
    return await Geolocation.getCurrentPosition();
  } else {
    return new Promise<GeolocationPosition>((resolve, reject) => {
      if (!navigator.geolocation) {
        reject(new Error('Geolocation not supported'));
        return;
      }
      navigator.geolocation.getCurrentPosition(resolve, reject);
    });
  }
};

export const watchPosition = async (callback: (position: GeolocationPosition) => void) => {
  if (isNative()) {
    const permissions = await Geolocation.checkPermissions();
    if (permissions.location !== 'granted') {
      const requestResult = await Geolocation.requestPermissions();
      if (requestResult.location !== 'granted') {
        throw new Error('Location permission denied');
      }
    }
    return await Geolocation.watchPosition({
      enableHighAccuracy: true,
      timeout: 10000
    }, (position) => {
      if (position) {
        callback(position as GeolocationPosition);
      }
    });
  } else {
    if (!navigator.geolocation) {
      throw new Error('Geolocation not supported');
    }
    return navigator.geolocation.watchPosition(callback, (error) => {
      console.error('GPS Tracking Error:', error);
    }, { enableHighAccuracy: true, maximumAge: 10000, timeout: 5000 });
  }
};

export const clearWatch = async (watchId: string | number) => {
  if (isNative()) {
    await Geolocation.clearWatch({ id: watchId as string });
  } else {
    navigator.geolocation.clearWatch(watchId as number);
  }
};

export const takePhoto = async () => {
  if (isNative()) {
    const permissions = await Camera.checkPermissions();
    if (permissions.camera !== 'granted') {
      const requestResult = await Camera.requestPermissions();
      if (requestResult.camera !== 'granted') {
        throw new Error('Camera permission denied');
      }
    }
    
    const image = await Camera.getPhoto({
      quality: 90,
      allowEditing: false,
      resultType: CameraResultType.DataUrl,
      source: CameraSource.Camera
    });
    
    return image.dataUrl;
  } else {
    return new Promise<string>((resolve, reject) => {
      navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => {
          const video = document.createElement('video');
          video.srcObject = stream;
          video.play();

          const canvas = document.createElement('canvas');
          const context = canvas.getContext('2d');
          
          setTimeout(() => {
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            context?.drawImage(video, 0, 0);
            
            const photoData = canvas.toDataURL('image/jpeg');
            stream.getTracks().forEach(track => track.stop());
            resolve(photoData);
          }, 3000);
        })
        .catch(reject);
    });
  }
};

export const initializePushNotifications = async () => {
  if (isNative()) {
    const permissions = await PushNotifications.checkPermissions();
    if (permissions.receive !== 'granted') {
      const requestResult = await PushNotifications.requestPermissions();
      if (requestResult.receive !== 'granted') {
        throw new Error('Push notification permission denied');
      }
    }
    
    await PushNotifications.register();
    
    PushNotifications.addListener('registration', (token) => {
      console.log('Push registration success, token: ' + token.value);
    });
    
    PushNotifications.addListener('registrationError', (error) => {
      console.error('Error on registration: ' + JSON.stringify(error));
    });
    
    PushNotifications.addListener('pushNotificationReceived', (notification) => {
      console.log('Push notification received: ', notification);
    });
    
    PushNotifications.addListener('pushNotificationActionPerformed', (notification) => {
      console.log('Push notification action performed', notification.actionId, notification.inputValue);
    });
  }
};

export const getDeviceInfo = async () => {
  if (isNative()) {
    return await Device.getInfo();
  } else {
    return {
      platform: 'web',
      operatingSystem: navigator.platform,
      osVersion: navigator.userAgent,
      manufacturer: 'unknown',
      model: 'web',
      isVirtual: false,
      webViewVersion: navigator.userAgent
    };
  }
};

export const getBatteryInfo = async () => {
  if (isNative()) {
    return await Device.getBatteryInfo();
  } else {
    if ('getBattery' in navigator) {
      const battery = await (navigator as unknown as { getBattery: () => Promise<{ level: number; charging: boolean }> }).getBattery();
      return {
        batteryLevel: battery.level,
        isCharging: battery.charging
      };
    }
    return {
      batteryLevel: undefined,
      isCharging: undefined
    };
  }
};
