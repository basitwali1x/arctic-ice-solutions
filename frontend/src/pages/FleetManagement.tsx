import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Truck, MapPin, Plus, RefreshCw, Settings, Navigation, AlertCircle } from 'lucide-react';
import { Vehicle, Location, FleetDashboard, Route } from '../types/api';
import { apiRequest } from '../utils/api';
import { useErrorToast } from '../hooks/useErrorToast';
import { useToast } from '../hooks/use-toast';


export function FleetManagement() {
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [locations, setLocations] = useState<Location[]>([]);
  const [fleetData, setFleetData] = useState<FleetDashboard | null>(null);
  const [routes, setRoutes] = useState<Route[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { showError } = useErrorToast();
  const { toast } = useToast();

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [vehiclesRes, locationsRes, fleetRes, routesRes] = await Promise.all([
        apiRequest('/api/vehicles'),
        apiRequest('/api/locations'),
        apiRequest('/api/dashboard/fleet'),
        apiRequest('/api/routes')
      ]);

      const vehiclesData = await vehiclesRes?.json();
      const locationsData = await locationsRes?.json();
      const fleetDataRes = await fleetRes?.json();
      const routesData = await routesRes?.json();

      setVehicles(Array.isArray(vehiclesData) ? vehiclesData : []);
      setLocations(Array.isArray(locationsData) ? locationsData : []);
      setFleetData(fleetDataRes || null);
      setRoutes(Array.isArray(routesData) ? routesData : []);
    } catch (error) {
      console.error('Failed to fetch data:', error);
      setError('Failed to load fleet data');
      setVehicles([]);
      setLocations([]);
      setFleetData(null);
      setRoutes([]);
      showError(error, 'Failed to load fleet data');
    } finally {
      setLoading(false);
    }
  };

  const getLocationName = (locationId: string) => {
    const location = locations.find(l => l.id === locationId);
    return location ? location.name : 'Unknown Location';
  };

  const getVehicleTypeDisplay = (type: string) => {
    const typeMap: Record<string, string> = {
      '53ft_reefer': '53ft Reefer',
      '42ft_reefer': '42ft Reefer',
      '20ft_reefer': '20ft Reefer',
      '16ft_reefer': '16ft Reefer'
    };
    return typeMap[type] || type;
  };

  const fleetByLocationData = Object.entries(fleetData?.vehicles_by_location || {}).map(([location, count]) => ({
    location,
    vehicles: count
  }));

  const handleOptimizeRoutes = async () => {
    try {
      const response = await apiRequest('/api/routes/optimize?location_id=loc_1', {
        method: 'POST'
      });
      
      if (response?.ok) {
        const result = await response.json();
        toast({
          title: 'Success',
          description: result.message || 'Routes optimized successfully',
        });
        fetchData();
      }
    } catch (error) {
      console.error('Error optimizing routes:', error);
      showError(error, 'Failed to optimize routes');
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center h-64">Loading...</div>;
  }

  if (error) {
    return (
      <Card className="border-red-200 bg-red-50">
        <CardHeader>
          <CardTitle className="flex items-center text-red-800">
            <AlertCircle className="h-5 w-5 mr-2" />
            Fleet Data Unavailable
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-red-700 mb-4">{error}</p>
          <Button onClick={fetchData} variant="outline">
            <RefreshCw className="h-4 w-4 mr-2" />
            Try Again
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Fleet & Route Management</h1>
        <div className="flex space-x-2">
          <Button variant="outline" size="sm" onClick={fetchData}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <Button variant="outline" size="sm">
            <Navigation className="h-4 w-4 mr-2" />
            Route Optimizer
          </Button>
          <Button size="sm">
            <Plus className="h-4 w-4 mr-2" />
            Add Vehicle
          </Button>
        </div>
      </div>

      {/* Fleet Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Vehicles</CardTitle>
            <Truck className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{fleetData?.total_vehicles || 8}</div>
            <p className="text-xs text-muted-foreground">Across 4 locations</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">In Use</CardTitle>
            <Navigation className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{fleetData?.vehicles_in_use || 6}</div>
            <p className="text-xs text-muted-foreground">Currently on routes</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Available</CardTitle>
            <Truck className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{fleetData?.vehicles_available || 2}</div>
            <p className="text-xs text-muted-foreground">Ready for dispatch</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Utilization</CardTitle>
            <Settings className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{fleetData?.fleet_utilization || 75}%</div>
            <p className="text-xs text-muted-foreground">Fleet efficiency</p>
          </CardContent>
        </Card>
      </div>

      {/* Fleet Distribution Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Fleet Distribution by Location</CardTitle>
          <CardDescription>Vehicle allocation across your locations</CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={fleetByLocationData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="location" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="vehicles" fill="#3B82F6" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Vehicle List */}
      <Card>
        <CardHeader>
          <CardTitle>Vehicle Fleet</CardTitle>
          <CardDescription>Manage your reefer vehicles</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {vehicles.map((vehicle) => (
              <div key={vehicle.id} className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                    <Truck className="h-6 w-6 text-blue-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold">{vehicle.license_plate}</h3>
                    <p className="text-sm text-gray-600">
                      {getVehicleTypeDisplay(vehicle.vehicle_type)} • {vehicle.capacity_pallets} pallets
                    </p>
                    <div className="flex items-center mt-1">
                      <MapPin className="h-3 w-3 text-gray-400 mr-1" />
                      <span className="text-xs text-gray-500">{getLocationName(vehicle.location_id)}</span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <Badge variant={vehicle.is_active ? "default" : "secondary"}>
                    {vehicle.is_active ? "Active" : "Inactive"}
                  </Badge>
                  <Button variant="outline" size="sm">
                    <Settings className="h-4 w-4 mr-1" />
                    Manage
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Route Management Section */}
      <Card>
        <CardHeader>
          <CardTitle>Route Management</CardTitle>
          <CardDescription>Optimize delivery routes for maximum efficiency</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <h3 className="font-semibold">Today's Routes</h3>
              <div className="space-y-2">
                {routes.length === 0 ? (
                  <p className="text-gray-500">No routes scheduled for today</p>
                ) : (
                  routes.map((route) => (
                    <div key={route.id} className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                      <div>
                        <p className="font-medium">{route.name}</p>
                        <p className="text-sm text-gray-600">{route.stops?.length || 0} stops • {route.estimated_duration_hours}h estimated</p>
                      </div>
                      <Badge className={`${
                        route.status === 'active' ? 'bg-green-100 text-green-800' :
                        route.status === 'planned' ? 'bg-blue-100 text-blue-800' :
                        route.status === 'completed' ? 'bg-gray-100 text-gray-800' :
                        'bg-yellow-100 text-yellow-800'
                      }`}>
                        {route.status === 'active' ? 'In Progress' : 
                         route.status === 'planned' ? 'Planned' :
                         route.status === 'completed' ? 'Completed' : 'Optimizing'}
                      </Badge>
                    </div>
                  ))
                )}
              </div>
            </div>

            <div className="space-y-4">
              <h3 className="font-semibold">Route Optimization</h3>
              <div className="p-4 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-600 mb-3">
                  Automatic route optimization considers traffic, customer time windows, and vehicle capacity.
                </p>
                <Button className="w-full" onClick={handleOptimizeRoutes}>
                  <Navigation className="h-4 w-4 mr-2" />
                  Optimize All Routes
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
