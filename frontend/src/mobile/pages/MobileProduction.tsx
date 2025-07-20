import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { TrendingUp, Factory, Plus } from 'lucide-react';
import { API_BASE_URL } from '../../lib/constants';

interface ProductionData {
  daily_production_pallets: number;
  target_production_pallets: number;
  production_efficiency: number;
  shift_1_pallets: number;
  shift_2_pallets: number;
}

export function MobileProduction() {
  const [productionData, setProductionData] = useState<ProductionData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchProductionData();
  }, []);

  const fetchProductionData = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/dashboard/production`);
      if (response.ok) {
        const data = await response.json();
        setProductionData(data);
      }
    } catch (error) {
      console.error('Error fetching production data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="p-4 space-y-4">
        <div className="animate-pulse space-y-4">
          <div className="h-24 bg-gray-200 rounded-lg"></div>
          <div className="h-24 bg-gray-200 rounded-lg"></div>
        </div>
      </div>
    );
  }

  const dailyProgress = productionData 
    ? (productionData.daily_production_pallets / productionData.target_production_pallets) * 100 
    : 0;

  return (
    <div className="p-4 space-y-4">
      <div>
        <h2 className="text-xl font-bold text-gray-900 mb-4">Production</h2>
      </div>

      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center space-x-2">
            <Factory className="h-5 w-5 text-blue-600" />
            <span>Daily Production</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-600">
              {productionData?.daily_production_pallets || 0}
            </div>
            <div className="text-sm text-gray-500 mb-3">
              of {productionData?.target_production_pallets || 0} pallets
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div 
                className="bg-blue-600 h-3 rounded-full transition-all duration-300" 
                style={{ width: `${Math.min(dailyProgress, 100)}%` }}
              ></div>
            </div>
            <div className="text-xs text-gray-500 mt-1">
              {dailyProgress.toFixed(1)}% Complete
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-2 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Shift 1</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {productionData?.shift_1_pallets || 0}
            </div>
            <div className="text-xs text-gray-500">pallets</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Shift 2</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">
              {productionData?.shift_2_pallets || 0}
            </div>
            <div className="text-xs text-gray-500">pallets</div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center space-x-2">
            <TrendingUp className="h-5 w-5 text-green-600" />
            <span>Efficiency</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">
              {productionData?.production_efficiency || 0}%
            </div>
            <div className="text-sm text-gray-500">Production Efficiency</div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base">Quick Actions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <Button className="w-full" size="sm">
              <Plus className="h-4 w-4 mr-2" />
              Submit Production Data
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
