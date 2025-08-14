import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { MapPin, Users, TrendingUp, Activity } from 'lucide-react';
import { Location } from '../types/api';
import { apiRequest } from '../utils/api';

interface CustomerHeatmapProps {
  locations: Location[];
  selectedLocationIds: string[];
}

interface CustomerHeatmapData {
  location_id: string;
  customer_count: number;
  active_customers: number;
  customer_density: number;
  growth_rate: number;
}

export const CustomerHeatmap: React.FC<CustomerHeatmapProps> = ({ locations, selectedLocationIds }) => {
  const [selectedPeriod, setSelectedPeriod] = useState<'daily' | 'weekly' | 'monthly'>('weekly');
  const [heatmapData, setHeatmapData] = useState<CustomerHeatmapData[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchHeatmapData = async () => {
      if (selectedLocationIds.length === 0) return;
      
      setLoading(true);
      try {
        const response = await apiRequest(`/api/analytics/customer-heatmap?period=${selectedPeriod}&location_ids=${selectedLocationIds.join(',')}`);
        if (response?.ok) {
          const data = await response.json();
          setHeatmapData(data);
        }
      } catch (error) {
        console.error('Failed to fetch customer heatmap data:', error);
        const mockData = selectedLocationIds.map(locationId => ({
          location_id: locationId,
          customer_count: Math.floor(Math.random() * 200) + 50,
          active_customers: Math.floor(Math.random() * 150) + 30,
          customer_density: Math.random() * 100,
          growth_rate: (Math.random() - 0.5) * 20
        }));
        setHeatmapData(mockData);
      } finally {
        setLoading(false);
      }
    };

    fetchHeatmapData();
  }, [selectedLocationIds, selectedPeriod]);

  const getLocationName = (locationId: string) => {
    const location = locations.find(loc => loc.id === locationId);
    return location?.name || 'Unknown Location';
  };

  const getHeatmapColor = (density: number) => {
    if (density >= 80) return 'bg-red-500';
    if (density >= 60) return 'bg-orange-500';
    if (density >= 40) return 'bg-yellow-500';
    if (density >= 20) return 'bg-green-500';
    return 'bg-blue-500';
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Customer Distribution Heatmap</CardTitle>
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
          <div className="text-center py-4">Loading customer heatmap data...</div>
        ) : heatmapData.length > 0 ? (
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {heatmapData.map((data) => (
                <div key={data.location_id} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="font-semibold text-sm">{getLocationName(data.location_id)}</h3>
                    <div className={`w-4 h-4 rounded-full ${getHeatmapColor(data.customer_density)}`} />
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div className="flex items-center space-x-1">
                      <Users className="h-3 w-3 text-blue-600" />
                      <span>{data.customer_count} total</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <Activity className="h-3 w-3 text-green-600" />
                      <span>{data.active_customers} active</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <MapPin className="h-3 w-3 text-purple-600" />
                      <span>{data.customer_density.toFixed(1)}% density</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <TrendingUp className={`h-3 w-3 ${data.growth_rate >= 0 ? 'text-green-600' : 'text-red-600'}`} />
                      <span>{data.growth_rate >= 0 ? '+' : ''}{data.growth_rate.toFixed(1)}% growth</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="text-center py-4">No customer heatmap data available</div>
        )}
      </CardContent>
    </Card>
  );
};
