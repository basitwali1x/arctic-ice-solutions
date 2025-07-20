import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';
import { Package, AlertTriangle, CheckCircle } from 'lucide-react';
import { API_BASE_URL } from '../../lib/constants';

interface InventoryData {
  inventory_levels: {
    '8lb_bags': number;
    '20lb_bags': number;
    'block_ice': number;
  };
}

export function MobileInventory() {
  const [inventoryData, setInventoryData] = useState<InventoryData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchInventoryData();
  }, []);

  const fetchInventoryData = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/dashboard/production`);
      if (response.ok) {
        const data = await response.json();
        setInventoryData(data);
      }
    } catch (error) {
      console.error('Error fetching inventory data:', error);
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

  const inventoryItems = [
    { 
      name: '8lb Bags', 
      current: inventoryData?.inventory_levels?.['8lb_bags'] || 0, 
      target: 1500,
      icon: Package 
    },
    { 
      name: '20lb Bags', 
      current: inventoryData?.inventory_levels?.['20lb_bags'] || 0, 
      target: 1000,
      icon: Package 
    },
    { 
      name: 'Block Ice', 
      current: inventoryData?.inventory_levels?.['block_ice'] || 0, 
      target: 200,
      icon: Package 
    }
  ];

  return (
    <div className="p-4 space-y-4">
      <div>
        <h2 className="text-xl font-bold text-gray-900 mb-4">Inventory</h2>
      </div>

      {inventoryItems.map((item) => {
        const percentage = (item.current / item.target) * 100;
        const isLow = percentage < 25;
        const isGood = percentage >= 75;
        
        return (
          <Card key={item.name}>
            <CardHeader className="pb-3">
              <CardTitle className="text-base flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <item.icon className="h-5 w-5 text-blue-600" />
                  <span>{item.name}</span>
                </div>
                {isLow ? (
                  <AlertTriangle className="h-5 w-5 text-red-500" />
                ) : isGood ? (
                  <CheckCircle className="h-5 w-5 text-green-500" />
                ) : null}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-2xl font-bold">{item.current}</span>
                  <Badge variant={isLow ? "destructive" : isGood ? "default" : "secondary"}>
                    {percentage.toFixed(0)}%
                  </Badge>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full transition-all duration-300 ${
                      isLow ? 'bg-red-500' : isGood ? 'bg-green-500' : 'bg-yellow-500'
                    }`}
                    style={{ width: `${Math.min(percentage, 100)}%` }}
                  ></div>
                </div>
                <div className="text-sm text-gray-500">
                  Target: {item.target} units
                </div>
              </div>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}
