import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Switch } from '../../components/ui/switch';
import { Label } from '../../components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../components/ui/select';
import { Input } from '../../components/ui/input';
import { Bell, MapPin, Bluetooth, Smartphone, Database, Shield } from 'lucide-react';

export function MobileSettings() {
  const [settings, setSettings] = useState({
    notifications: {
      push_enabled: true,
      work_orders: true,
      route_updates: true,
      system_alerts: true,
      sound_enabled: true
    },
    gps: {
      tracking_enabled: true,
      high_accuracy: true,
      background_tracking: false,
      geofencing_alerts: true
    },
    printer: {
      auto_connect: false,
      default_printer: '',
      receipt_copies: 1
    },
    app: {
      theme: 'light',
      language: 'en',
      auto_sync: true,
      offline_mode: true,
      cache_duration: 24
    },
    security: {
      auto_logout: 30,
      require_pin: false,
      biometric_auth: false
    }
  });

  const updateSetting = (category: string, key: string, value: any) => {
    setSettings(prev => ({
      ...prev,
      [category]: {
        ...prev[category as keyof typeof prev],
        [key]: value
      }
    }));
  };

  const saveSettings = () => {
    localStorage.setItem('arctic_ice_mobile_settings', JSON.stringify(settings));
    alert('Settings saved successfully!');
  };

  const resetSettings = () => {
    if (confirm('Are you sure you want to reset all settings to default?')) {
      localStorage.removeItem('arctic_ice_mobile_settings');
      window.location.reload();
    }
  };

  const clearCache = () => {
    if (confirm('Clear all cached data? This will require re-downloading data on next sync.')) {
      localStorage.clear();
      alert('Cache cleared successfully!');
    }
  };

  return (
    <div className="p-4 space-y-4">
      <div>
        <h2 className="text-xl font-bold text-gray-900 mb-4">Settings</h2>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Bell className="h-5 w-5 mr-2" />
            Notifications
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <Label htmlFor="push-notifications">Push Notifications</Label>
            <Switch
              id="push-notifications"
              checked={settings.notifications.push_enabled}
              onCheckedChange={(checked) => updateSetting('notifications', 'push_enabled', checked)}
            />
          </div>
          <div className="flex items-center justify-between">
            <Label htmlFor="work-order-notifications">Work Order Updates</Label>
            <Switch
              id="work-order-notifications"
              checked={settings.notifications.work_orders}
              onCheckedChange={(checked) => updateSetting('notifications', 'work_orders', checked)}
            />
          </div>
          <div className="flex items-center justify-between">
            <Label htmlFor="route-notifications">Route Updates</Label>
            <Switch
              id="route-notifications"
              checked={settings.notifications.route_updates}
              onCheckedChange={(checked) => updateSetting('notifications', 'route_updates', checked)}
            />
          </div>
          <div className="flex items-center justify-between">
            <Label htmlFor="system-notifications">System Alerts</Label>
            <Switch
              id="system-notifications"
              checked={settings.notifications.system_alerts}
              onCheckedChange={(checked) => updateSetting('notifications', 'system_alerts', checked)}
            />
          </div>
          <div className="flex items-center justify-between">
            <Label htmlFor="sound-notifications">Sound Enabled</Label>
            <Switch
              id="sound-notifications"
              checked={settings.notifications.sound_enabled}
              onCheckedChange={(checked) => updateSetting('notifications', 'sound_enabled', checked)}
            />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <MapPin className="h-5 w-5 mr-2" />
            GPS & Location
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <Label htmlFor="gps-tracking">GPS Tracking</Label>
            <Switch
              id="gps-tracking"
              checked={settings.gps.tracking_enabled}
              onCheckedChange={(checked) => updateSetting('gps', 'tracking_enabled', checked)}
            />
          </div>
          <div className="flex items-center justify-between">
            <Label htmlFor="high-accuracy">High Accuracy Mode</Label>
            <Switch
              id="high-accuracy"
              checked={settings.gps.high_accuracy}
              onCheckedChange={(checked) => updateSetting('gps', 'high_accuracy', checked)}
            />
          </div>
          <div className="flex items-center justify-between">
            <Label htmlFor="background-tracking">Background Tracking</Label>
            <Switch
              id="background-tracking"
              checked={settings.gps.background_tracking}
              onCheckedChange={(checked) => updateSetting('gps', 'background_tracking', checked)}
            />
          </div>
          <div className="flex items-center justify-between">
            <Label htmlFor="geofencing">Geofencing Alerts</Label>
            <Switch
              id="geofencing"
              checked={settings.gps.geofencing_alerts}
              onCheckedChange={(checked) => updateSetting('gps', 'geofencing_alerts', checked)}
            />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Bluetooth className="h-5 w-5 mr-2" />
            Printer Settings
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <Label htmlFor="auto-connect-printer">Auto-Connect to Printer</Label>
            <Switch
              id="auto-connect-printer"
              checked={settings.printer.auto_connect}
              onCheckedChange={(checked) => updateSetting('printer', 'auto_connect', checked)}
            />
          </div>
          <div>
            <Label htmlFor="default-printer">Default Printer</Label>
            <Select 
              value={settings.printer.default_printer} 
              onValueChange={(value) => updateSetting('printer', 'default_printer', value)}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select default printer" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="zebra-zq320">Zebra ZQ320</SelectItem>
                <SelectItem value="star-sm-l200">Star SM-L200</SelectItem>
                <SelectItem value="epson-tm-p20">Epson TM-P20</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label htmlFor="receipt-copies">Receipt Copies</Label>
            <Input
              id="receipt-copies"
              type="number"
              min="1"
              max="3"
              value={settings.printer.receipt_copies}
              onChange={(e) => updateSetting('printer', 'receipt_copies', parseInt(e.target.value))}
            />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Smartphone className="h-5 w-5 mr-2" />
            App Preferences
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label htmlFor="theme">Theme</Label>
            <Select 
              value={settings.app.theme} 
              onValueChange={(value) => updateSetting('app', 'theme', value)}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="light">Light</SelectItem>
                <SelectItem value="dark">Dark</SelectItem>
                <SelectItem value="auto">Auto</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label htmlFor="language">Language</Label>
            <Select 
              value={settings.app.language} 
              onValueChange={(value) => updateSetting('app', 'language', value)}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="en">English</SelectItem>
                <SelectItem value="es">Español</SelectItem>
                <SelectItem value="fr">Français</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="flex items-center justify-between">
            <Label htmlFor="auto-sync">Auto Sync</Label>
            <Switch
              id="auto-sync"
              checked={settings.app.auto_sync}
              onCheckedChange={(checked) => updateSetting('app', 'auto_sync', checked)}
            />
          </div>
          <div className="flex items-center justify-between">
            <Label htmlFor="offline-mode">Offline Mode</Label>
            <Switch
              id="offline-mode"
              checked={settings.app.offline_mode}
              onCheckedChange={(checked) => updateSetting('app', 'offline_mode', checked)}
            />
          </div>
          <div>
            <Label htmlFor="cache-duration">Cache Duration (hours)</Label>
            <Input
              id="cache-duration"
              type="number"
              min="1"
              max="168"
              value={settings.app.cache_duration}
              onChange={(e) => updateSetting('app', 'cache_duration', parseInt(e.target.value))}
            />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Shield className="h-5 w-5 mr-2" />
            Security
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label htmlFor="auto-logout">Auto Logout (minutes)</Label>
            <Input
              id="auto-logout"
              type="number"
              min="5"
              max="120"
              value={settings.security.auto_logout}
              onChange={(e) => updateSetting('security', 'auto_logout', parseInt(e.target.value))}
            />
          </div>
          <div className="flex items-center justify-between">
            <Label htmlFor="require-pin">Require PIN</Label>
            <Switch
              id="require-pin"
              checked={settings.security.require_pin}
              onCheckedChange={(checked) => updateSetting('security', 'require_pin', checked)}
            />
          </div>
          <div className="flex items-center justify-between">
            <Label htmlFor="biometric-auth">Biometric Authentication</Label>
            <Switch
              id="biometric-auth"
              checked={settings.security.biometric_auth}
              onCheckedChange={(checked) => updateSetting('security', 'biometric_auth', checked)}
            />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Database className="h-5 w-5 mr-2" />
            Data Management
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex space-x-2">
            <Button onClick={saveSettings} className="flex-1">
              Save Settings
            </Button>
            <Button variant="outline" onClick={clearCache}>
              Clear Cache
            </Button>
          </div>
          <Button variant="destructive" onClick={resetSettings} className="w-full">
            Reset to Defaults
          </Button>
        </CardContent>
      </Card>

      <div className="text-center text-xs text-gray-500 pt-4">
        Arctic Ice Solutions Mobile App v1.0
      </div>
    </div>
  );
}
