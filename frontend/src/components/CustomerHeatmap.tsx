import { useState, useEffect, useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { MapPin } from 'lucide-react';
import { Location } from '../types/api';
import { apiRequest } from '../utils/api';

interface CustomerHeatmapProps {
  locations: Location[];
  selectedLocationIds: string[];
}

interface SalesData {
  location_id: string;
  location_name: string;
  sales_volume: number;
  customer_count: number;
  coordinates?: { lat: number; lng: number };
}

export const CustomerHeatmap = ({ selectedLocationIds }: CustomerHeatmapProps) => {
  const [selectedPeriod, setSelectedPeriod] = useState<'daily' | 'weekly' | 'monthly'>('weekly');
  const [salesData, setSalesData] = useState<SalesData[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchSalesData = useMemo(() => async () => {
    if (!selectedLocationIds.length) return;
    
    setLoading(true);
    try {
      const locationIdsParam = selectedLocationIds.join(',');
      const response = await apiRequest(`/api/sales/geo-temporal?period=${selectedPeriod}&location_ids=${locationIdsParam}`);
      if (response?.ok) {
        const data = await response.json();
        setSalesData(data.locations || []);
      }
    } catch (error) {
      console.error('Failed to fetch sales data:', error);
    } finally {
      setLoading(false);
    }
  }, [selectedLocationIds, selectedPeriod]);

  useEffect(() => {
    fetchSalesData();
  }, [fetchSalesData]);

  const maxSalesVolume = useMemo(() => 
    Math.max(...salesData.map(d => d.sales_volume), 1), 
    [salesData]
  );

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Customer Sales Heatmap</CardTitle>
          <Select value={selectedPeriod} onValueChange={(value: 'daily' | 'weekly' | 'monthly') => setSelectedPeriod(value)}>
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="daily">Daily</SelectItem>
              <SelectItem value="weekly">Weekly</SelectItem>
              <SelectItem value="monthly">Monthly</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="text-center py-8">Loading sales data...</div>
        ) : salesData.length > 0 ? (
          <div className="space-y-4">
            {salesData.map((location) => {
              const intensity = (location.sales_volume / maxSalesVolume) * 100;
              const intensityColor = intensity > 75 ? 'bg-red-500' : 
                                    intensity > 50 ? 'bg-orange-500' : 
                                    intensity > 25 ? 'bg-yellow-500' : 'bg-green-500';
              
              return (
                <div key={location.location_id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <MapPin className="h-5 w-5 text-gray-600" />
                    <div>
                      <p className="font-medium">{location.location_name}</p>
                      <p className="text-sm text-gray-600">{location.customer_count} customers</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    <div className="text-right">
                      <p className="font-bold">${location.sales_volume.toLocaleString()}</p>
                      <p className="text-sm text-gray-600">{selectedPeriod} sales</p>
                    </div>
                    <div className={`w-4 h-8 rounded ${intensityColor}`} title={`${intensity.toFixed(1)}% of max volume`} />
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            No sales data available for selected locations and period
          </div>
        )}
      </CardContent>
    </Card>
  );
};
