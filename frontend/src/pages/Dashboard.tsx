import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { TrendingUp, Users, Truck, Package, DollarSign, MapPin, Clock } from 'lucide-react';
import { DashboardOverview, ProductionDashboard, FleetDashboard, FinancialDashboard } from '../types/api';
import { apiRequest } from '../utils/api';

export function Dashboard() {
  const [dashboardData, setDashboardData] = useState<{
    overview: DashboardOverview | null;
    production: ProductionDashboard | null;
    fleet: FleetDashboard | null;
    financial: FinancialDashboard | null;
  }>({
    overview: null,
    production: null,
    fleet: null,
    financial: null
  });

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const [overviewRes, productionRes, fleetRes, financialRes] = await Promise.all([
          apiRequest('/api/dashboard/overview'),
          apiRequest('/api/dashboard/production'),
          apiRequest('/api/dashboard/fleet'),
          apiRequest('/api/dashboard/financial')
        ]);

        const [overview, production, fleet, financial] = await Promise.all([
          overviewRes?.ok ? overviewRes.json() : null,
          productionRes?.ok ? productionRes.json() : null,
          fleetRes?.ok ? fleetRes.json() : null,
          financialRes?.ok ? financialRes.json() : null
        ]);

        setDashboardData({ overview, production, fleet, financial });
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error);
        setDashboardData({
          overview: null,
          production: null,
          fleet: null,
          financial: null
        });
      }
    };

    fetchDashboardData();
  }, []);

  const productionData = [
    { name: 'Shift 1', pallets: dashboardData.production?.shift_1_pallets || 45 },
    { name: 'Shift 2', pallets: dashboardData.production?.shift_2_pallets || 35 },
  ];

  const paymentData = dashboardData.financial?.payment_breakdown ? [
    { name: 'Cash', value: dashboardData.financial.payment_breakdown.cash, color: '#0088FE' },
    { name: 'Check', value: dashboardData.financial.payment_breakdown.check, color: '#00C49F' },
    { name: 'Credit', value: dashboardData.financial.payment_breakdown.credit, color: '#FFBB28' }
  ] : [
    { name: 'Cash', value: 45, color: '#0088FE' },
    { name: 'Check', value: 30, color: '#00C49F' },
    { name: 'Credit', value: 25, color: '#FFBB28' }
  ];

  const fleetData = Object.entries(dashboardData.fleet?.vehicles_by_location || {}).map(([location, count]) => ({
    location,
    vehicles: count
  }));

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <div className="flex items-center space-x-2 text-sm text-gray-600">
          <Clock className="h-4 w-4" />
          <span>Last updated: {new Date().toLocaleTimeString()}</span>
        </div>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Customers</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashboardData.overview?.total_customers || 1200}</div>
            <p className="text-xs text-muted-foreground">
              <span className="text-green-600 flex items-center">
                <TrendingUp className="h-3 w-3 mr-1" />
                +12% from last month
              </span>
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Fleet Vehicles</CardTitle>
            <Truck className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashboardData.overview?.total_vehicles || 8}</div>
            <p className="text-xs text-muted-foreground">
              {dashboardData.fleet?.vehicles_in_use || 6} in use, {dashboardData.fleet?.vehicles_available || 2} available
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Today's Orders</CardTitle>
            <Package className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashboardData.overview?.total_orders_today || 0}</div>
            <p className="text-xs text-muted-foreground">
              <span className="text-green-600 flex items-center">
                <TrendingUp className="h-3 w-3 mr-1" />
                +8% from yesterday
              </span>
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Daily Revenue</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${dashboardData.financial?.daily_revenue?.toLocaleString() || '12,500'}</div>
            <p className="text-xs text-muted-foreground">
              <span className="text-green-600 flex items-center">
                <TrendingUp className="h-3 w-3 mr-1" />
                +15% from yesterday
              </span>
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Production Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Daily Production</CardTitle>
            <CardDescription>Pallets produced by shift</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={productionData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="pallets" fill="#3B82F6" />
              </BarChart>
            </ResponsiveContainer>
            <div className="mt-4 text-sm text-gray-600">
              Target: {dashboardData.production?.target_production_pallets || 160} pallets/day
            </div>
          </CardContent>
        </Card>

        {/* Payment Methods */}
        <Card>
          <CardHeader>
            <CardTitle>Payment Methods</CardTitle>
            <CardDescription>Revenue breakdown by payment type</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={paymentData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value }) => `${name}: ${value}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {paymentData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Fleet and Locations */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Fleet Distribution */}
        <Card>
          <CardHeader>
            <CardTitle>Fleet by Location</CardTitle>
            <CardDescription>Vehicle distribution across locations</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={fleetData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="location" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="vehicles" fill="#10B981" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Locations Overview */}
        <Card>
          <CardHeader>
            <CardTitle>Locations Overview</CardTitle>
            <CardDescription>Multi-location operations status</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                <div className="flex items-center">
                  <MapPin className="h-5 w-5 text-blue-600 mr-2" />
                  <div>
                    <p className="font-medium">Leesville HQ</p>
                    <p className="text-sm text-gray-600">Production &amp; Headquarters</p>
                  </div>
                </div>
                <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs">Active</span>
              </div>

              <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                <div className="flex items-center">
                  <MapPin className="h-5 w-5 text-green-600 mr-2" />
                  <div>
                    <p className="font-medium">Lake Charles</p>
                    <p className="text-sm text-gray-600">Distribution Center</p>
                  </div>
                </div>
                <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs">Active</span>
              </div>

              <div className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg">
                <div className="flex items-center">
                  <MapPin className="h-5 w-5 text-yellow-600 mr-2" />
                  <div>
                    <p className="font-medium">Lufkin</p>
                    <p className="text-sm text-gray-600">Distribution Center</p>
                  </div>
                </div>
                <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs">Active</span>
              </div>

              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center">
                  <MapPin className="h-5 w-5 text-gray-600 mr-2" />
                  <div>
                    <p className="font-medium">Jasper</p>
                    <p className="text-sm text-gray-600">Warehouse Only</p>
                  </div>
                </div>
                <span className="px-2 py-1 bg-yellow-100 text-yellow-800 rounded-full text-xs">Warehouse</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
