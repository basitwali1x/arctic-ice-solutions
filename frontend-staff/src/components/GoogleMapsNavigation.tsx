import React, { useCallback, useState, useEffect } from 'react';
import { GoogleMap, DirectionsRenderer, useJsApiLoader } from '@react-google-maps/api';
import { RouteStop } from '../types/api';

interface GoogleMapsNavigationProps {
  stops: RouteStop[];
  currentLocation?: { lat: number; lng: number };
  onDirectionsChange?: (directions: google.maps.DirectionsResult) => void;
}

const containerStyle = {
  width: '100%',
  height: '400px'
};

const center = {
  lat: 31.1391,
  lng: -93.2044
};

const GoogleMapsNavigation: React.FC<GoogleMapsNavigationProps> = ({
  stops,
  currentLocation,
  onDirectionsChange
}) => {
  const { isLoaded } = useJsApiLoader({
    id: 'google-map-script',
    googleMapsApiKey: (import.meta as any).env?.VITE_GOOGLE_MAPS_API_KEY || ''
  });

  const [, setMap] = useState<google.maps.Map | null>(null);
  const [directions, setDirections] = useState<google.maps.DirectionsResult | null>(null);

  const onLoad = useCallback((map: google.maps.Map) => {
    setMap(map);
  }, []);

  const onUnmount = useCallback(() => {
    setMap(null);
  }, []);

  useEffect(() => {
    if (isLoaded && stops.length > 0) {
      const directionsService = new google.maps.DirectionsService();
      
      const origin = currentLocation || center;
      const destination = stops[stops.length - 1].coordinates || { lat: center.lat, lng: center.lng };
      const waypoints = stops.slice(0, -1).map(stop => ({
        location: stop.coordinates || { lat: center.lat, lng: center.lng },
        stopover: true
      }));

      directionsService.route({
        origin,
        destination,
        waypoints,
        travelMode: google.maps.TravelMode.DRIVING,
        optimizeWaypoints: true,
        avoidTolls: true
      }, (result, status) => {
        if (status === 'OK' && result) {
          setDirections(result);
          onDirectionsChange?.(result);
        } else {
          console.error('Directions request failed:', status);
        }
      });
    }
  }, [isLoaded, stops, currentLocation, onDirectionsChange]);

  return isLoaded ? (
    <GoogleMap
      mapContainerStyle={containerStyle}
      center={currentLocation || center}
      zoom={12}
      onLoad={onLoad}
      onUnmount={onUnmount}
    >
      {directions && (
        <DirectionsRenderer
          directions={directions}
          options={{
            suppressMarkers: false,
            polylineOptions: {
              strokeColor: '#2563eb',
              strokeWeight: 4
            }
          }}
        />
      )}
    </GoogleMap>
  ) : <div>Loading map...</div>;
};

export default GoogleMapsNavigation;
