import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Truck, MapPin, Plus, RefreshCw, Settings, Navigation } from 'lucide-react';
import { Vehicle, Location, FleetDashboard } from '../types/api';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export function FleetManagement() {
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [locations, setLocations] = useState<Location[]>([]);
  const [fleetData, setFleetData] = useState<FleetDashboard | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [vehiclesRes, locationsRes, fleetRes] = await Promise.all([
          fetch(`${API_BASE_URL}/api/vehicles`),
          fetch(`${API_BASE_URL}/api/locations`),
          fetch(`${API_BASE_URL}/api/dashboard/fleet`)
        ]);

        const vehiclesData = await vehiclesRes.json();
        const locationsData = await locationsRes.json();
        const fleetDataRes = await fleetRes.json();

        setVehicles(vehiclesData);
        setLocations(locationsData);
        setFleetData(fleetDataRes);
      } catch (error) {
        console.error('Failed to fetch data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

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

  if (loading) {
    return <div className="flex items-center justify-center h-64">Loading...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Fleet & Route Management</h1>
        <div className="flex space-x-2">
          <Button variant="outline" size="sm">
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
                <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                  <div>
                    <p className="font-medium">Route LA-001</p>
                    <p className="text-sm text-gray-600">Lake Charles Area • 12 stops</p>
                  </div>
                  <Badge className="bg-green-100 text-green-800">In Progress</Badge>
                </div>
                <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                  <div>
                    <p className="font-medium">Route TX-002</p>
                    <p className="text-sm text-gray-600">Lufkin Area • 8 stops</p>
                  </div>
                  <Badge className="bg-blue-100 text-blue-800">Planned</Badge>
                </div>
                <div className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg">
                  <div>
                    <p className="font-medium">Route LA-003</p>
                    <p className="text-sm text-gray-600">Leesville Area • 15 stops</p>
                  </div>
                  <Badge className="bg-yellow-100 text-yellow-800">Optimizing</Badge>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <h3 className="font-semibold">Route Optimization</h3>
              <div className="p-4 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-600 mb-3">
                  Automatic route optimization considers traffic, customer time windows, and vehicle capacity.
                </p>
                <Button className="w-full">
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
