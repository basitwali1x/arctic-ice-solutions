import React, { useState, useEffect, useCallback } from 'react';
import { GoogleMap, HeatmapLayer, useJsApiLoader } from '@react-google-maps/api';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { GeoTemporalSales, TimePeriod, Location } from '../types/api';
import { apiRequest } from '../utils/api';

interface CustomerHeatmapProps {
  locations: Location[];
  selectedLocationIds?: string[];
}

const libraries: ("visualization")[] = ["visualization"];

const containerStyle = {
  width: '100%',
  height: '500px'
};

const center = {
  lat: 31.1391,
  lng: -93.2044
};

const timePeriods: TimePeriod[] = [
  { value: 'daily', label: 'Daily Sales' },
  { value: 'weekly', label: 'Weekly Sales' },
  { value: 'monthly', label: 'Monthly Sales' }
];

export const CustomerHeatmap: React.FC<CustomerHeatmapProps> = ({
  selectedLocationIds
}) => {
  const googleMapsApiKey = (import.meta as any).env?.VITE_GOOGLE_MAPS_API_KEY || '';
  const { isLoaded } = useJsApiLoader({
    id: 'google-map-script',
    googleMapsApiKey,
    libraries
  });

  const [selectedPeriod, setSelectedPeriod] = useState<'daily' | 'weekly' | 'monthly'>('weekly');
  const [loading, setLoading] = useState(false);
  const [heatmapData, setHeatmapData] = useState<google.maps.visualization.WeightedLocation[]>([]);

  const fetchSalesData = useCallback(async () => {
    if (!isLoaded) return;
    
    setLoading(true);
    try {
      const locationParam = selectedLocationIds?.join(',') || '';
      const response = await apiRequest(`/api/sales/geo-temporal?period=${selectedPeriod}&location_ids=${locationParam}`);
      
      if (response?.ok) {
        const data = await response.json();
        
        const heatmapPoints = data.sales.map((sale: GeoTemporalSales) => ({
          location: new google.maps.LatLng(sale.coordinates.lat, sale.coordinates.lng),
          weight: Math.max(1, sale.sales_amount / 1000)
        }));
        
        setHeatmapData(heatmapPoints);
      }
    } catch (error) {
      console.error('Failed to fetch sales data:', error);
    } finally {
      setLoading(false);
    }
  }, [isLoaded, selectedPeriod, selectedLocationIds]);

  useEffect(() => {
    fetchSalesData();
  }, [fetchSalesData]);

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Customer Sales Heatmap</CardTitle>
          <Select value={selectedPeriod} onValueChange={(value: 'daily' | 'weekly' | 'monthly') => setSelectedPeriod(value)}>
            <SelectTrigger className="w-40">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {timePeriods.map((period) => (
                <SelectItem key={period.value} value={period.value}>
                  {period.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </CardHeader>
      <CardContent>
        {loading && <div className="text-center py-4">Loading sales data...</div>}
        {!googleMapsApiKey ? (
          <div className="text-center py-8 bg-gray-50 rounded-lg">
            <p className="text-gray-600 mb-2">Google Maps API key required for heatmap visualization</p>
            <p className="text-sm text-gray-500">Add VITE_GOOGLE_MAPS_API_KEY to .env.local to enable maps</p>
          </div>
        ) : isLoaded ? (
          <GoogleMap
            mapContainerStyle={containerStyle}
            center={center}
            zoom={10}
          >
            {heatmapData.length > 0 && (
              <HeatmapLayer
                data={heatmapData}
                options={{
                  radius: 20,
                  opacity: 0.6,
                  gradient: [
                    'rgba(0, 255, 255, 0)',
                    'rgba(0, 255, 255, 1)',
                    'rgba(0, 191, 255, 1)',
                    'rgba(0, 127, 255, 1)',
                    'rgba(0, 63, 255, 1)',
                    'rgba(0, 0, 255, 1)',
                    'rgba(0, 0, 223, 1)',
                    'rgba(0, 0, 191, 1)',
                    'rgba(0, 0, 159, 1)',
                    'rgba(0, 0, 127, 1)',
                    'rgba(63, 0, 91, 1)',
                    'rgba(127, 0, 63, 1)',
                    'rgba(191, 0, 31, 1)',
                    'rgba(255, 0, 0, 1)'
                  ]
                }}
              />
            )}
          </GoogleMap>
        ) : (
          <div className="text-center py-4">Loading map...</div>
        )}
      </CardContent>
    </Card>
  );
};
