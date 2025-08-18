import { useState, useEffect, useCallback, useMemo } from 'react';
import './Dashboard.css';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { TrendingUp, Users, Truck, Package, DollarSign, MapPin, Clock, AlertCircle, RefreshCw, Phone, Mail, Navigation, FileText } from 'lucide-react';
import { DashboardOverview, ProductionDashboard, FleetDashboard, FinancialDashboard, Location, Route } from '../types/api';
import { apiRequest } from '../utils/api';
import { useErrorToast } from '../hooks/useErrorToast';
import { LocationPerformance } from '../components/LocationPerformance';

export function Dashboard() {
  const [dashboardState, setDashboardState] = useState<{
    data: {
      overview: DashboardOverview | null;
      production: ProductionDashboard | null;
      fleet: FleetDashboard | null;
      financial: FinancialDashboard | null;
    };
    locations: Location[];
    loading: boolean;
    error: string | null;
  }>({
    data: {
      overview: null,
      production: null,
      fleet: null,
      financial: null
    },
    locations: [],
    loading: true,
    error: null
  });
  const [selectedLocation, setSelectedLocation] = useState<Location | null>(null);
  const [showLocationModal, setShowLocationModal] = useState(false);
  const [selectedOptimizeLocation, setSelectedOptimizeLocation] = useState<string>('');
  const [optimizedRoutes, setOptimizedRoutes] = useState<Route[]>([]);
  const [isOptimizing, setIsOptimizing] = useState(false);
  const { showError } = useErrorToast();

  const fetchDashboardData = useCallback(async () => {
    try {
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

      setDashboardState({
        data: { overview, production, fleet, financial },
        locations: locations || [],
        loading: false,
        error: null
      });
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
      setDashboardState(prev => ({
        ...prev,
        loading: false,
        error: 'Failed to load dashboard data'
      }));
    }
  }, []);

  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  const productionData = useMemo(() => [
    { name: 'Shift 1', pallets: dashboardState.data.production?.shift_1_pallets || 45 },
    { name: 'Shift 2', pallets: dashboardState.data.production?.shift_2_pallets || 35 },
  ], [dashboardState.data.production]);

  const paymentData = useMemo(() => dashboardState.data.financial?.payment_breakdown ? [
    { name: 'Cash', value: dashboardState.data.financial.payment_breakdown.cash, color: '#0088FE' },
    { name: 'Check', value: dashboardState.data.financial.payment_breakdown.check, color: '#00C49F' },
    { name: 'Credit', value: dashboardState.data.financial.payment_breakdown.credit, color: '#FFBB28' }
  ] : [
    { name: 'Cash', value: 45, color: '#0088FE' },
    { name: 'Check', value: 30, color: '#00C49F' },
    { name: 'Credit', value: 25, color: '#FFBB28' }
  ], [dashboardState.data.financial]);

  const fleetData = useMemo(() => Object.entries(dashboardState.data.fleet?.vehicles_by_location || {}).map(([location, count]) => ({
    location,
    vehicles: count
  })), [dashboardState.data.fleet]);

  const handleLocationClick = (locationName: string) => {
    const location = dashboardState.locations.find(loc => 
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
        location_type: 'distribution',
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

  const handleOptimizeRoutes = async () => {
    if (!selectedOptimizeLocation) {
      showError(new Error('Please select a location'), 'Please select a location for route optimization');
      return;
    }

    try {
      setIsOptimizing(true);
      const response = await apiRequest(`/api/routes/optimize?location_id=${selectedOptimizeLocation}`, {
        method: 'POST'
      });
      
      if (response?.ok) {
        const result = await response.json();
        setOptimizedRoutes(result.routes || []);
        if (result.routes && result.routes.length > 0) {
          console.log(`Successfully optimized ${result.routes.length} routes`);
        } else {
          showError(new Error('No routes generated'), result.message || 'No pending orders found for optimization');
        }
      }
    } catch (error) {
      console.error('Error optimizing routes:', error);
      showError(error, 'Failed to optimize routes');
      setOptimizedRoutes([]);
    } finally {
      setIsOptimizing(false);
    }
  };

  if (dashboardState.loading) {
    return <div className="flex items-center justify-center h-64 dashboard-loading">Loading dashboard...</div>;
  }

  if (dashboardState.error) {
    return (
      <Card className="border-red-200 bg-red-50">
        <CardHeader>
          <CardTitle className="flex items-center text-red-800">
            <AlertCircle className="h-5 w-5 mr-2" />
            Dashboard Unavailable
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-red-700 mb-4">{dashboardState.error}</p>
          <Button onClick={fetchDashboardData} variant="outline">
            <RefreshCw className="h-4 w-4 mr-2" />
            Retry
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6 dashboard-container dashboard-content dashboard-loaded">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <div className="flex items-center space-x-2 text-sm text-gray-600">
          <Clock className="h-4 w-4" />
          <span>Last updated: {dashboardState.loading ? 'Loading...' : 'Just now'}</span>
        </div>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Customers</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashboardState.data.overview?.total_customers || 1200}</div>
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
            <div className="text-2xl font-bold">{dashboardState.data.overview?.total_vehicles || 8}</div>
            <p className="text-xs text-muted-foreground">
              {dashboardState.data.fleet?.vehicles_in_use || 6} in use, {dashboardState.data.fleet?.vehicles_available || 2} available
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Today's Orders</CardTitle>
            <Package className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashboardState.data.overview?.total_orders_today || 0}</div>
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
            <CardTitle className="text-sm font-medium">Today's Revenue</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${dashboardState.data.financial?.daily_revenue?.toLocaleString() || '0'}</div>
            <p className="text-xs text-muted-foreground">
              <span className="text-green-600 flex items-center">
                <TrendingUp className="h-3 w-3 mr-1" />
                Current day revenue
              </span>
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Average Daily Revenue</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${dashboardState.data.financial?.daily_revenue_average?.toLocaleString() || '12,500'}</div>
            <p className="text-xs text-muted-foreground">
              <span className="text-blue-600 flex items-center">
                <TrendingUp className="h-3 w-3 mr-1" />
                7-day average
              </span>
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Outstanding Invoices</CardTitle>
            <FileText className="h-4 w-4 text-yellow-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">${dashboardState.data.financial?.outstanding_invoices?.toLocaleString() || '25,000'}</div>
            <p className="text-xs text-muted-foreground">Accounts receivable</p>
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
              Target: {dashboardState.data.production?.target_production_pallets || 160} pallets/day
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
                  {paymentData.map((entry: any, index: number) => (
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

      {/* AI Route Optimization */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Navigation className="h-5 w-5 mr-2" />
            AI Route Optimization
          </CardTitle>
          <CardDescription>Generate optimized delivery routes using AI algorithms</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium text-gray-700 mb-2 block">Select Location</label>
                <Select value={selectedOptimizeLocation} onValueChange={setSelectedOptimizeLocation}>
                  <SelectTrigger>
                    <SelectValue placeholder="Choose location for optimization" />
                  </SelectTrigger>
                  <SelectContent>
                    {dashboardState.locations.map((location) => (
                      <SelectItem key={location.id} value={location.id}>
                        {location.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              <Button 
                onClick={handleOptimizeRoutes} 
                disabled={!selectedOptimizeLocation || isOptimizing}
                className="w-full"
              >
                <Navigation className="h-4 w-4 mr-2" />
                {isOptimizing ? 'AI Optimizing Routes...' : 'Generate AI-Optimized Routes'}
              </Button>
              
              {optimizedRoutes.length > 0 && (
                <div className="text-sm text-green-600 bg-green-50 p-3 rounded-lg">
                  ✓ Generated {optimizedRoutes.length} optimized route{optimizedRoutes.length !== 1 ? 's' : ''}
                </div>
              )}
            </div>

            <div className="space-y-4">
              <h3 className="font-semibold">Route Preview</h3>
              {optimizedRoutes.length === 0 ? (
                <div className="text-gray-500 text-sm bg-gray-50 p-4 rounded-lg text-center">
                  Select a location and click "Generate AI-Optimized Routes" to see Google OR-Tools powered delivery routes with real-time traffic optimization
                </div>
              ) : (
                <div className="space-y-3 max-h-64 overflow-y-auto">
                  {optimizedRoutes.map((route) => (
                    <div key={route.id} className="p-3 bg-blue-50 rounded-lg border">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-medium text-sm">{route.name}</h4>
                        <Badge className="bg-blue-100 text-blue-800">
                          {route.status}
                        </Badge>
                      </div>
                      <div className="text-xs text-gray-600 space-y-1">
                        <div className="flex justify-between">
                          <span>Stops:</span>
                          <span>{route.stops?.length || 0}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Est. Duration:</span>
                          <span>{route.estimated_duration_hours}h</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Date:</span>
                          <span>{route.date}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>AI Optimized:</span>
                          <span className="text-green-600">✓ OR-Tools</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Customer Mapping and Location Performance */}
      <div className="grid grid-cols-1 gap-6">
        <LocationPerformance locations={dashboardState.locations} />
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
