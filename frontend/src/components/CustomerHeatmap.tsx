import React, { useState, useEffect, useCallback, useMemo } from 'react';
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
  const googleMapsApiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY;
  const { isLoaded, loadError } = useJsApiLoader({
    id: 'google-map-script',
    googleMapsApiKey,
    libraries
  });

  console.log('CustomerHeatmap - API Key loaded from environment');
  console.log('CustomerHeatmap - isLoaded:', isLoaded);
  console.log('CustomerHeatmap - loadError:', loadError);

  const [selectedPeriod, setSelectedPeriod] = useState<'daily' | 'weekly' | 'monthly'>('weekly');
  const [loading, setLoading] = useState(false);
  const [heatmapData, setHeatmapData] = useState<google.maps.visualization.WeightedLocation[]>([]);

  const fetchSalesData = useCallback(async () => {
    if (!isLoaded || !window.google) return;
    
    setLoading(true);
    try {
      const locationParam = selectedLocationIds?.join(',') || 'loc_1,loc_2,loc_3,loc_4';
      const response = await apiRequest(`/api/sales/geo-temporal?period=${selectedPeriod}&location_ids=${locationParam}`);
      
      if (response?.ok) {
        const data = await response.json();
        
        const heatmapPoints = data.sales?.map((sale: GeoTemporalSales) => ({
          location: new google.maps.LatLng(sale.coordinates.lat, sale.coordinates.lng),
          weight: Math.max(1, sale.sales_amount / 1000)
        })) || [];
        
        setHeatmapData(heatmapPoints);
      }
    } catch (error) {
      console.error('Failed to fetch sales data:', error);
    } finally {
      setLoading(false);
    }
  }, [isLoaded, selectedPeriod, selectedLocationIds]);

  const memoizedHeatmapData = useMemo(() => heatmapData, [heatmapData]);

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
        {loadError ? (
          <div className="text-center py-8 bg-red-50 rounded-lg">
            <p className="text-red-600 mb-2">Google Maps failed to load</p>
            <p className="text-sm text-red-500">Error: {loadError.message}</p>
          </div>
        ) : isLoaded ? (
          <div className="heatmap-container" style={{ 
            minHeight: '500px', 
            background: '#f5f5f5',
            willChange: 'transform'
          }}>
            <GoogleMap
              mapContainerStyle={containerStyle}
              center={center}
              zoom={10}
              options={{
                styles: [
                  {
                    featureType: 'all',
                    elementType: 'geometry',
                    stylers: [{ color: '#f5f5f5' }]
                  }
                ]
              }}
            >
              {memoizedHeatmapData.length > 0 && (
                <HeatmapLayer
                  data={memoizedHeatmapData}
                  options={{
                    radius: 20,
                    opacity: 0.6,
                    gradient: [
                      'rgba(102, 255, 0, 0)',
                      'rgba(102, 255, 0, 1)',
                      'rgba(255, 255, 0, 1)',
                      'rgba(255, 140, 0, 1)',
                      'rgba(255, 0, 0, 1)'
                    ]
                  }}
                />
              )}
            </GoogleMap>
          </div>
        ) : (
          <div className="text-center py-4 bg-gray-50 rounded-lg" style={{ 
            minHeight: '500px', 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center',
            willChange: 'transform'
          }}>
            <div>Loading Google Maps...</div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};
