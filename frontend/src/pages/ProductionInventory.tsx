import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Package, TrendingUp, AlertTriangle, Plus, RefreshCw } from 'lucide-react';
import { Product, ProductionDashboard } from '../types/api';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://app-jswjngwy.fly.dev';

export function ProductionInventory() {
  const [products, setProducts] = useState<Product[]>([]);
  const [productionData, setProductionData] = useState<ProductionDashboard | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [productsRes, productionRes] = await Promise.all([
          fetch(`${API_BASE_URL}/api/products`),
          fetch(`${API_BASE_URL}/api/dashboard/production`)
        ]);

        const productsData = await productsRes.json();
        const productionDataRes = await productionRes.json();

        setProducts(productsData);
        setProductionData(productionDataRes);
      } catch (error) {
        console.error('Failed to fetch data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const inventoryData = productionData ? [
    { name: '8lb Bags', current: productionData.inventory_levels['8lb_bags'], target: 1500 },
    { name: '20lb Bags', current: productionData.inventory_levels['20lb_bags'], target: 1000 },
    { name: 'Block Ice', current: productionData.inventory_levels['block_ice'], target: 200 }
  ] : [];

  const productionTrend = [
    { day: 'Mon', pallets: 75 },
    { day: 'Tue', pallets: 82 },
    { day: 'Wed', pallets: 78 },
    { day: 'Thu', pallets: 85 },
    { day: 'Fri', pallets: 80 },
    { day: 'Sat', pallets: 88 },
    { day: 'Sun', pallets: 76 }
  ];

  if (loading) {
    return <div className="flex items-center justify-center h-64">Loading...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Production & Inventory</h1>
        <div className="flex space-x-2">
          <Button variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <Button size="sm">
            <Plus className="h-4 w-4 mr-2" />
            Add Product
          </Button>
        </div>
      </div>

      {/* Production Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Daily Production</CardTitle>
            <Package className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{productionData?.daily_production_pallets || 80} pallets</div>
            <p className="text-xs text-muted-foreground">
              Target: {productionData?.target_production_pallets || 160} pallets
            </p>
            <div className="mt-2">
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-blue-600 h-2 rounded-full" 
                  style={{ width: `${((productionData?.daily_production_pallets || 80) / (productionData?.target_production_pallets || 160)) * 100}%` }}
                ></div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Production Efficiency</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{productionData?.production_efficiency || 85.5}%</div>
            <p className="text-xs text-muted-foreground">
              <span className="text-green-600">+2.1% from last week</span>
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Low Stock Alerts</CardTitle>
            <AlertTriangle className="h-4 w-4 text-yellow-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">2</div>
            <p className="text-xs text-muted-foreground">Items below minimum threshold</p>
          </CardContent>
        </Card>
      </div>

      {/* Production Shifts */}
      <Card>
        <CardHeader>
          <CardTitle>Shift Production</CardTitle>
          <CardDescription>Current shift performance</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-blue-50 rounded-lg">
                <div>
                  <h3 className="font-semibold">Shift 1 (6 AM - 2 PM)</h3>
                  <p className="text-sm text-gray-600">Current shift</p>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold">{productionData?.shift_1_pallets || 45}</p>
                  <p className="text-sm text-gray-600">pallets</p>
                </div>
              </div>
              
              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div>
                  <h3 className="font-semibold">Shift 2 (2 PM - 10 PM)</h3>
                  <p className="text-sm text-gray-600">Starting soon</p>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold">{productionData?.shift_2_pallets || 35}</p>
                  <p className="text-sm text-gray-600">pallets (yesterday)</p>
                </div>
              </div>
            </div>

            <div>
              <h3 className="font-semibold mb-4">Weekly Production Trend</h3>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={productionTrend}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="day" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="pallets" fill="#3B82F6" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Inventory Levels */}
      <Card>
        <CardHeader>
          <CardTitle>Current Inventory Levels</CardTitle>
          <CardDescription>Stock levels across all products</CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={inventoryData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="current" fill="#10B981" name="Current Stock" />
              <Bar dataKey="target" fill="#E5E7EB" name="Target Level" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Product List */}
      <Card>
        <CardHeader>
          <CardTitle>Product Catalog</CardTitle>
          <CardDescription>Manage your ice products</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {products.map((product) => (
              <div key={product.id} className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                    <Package className="h-6 w-6 text-blue-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold">{product.name}</h3>
                    <p className="text-sm text-gray-600">{product.weight_lbs} lbs • ${product.price}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <Badge variant={product.is_active ? "default" : "secondary"}>
                    {product.is_active ? "Active" : "Inactive"}
                  </Badge>
                  <Button variant="outline" size="sm">Edit</Button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
