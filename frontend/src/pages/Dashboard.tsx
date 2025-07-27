import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { TrendingUp, Users, Truck, Package, DollarSign, MapPin, Clock, AlertCircle, RefreshCw, Phone, Mail, Navigation } from 'lucide-react';
import { DashboardOverview, ProductionDashboard, FleetDashboard, FinancialDashboard, Location } from '../types/api';
import { apiRequest } from '../utils/api';
import { useErrorToast } from '../hooks/useErrorToast';

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
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [locations, setLocations] = useState<Location[]>([]);
  const [selectedLocation, setSelectedLocation] = useState<Location | null>(null);
  const [showLocationModal, setShowLocationModal] = useState(false);
  const { showError } = useErrorToast();

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [overviewRes, productionRes, fleetRes, financialRes, locationsRes] = await Promise.all([
        apiRequest('/api/dashboard/overview'),
        apiRequest('/api/dashboard/production'),
        apiRequest('/api/dashboard/fleet'),
        apiRequest('/api/dashboard/financial'),
        apiRequest('/api/locations')
      ]);

      const [overview, production, fleet, financial, locations] = await Promise.all([
        overviewRes?.ok ? overviewRes.json() : null,
        productionRes?.ok ? productionRes.json() : null,
        fleetRes?.ok ? fleetRes.json() : null,
        financialRes?.ok ? financialRes.json() : null,
        locationsRes?.ok ? locationsRes.json() : null
      ]);

      setDashboardData({ overview, production, fleet, financial });
      setLocations(locations || []);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
      setError('Failed to load dashboard data');
      showError(error, 'Failed to load dashboard data');
      setDashboardData({
        overview: null,
        production: null,
        fleet: null,
        financial: null
      });
      setLocations([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
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

  const handleLocationClick = (locationName: string) => {
    const location = locations.find(loc => 
      loc.name.toLowerCase().includes(locationName.toLowerCase()) ||
      locationName.toLowerCase().includes(loc.name.toLowerCase())
    );
    
    if (location) {
      setSelectedLocation(location);
      setShowLocationModal(true);
    } else {
      const staticLocation: Location = {
        id: locationName.toLowerCase().replace(/\s+/g, '-'),
        name: locationName,
        address: getLocationAddress(locationName),
        city: getLocationCity(locationName),
        state: getLocationState(locationName),
        zip_code: getLocationZip(locationName),
        phone: '(337) 555-0100',
        email: `${locationName.toLowerCase().replace(/\s+/g, '')}@arcticeice.com`,
        manager_id: '',
        is_active: true
      };
      setSelectedLocation(staticLocation);
      setShowLocationModal(true);
    }
  };

  const getLocationAddress = (name: string) => {
    const addresses: { [key: string]: string } = {
      'Leesville HQ': '123 Ice Plant Rd',
      'Lake Charles': '456 Distribution Ave',
      'Lufkin': '789 Delivery St',
      'Jasper': '321 Storage Blvd'
    };
    return addresses[name] || '123 Main St';
  };

  const getLocationCity = (name: string) => {
    const cities: { [key: string]: string } = {
      'Leesville HQ': 'Leesville',
      'Lake Charles': 'Lake Charles',
      'Lufkin': 'Lufkin',
      'Jasper': 'Jasper'
    };
    return cities[name] || name;
  };

  const getLocationState = (name: string) => {
    const states: { [key: string]: string } = {
      'Leesville HQ': 'LA',
      'Lake Charles': 'LA',
      'Lufkin': 'TX',
      'Jasper': 'TX'
    };
    return states[name] || 'LA';
  };

  const getLocationZip = (name: string) => {
    const zips: { [key: string]: string } = {
      'Leesville HQ': '71446',
      'Lake Charles': '70601',
      'Lufkin': '75901',
      'Jasper': '75951'
    };
    return zips[name] || '70000';
  };

  if (loading) {
    return <div className="flex items-center justify-center h-64">Loading dashboard...</div>;
  }

  if (error) {
    return (
      <Card className="border-red-200 bg-red-50">
        <CardHeader>
          <CardTitle className="flex items-center text-red-800">
            <AlertCircle className="h-5 w-5 mr-2" />
            Dashboard Unavailable
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-red-700 mb-4">{error}</p>
          <Button onClick={fetchDashboardData} variant="outline">
            <RefreshCw className="h-4 w-4 mr-2" />
            Retry
          </Button>
        </CardContent>
      </Card>
    );
  }

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
              <div 
                className="flex items-center justify-between p-3 bg-blue-50 rounded-lg cursor-pointer hover:bg-blue-100 transition-colors"
                onClick={() => handleLocationClick('Leesville HQ')}
              >
                <div className="flex items-center">
                  <MapPin className="h-5 w-5 text-blue-600 mr-2" />
                  <div>
                    <p className="font-medium">Leesville HQ</p>
                    <p className="text-sm text-gray-600">Production &amp; Headquarters</p>
                  </div>
                </div>
                <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs">Active</span>
              </div>

              <div 
                className="flex items-center justify-between p-3 bg-green-50 rounded-lg cursor-pointer hover:bg-green-100 transition-colors"
                onClick={() => handleLocationClick('Lake Charles')}
              >
                <div className="flex items-center">
                  <MapPin className="h-5 w-5 text-green-600 mr-2" />
                  <div>
                    <p className="font-medium">Lake Charles</p>
                    <p className="text-sm text-gray-600">Distribution Center</p>
                  </div>
                </div>
                <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs">Active</span>
              </div>

              <div 
                className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg cursor-pointer hover:bg-yellow-100 transition-colors"
                onClick={() => handleLocationClick('Lufkin')}
              >
                <div className="flex items-center">
                  <MapPin className="h-5 w-5 text-yellow-600 mr-2" />
                  <div>
                    <p className="font-medium">Lufkin</p>
                    <p className="text-sm text-gray-600">Distribution Center</p>
                  </div>
                </div>
                <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs">Active</span>
              </div>

              <div 
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100 transition-colors"
                onClick={() => handleLocationClick('Jasper')}
              >
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

      {/* Location Details Modal */}
      <Dialog open={showLocationModal} onOpenChange={setShowLocationModal}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle className="flex items-center">
              <MapPin className="h-5 w-5 mr-2" />
              {selectedLocation?.name}
            </DialogTitle>
          </DialogHeader>
          
          {selectedLocation && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-2">Address</h3>
                    <div className="text-gray-600">
                      <p>{selectedLocation.address}</p>
                      <p>{selectedLocation.city}, {selectedLocation.state} {selectedLocation.zip_code}</p>
                    </div>
                  </div>
                  
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-2">Contact Information</h3>
                    <div className="space-y-2">
                      <div className="flex items-center text-gray-600">
                        <Phone className="h-4 w-4 mr-2" />
                        <span>{selectedLocation.phone}</span>
                      </div>
                      <div className="flex items-center text-gray-600">
                        <Mail className="h-4 w-4 mr-2" />
                        <span>{selectedLocation.email}</span>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div className="space-y-4">
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-2">Operations</h3>
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-gray-600">Status</span>
                        <span className={`px-2 py-1 rounded-full text-xs ${
                          selectedLocation.is_active 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {selectedLocation.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-gray-600">Type</span>
                        <span className="text-gray-900">
                          {selectedLocation.name.includes('HQ') ? 'Headquarters' :
                           selectedLocation.name.includes('Jasper') ? 'Warehouse' : 'Distribution Center'}
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-2">Quick Actions</h3>
                    <div className="space-y-2">
                      <Button 
                        variant="outline" 
                        size="sm" 
                        className="w-full justify-start"
                        onClick={() => window.open(`https://maps.google.com/?q=${encodeURIComponent(selectedLocation.address + ', ' + selectedLocation.city + ', ' + selectedLocation.state)}`)}
                      >
                        <Navigation className="h-4 w-4 mr-2" />
                        View on Map
                      </Button>
                      <Button 
                        variant="outline" 
                        size="sm" 
                        className="w-full justify-start"
                        onClick={() => window.open(`tel:${selectedLocation.phone}`)}
                      >
                        <Phone className="h-4 w-4 mr-2" />
                        Call Location
                      </Button>
                      <Button 
                        variant="outline" 
                        size="sm" 
                        className="w-full justify-start"
                        onClick={() => window.open(`mailto:${selectedLocation.email}`)}
                      >
                        <Mail className="h-4 w-4 mr-2" />
                        Send Email
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowLocationModal(false)}>
              Close
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
