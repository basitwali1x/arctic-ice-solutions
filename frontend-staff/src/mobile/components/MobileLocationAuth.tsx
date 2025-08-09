import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { MapPin, Loader2, AlertTriangle } from 'lucide-react';

interface MobileLocationAuthProps {
  onLocationVerified: () => void;
}

export function MobileLocationAuth({ onLocationVerified }: MobileLocationAuthProps) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [location, setLocation] = useState<{ lat: number; lng: number } | null>(null);

  useEffect(() => {
    verifyLocation();
  }, []);

  const verifyLocation = () => {
    setLoading(true);
    setError(null);

    if (!navigator.geolocation) {
      setError('GPS not supported on this device');
      setLoading(false);
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const currentLocation = {
          lat: position.coords.latitude,
          lng: position.coords.longitude
        };
        setLocation(currentLocation);
        
        setLoading(false);
        onLocationVerified();
      },
      (error) => {
        console.error('GPS Error:', error);
        setError('Unable to verify location. Please enable GPS and try again.');
        setLoading(false);
      },
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 60000 }
    );
  };

  const skipLocationVerification = () => {
    setLocation({ lat: 30.6118, lng: -93.0862 }); // Default to Leesville, LA
    setLoading(false);
    onLocationVerified();
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <MapPin className="h-5 w-5 text-blue-600" />
            <span>Location Verification</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {loading && (
            <div className="text-center">
              <Loader2 className="h-8 w-8 animate-spin mx-auto mb-2 text-blue-600" />
              <p className="text-sm text-gray-600">Verifying your location...</p>
            </div>
          )}
          
          {error && (
            <div className="text-center">
              <AlertTriangle className="h-8 w-8 mx-auto mb-2 text-red-500" />
              <p className="text-sm text-red-600 mb-4">{error}</p>
              <div className="space-y-2">
                <Button onClick={verifyLocation} className="w-full">
                  Try Again
                </Button>
                <Button onClick={skipLocationVerification} variant="outline" className="w-full">
                  Skip for Testing
                </Button>
              </div>
            </div>
          )}
          
          {location && !loading && (
            <div className="text-center">
              <MapPin className="h-8 w-8 mx-auto mb-2 text-green-500" />
              <p className="text-sm text-green-600">Location verified successfully!</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
