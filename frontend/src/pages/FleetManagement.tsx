import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogDescription } from '@/components/ui/dialog';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Truck, MapPin, Plus, RefreshCw, Settings, Navigation, AlertCircle, Upload } from 'lucide-react';
import { Vehicle, Location, FleetDashboard, Route } from '../types/api';
import { apiRequest } from '../utils/api';
import { useErrorToast } from '../hooks/useErrorToast';
import { useToast } from '../hooks/use-toast';
import GoogleMapsNavigation from '../components/GoogleMapsNavigation';


export function FleetManagement() {
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [locations, setLocations] = useState<Location[]>([]);
  const [fleetData, setFleetData] = useState<FleetDashboard | null>(null);
  const [routes, setRoutes] = useState<Route[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { showError } = useErrorToast();
  const { toast } = useToast();
  const [showVehicleModal, setShowVehicleModal] = useState(false);
  const [showRouteImportModal, setShowRouteImportModal] = useState(false);
  const [importing, setImporting] = useState(false);
  const [importFiles, setImportFiles] = useState<FileList | null>(null);
  const [selectedLocationId, setSelectedLocationId] = useState('');
  const [selectedOptimizeLocation, setSelectedOptimizeLocation] = useState<string>('');
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [showRouteMapModal, setShowRouteMapModal] = useState(false);
  const [selectedRoute, setSelectedRoute] = useState<any>(null);
  const [newVehicle, setNewVehicle] = useState({
    license_plate: '',
    vehicle_type: '53ft_reefer',
    capacity_pallets: '',
    location_id: '',
    is_active: true
  });

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
        toast({
          title: 'Success',
          description: result.message || 'Routes optimized successfully',
        });
        fetchData();
      }
    } catch (error) {
      console.error('Error optimizing routes:', error);
      showError(error, 'Failed to optimize routes');
    } finally {
      setIsOptimizing(false);
    }
  };

  const handleCreateVehicle = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const vehicleData = {
        ...newVehicle,
        capacity_pallets: parseInt(newVehicle.capacity_pallets)
      };

      const response = await apiRequest('/api/vehicles', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(vehicleData)
      });

      if (response?.ok) {
        toast({
          title: 'Success',
          description: 'Vehicle created successfully',
        });
        setShowVehicleModal(false);
        setNewVehicle({
          license_plate: '',
          vehicle_type: '53ft_reefer',
          capacity_pallets: '',
          location_id: '',
          is_active: true
        });
        fetchData();
      }
    } catch (error) {
      console.error('Error creating vehicle:', error);
      showError(error, 'Failed to create vehicle');
    }
  };

  const handleRouteImport = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!importFiles || importFiles.length === 0) {
      showError(new Error('No files selected'), 'Please select Excel files to import');
      return;
    }

    if (!selectedLocationId) {
      showError(new Error('No location selected'), 'Please select a target location');
      return;
    }

    try {
      setImporting(true);
      
      const formData = new FormData();
      Array.from(importFiles).forEach(file => {
        formData.append('files', file);
      });
      formData.append('location_id', selectedLocationId);

      const response = await apiRequest('/api/routes/bulk-import', {
        method: 'POST',
        body: formData,
      });

      if (response && response.ok) {
        const result = await response.json();
        toast({
          title: "Import Successful!",
          description: `Imported ${result.routes_imported} routes with ${result.total_records} total stops`,
        });
        resetRouteImportModal();
        fetchData();
      } else if (response) {
        const errorData = await response.json();
        showError(new Error('Import failed'), errorData.detail || 'Unknown error occurred');
      } else {
        showError(new Error('Network error'), 'Failed to connect to server');
      }
    } catch (error) {
      showError(error as Error, 'Failed to import routes');
    } finally {
      setImporting(false);
    }
  };

  const resetRouteImportModal = () => {
    setShowRouteImportModal(false);
    setImportFiles(null);
    setSelectedLocationId('');
  };

  const handleRouteCardClick = (route: any) => {
    if (route.status === 'planned' && route.stops && route.stops.length > 0) {
      setSelectedRoute(route);
      setShowRouteMapModal(true);
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
          <Button variant="outline" size="sm" onClick={() => setShowRouteImportModal(true)}>
            <Upload className="h-4 w-4 mr-2" />
            Import Routes
          </Button>
          <Button size="sm" onClick={() => setShowVehicleModal(true)}>
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
                    <div 
                      key={route.id} 
                      className={`flex items-center justify-between p-3 bg-green-50 rounded-lg ${
                        route.status === 'planned' && route.stops && route.stops.length > 0 
                          ? 'cursor-pointer hover:bg-green-100 transition-colors' 
                          : ''
                      }`}
                      onClick={() => handleRouteCardClick(route)}
                    >
                      <div>
                        <p className="font-medium">{route.name}</p>
                        <p className="text-sm text-gray-600">
                          {route.stops?.length || 0} stops • {route.estimated_duration_hours}h estimated
                          {route.status === 'planned' && route.stops && route.stops.length > 0 && (
                            <span className="ml-2 text-blue-600">• Click to view map</span>
                          )}
                        </p>
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
              <div className="p-4 bg-gray-50 rounded-lg space-y-4">
                <p className="text-sm text-gray-600">
                  Automatic route optimization considers traffic, customer time windows, and vehicle capacity.
                </p>
                <div>
                  <label className="text-sm font-medium text-gray-700 mb-2 block">Select Location</label>
                  <Select value={selectedOptimizeLocation} onValueChange={setSelectedOptimizeLocation}>
                    <SelectTrigger>
                      <SelectValue placeholder="Choose location for optimization" />
                    </SelectTrigger>
                    <SelectContent>
                      {locations.map(location => (
                        <SelectItem key={location.id} value={location.id}>
                          {location.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <Button 
                  className="w-full" 
                  onClick={handleOptimizeRoutes}
                  disabled={!selectedOptimizeLocation || isOptimizing}
                >
                  <Navigation className="h-4 w-4 mr-2" />
                  {isOptimizing ? 'Optimizing Routes...' : 'Optimize All Routes'}
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Vehicle Creation Modal */}
      <Dialog open={showVehicleModal} onOpenChange={setShowVehicleModal}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Add New Vehicle</DialogTitle>
          </DialogHeader>
          
          <form onSubmit={handleCreateVehicle} className="space-y-4">
            <div>
              <Label htmlFor="license_plate">License Plate</Label>
              <Input
                id="license_plate"
                value={newVehicle.license_plate}
                onChange={(e) => setNewVehicle({...newVehicle, license_plate: e.target.value})}
                placeholder="Enter license plate"
                required
              />
            </div>
            
            <div>
              <Label htmlFor="vehicle_type">Vehicle Type</Label>
              <Select value={newVehicle.vehicle_type} onValueChange={(value) => setNewVehicle({...newVehicle, vehicle_type: value})}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="53ft_reefer">53ft Reefer</SelectItem>
                  <SelectItem value="42ft_reefer">42ft Reefer</SelectItem>
                  <SelectItem value="20ft_reefer">20ft Reefer</SelectItem>
                  <SelectItem value="16ft_reefer">16ft Reefer</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <Label htmlFor="capacity_pallets">Capacity (Pallets)</Label>
              <Input
                id="capacity_pallets"
                type="number"
                value={newVehicle.capacity_pallets}
                onChange={(e) => setNewVehicle({...newVehicle, capacity_pallets: e.target.value})}
                placeholder="Enter pallet capacity"
                min="1"
                required
              />
            </div>
            
            <div>
              <Label htmlFor="location_id">Location</Label>
              <Select value={newVehicle.location_id} onValueChange={(value) => setNewVehicle({...newVehicle, location_id: value})}>
                <SelectTrigger>
                  <SelectValue placeholder="Select location" />
                </SelectTrigger>
                <SelectContent>
                  {locations.map(location => (
                    <SelectItem key={location.id} value={location.id}>
                      {location.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="is_active"
                checked={newVehicle.is_active}
                onChange={(e) => setNewVehicle({...newVehicle, is_active: e.target.checked})}
              />
              <Label htmlFor="is_active">Active Vehicle</Label>
            </div>
            
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setShowVehicleModal(false)}>
                Cancel
              </Button>
              <Button type="submit">
                Create Vehicle
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Route Import Modal */}
      <Dialog open={showRouteImportModal} onOpenChange={setShowRouteImportModal}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Bulk Import Routes</DialogTitle>
            <DialogDescription>
              Import routes from Excel files. Each sheet will be treated as a separate route.
            </DialogDescription>
          </DialogHeader>
          
          <form onSubmit={handleRouteImport} className="space-y-4">
            <div>
              <Label htmlFor="location_id">Target Location *</Label>
              <Select value={selectedLocationId} onValueChange={setSelectedLocationId}>
                <SelectTrigger>
                  <SelectValue placeholder="Select location" />
                </SelectTrigger>
                <SelectContent>
                  {locations.map(location => (
                    <SelectItem key={location.id} value={location.id}>
                      {location.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="route_files">Excel Files *</Label>
              <Input
                id="route_files"
                type="file"
                accept=".xlsx,.xls"
                multiple
                onChange={(e) => setImportFiles(e.target.files)}
                disabled={importing}
              />
              <p className="text-sm text-gray-500 mt-1">
                Select Excel files containing route data. Each sheet will become a separate route.
              </p>
            </div>

            <DialogFooter>
              <Button 
                type="button" 
                variant="outline" 
                onClick={resetRouteImportModal}
                disabled={importing}
              >
                Cancel
              </Button>
              <Button 
                type="submit" 
                disabled={importing || !importFiles || !selectedLocationId}
              >
                {importing ? 'Importing...' : 'Import Routes'}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Route Map Modal */}
      <Dialog open={showRouteMapModal} onOpenChange={setShowRouteMapModal}>
        <DialogContent className="max-w-4xl max-h-[80vh]">
          <DialogHeader>
            <DialogTitle>
              {selectedRoute?.name || 'Route Map'}
            </DialogTitle>
            <DialogDescription>
              View route stops and navigation on the map
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            {selectedRoute && selectedRoute.stops && selectedRoute.stops.length > 0 ? (
              <div className="h-96">
                <GoogleMapsNavigation
                  stops={selectedRoute.stops.map((stop: any) => ({
                    id: stop.id,
                    order_id: stop.order_id || stop.id,
                    customer_id: stop.customer_id,
                    stop_number: stop.stop_number || 1,
                    estimated_arrival: stop.estimated_arrival || '',
                    status: stop.status || 'pending',
                    customer_name: stop.customer_name,
                    address: stop.address,
                    coordinates: stop.coordinates,
                    delivery_instructions: '',
                    priority: 1,
                    time_window_start: '',
                    time_window_end: '',
                    completed_at: stop.status === 'completed' ? new Date().toISOString() : undefined
                  }))}
                  onDirectionsChange={(directions: any) => {
                    console.log('Route directions updated:', directions);
                  }}
                />
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                No route stops available or coordinates missing
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
