import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge } from '../../components/ui/badge';
import { MapPin, Clock, Truck, Navigation, CheckCircle } from 'lucide-react';

interface Route {
  id: string;
  name: string;
  driver_name: string;
  vehicle_id: string;
  vehicle_name: string;
  status: 'planned' | 'in_progress' | 'completed';
  estimated_duration: number;
  stops: RouteStop[];
  total_distance: number;
}

interface RouteStop {
  id: string;
  customer_name: string;
  address: string;
  delivery_time: string;
  status: 'pending' | 'completed';
  order_total: number;
}

export function MobileRoutes() {
  const [routes, setRoutes] = useState<Route[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedRoute, setSelectedRoute] = useState<Route | null>(null);

  useEffect(() => {
    fetchRoutes();
  }, []);

  const fetchRoutes = async () => {
    try {
      const mockRoutes: Route[] = [
        {
          id: '1',
          name: 'Route 1 - Lake Charles',
          driver_name: 'Mike Johnson',
          vehicle_id: 'LA-ICE-01',
          vehicle_name: 'LA-ICE-01 (53ft Reefer)',
          status: 'in_progress',
          estimated_duration: 6.5,
          total_distance: 120,
          stops: [
            {
              id: '1',
              customer_name: 'Walmart Supercenter',
              address: '123 Main St, Lake Charles, LA',
              delivery_time: '09:00 AM',
              status: 'completed',
              order_total: 850.00
            },
            {
              id: '2',
              customer_name: 'Brookshire Grocery',
              address: '456 Oak Ave, Lake Charles, LA',
              delivery_time: '11:30 AM',
              status: 'pending',
              order_total: 650.00
            },
            {
              id: '3',
              customer_name: 'Circle K',
              address: '789 Pine St, Lake Charles, LA',
              delivery_time: '02:00 PM',
              status: 'pending',
              order_total: 320.00
            }
          ]
        },
        {
          id: '2',
          name: 'Route 2 - Lufkin',
          driver_name: 'Sarah Wilson',
          vehicle_id: 'TX-ICE-01',
          vehicle_name: 'TX-ICE-01 (20ft Reefer)',
          status: 'planned',
          estimated_duration: 4.0,
          total_distance: 85,
          stops: [
            {
              id: '4',
              customer_name: 'HEB Plus',
              address: '321 Commerce St, Lufkin, TX',
              delivery_time: '10:00 AM',
              status: 'pending',
              order_total: 1200.00
            },
            {
              id: '5',
              customer_name: 'Sonic Drive-In',
              address: '654 Loop 287, Lufkin, TX',
              delivery_time: '01:00 PM',
              status: 'pending',
              order_total: 180.00
            }
          ]
        }
      ];
      
      setRoutes(mockRoutes);
    } catch (error) {
      console.error('Error fetching routes:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-500';
      case 'in_progress': return 'bg-blue-500';
      case 'planned': return 'bg-gray-500';
      default: return 'bg-gray-500';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'in_progress': return <Navigation className="h-4 w-4 text-blue-500" />;
      case 'planned': return <Clock className="h-4 w-4 text-gray-500" />;
      default: return <Clock className="h-4 w-4" />;
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

  if (selectedRoute) {
    return (
      <div className="p-4 space-y-4">
        <div className="flex items-center justify-between">
          <Button variant="outline" size="sm" onClick={() => setSelectedRoute(null)}>
            ← Back
          </Button>
          <h2 className="text-lg font-bold">{selectedRoute.name}</h2>
        </div>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base flex items-center space-x-2">
              <Truck className="h-5 w-5 text-blue-600" />
              <span>Route Details</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <p className="text-xs text-gray-500">Driver</p>
                <p className="font-medium">{selectedRoute.driver_name}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Vehicle</p>
                <p className="font-medium">{selectedRoute.vehicle_name}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Duration</p>
                <p className="font-medium">{selectedRoute.estimated_duration}h</p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Distance</p>
                <p className="font-medium">{selectedRoute.total_distance} mi</p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              {getStatusIcon(selectedRoute.status)}
              <Badge className={getStatusColor(selectedRoute.status)}>
                {selectedRoute.status.replace('_', ' ').toUpperCase()}
              </Badge>
            </div>
          </CardContent>
        </Card>

        <div className="space-y-3">
          <h3 className="font-semibold">Delivery Stops</h3>
          {selectedRoute.stops.map((stop, index) => (
            <Card key={stop.id}>
              <CardContent className="p-4">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    <div className="w-6 h-6 rounded-full bg-blue-100 flex items-center justify-center text-xs font-bold text-blue-600">
                      {index + 1}
                    </div>
                    <div>
                      <p className="font-medium text-sm">{stop.customer_name}</p>
                      <p className="text-xs text-gray-500">{stop.delivery_time}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-1">
                    {getStatusIcon(stop.status)}
                    <span className="text-xs capitalize">{stop.status}</span>
                  </div>
                </div>
                <div className="space-y-1 text-xs">
                  <p className="flex items-center space-x-1">
                    <MapPin className="h-3 w-3 text-gray-400" />
                    <span>{stop.address}</span>
                  </p>
                  <p><strong>Order Total:</strong> ${stop.order_total.toFixed(2)}</p>
                </div>
                {stop.status === 'pending' && (
                  <Button size="sm" className="w-full mt-3">
                    Mark as Delivered
                  </Button>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold">Routes & Deliveries</h2>
        <Button size="sm">
          <Navigation className="h-4 w-4 mr-1" />
          Navigate
        </Button>
      </div>

      <div className="space-y-3">
        {routes.length === 0 ? (
          <Card>
            <CardContent className="p-6 text-center">
              <MapPin className="h-12 w-12 text-gray-400 mx-auto mb-2" />
              <p className="text-gray-500">No routes assigned today</p>
            </CardContent>
          </Card>
        ) : (
          routes.map((route) => (
            <Card key={route.id} className="cursor-pointer" onClick={() => setSelectedRoute(route)}>
              <CardContent className="p-4">
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <h3 className="font-medium">{route.name}</h3>
                    <p className="text-sm text-gray-600">{route.driver_name}</p>
                  </div>
                  <div className="flex items-center space-x-1">
                    {getStatusIcon(route.status)}
                    <Badge className={getStatusColor(route.status)}>
                      {route.status.replace('_', ' ').toUpperCase()}
                    </Badge>
                  </div>
                </div>
                
                <div className="grid grid-cols-3 gap-2 text-xs text-gray-500">
                  <div>
                    <span className="font-medium">{route.stops.length}</span> stops
                  </div>
                  <div>
                    <span className="font-medium">{route.estimated_duration}h</span> duration
                  </div>
                  <div>
                    <span className="font-medium">{route.total_distance}</span> mi
                  </div>
                </div>
                
                <div className="mt-2 text-xs">
                  <p><strong>Vehicle:</strong> {route.vehicle_name}</p>
                  <p><strong>Total Value:</strong> ${route.stops.reduce((sum, stop) => sum + stop.order_total, 0).toFixed(2)}</p>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}
