import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { TrendingUp, Users, Truck, DollarSign } from 'lucide-react';
import { LocationPerformance as LocationPerformanceType, Location } from '../types/api';
import { apiRequest } from '../utils/api';

interface LocationPerformanceProps {
  locations: Location[];
}

export const LocationPerformance: React.FC<LocationPerformanceProps> = ({ locations }) => {
  const [selectedLocationId, setSelectedLocationId] = useState<string>(locations[0]?.id || '');
  const [selectedPeriod, setSelectedPeriod] = useState<'daily' | 'weekly' | 'monthly'>('weekly');
  const [performanceData, setPerformanceData] = useState<LocationPerformanceType | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchPerformanceData = async () => {
      if (!selectedLocationId) return;
      
      setLoading(true);
      try {
        const response = await apiRequest(`/api/performance/locations/${selectedLocationId}?period=${selectedPeriod}`);
        if (response?.ok) {
          const data = await response.json();
          setPerformanceData(data);
        }
      } catch (error) {
        console.error('Failed to fetch performance data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchPerformanceData();
  }, [selectedLocationId, selectedPeriod]);

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Location Performance</CardTitle>
          <div className="flex space-x-2">
            <Select value={selectedLocationId} onValueChange={setSelectedLocationId}>
              <SelectTrigger className="w-40">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {locations.map((location) => (
                  <SelectItem key={location.id} value={location.id}>
                    {location.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
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
        </div>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="text-center py-4">Loading performance data...</div>
        ) : performanceData ? (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="flex items-center space-x-2">
              <DollarSign className="h-8 w-8 text-green-600" />
              <div>
                <p className="text-sm text-gray-600">Sales Volume</p>
                <p className="text-lg font-bold">${performanceData.metrics.sales_volume.toLocaleString()}</p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <Users className="h-8 w-8 text-blue-600" />
              <div>
                <p className="text-sm text-gray-600">Customers</p>
                <p className="text-lg font-bold">{performanceData.metrics.customer_count}</p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <Truck className="h-8 w-8 text-purple-600" />
              <div>
                <p className="text-sm text-gray-600">Vehicles</p>
                <p className="text-lg font-bold">{performanceData.metrics.vehicle_count}</p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <TrendingUp className="h-8 w-8 text-orange-600" />
              <div>
                <p className="text-sm text-gray-600">Efficiency</p>
                <p className="text-lg font-bold">{performanceData.metrics.efficiency.toFixed(1)}%</p>
              </div>
            </div>
          </div>
        ) : (
          <div className="text-center py-4">No performance data available</div>
        )}
      </CardContent>
    </Card>
  );
};
