import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge } from '../../components/ui/badge';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../components/ui/select';
import { MapPin, Navigation, Package, DollarSign, Fuel, Clock, Bluetooth } from 'lucide-react';
import { getCurrentPosition, watchPosition, clearWatch } from '../../utils/capacitor';

interface RouteStop {
  id: string;
  address: string;
  customer: string;
  bags: number;
  status: 'pending' | 'delivered' | 'failed';
  payment_method?: 'cash' | 'check' | 'credit';
  payment_amount?: number;
  delivery_time?: string;
}

interface DriverRoute {
  id: string;
  route_number: string;
  driver_name: string;
  vehicle_id: string;
  start_time: string;
  estimated_completion: string;
  total_stops: number;
  completed_stops: number;
  total_bags: number;
  delivered_bags: number;
  stops: RouteStop[];
}

export function MobileDriver() {
  const [currentRoute, setCurrentRoute] = useState<DriverRoute | null>(null);
  const [currentLocation, setCurrentLocation] = useState<{ lat: number; lng: number } | null>(null);
  const [selectedStop, setSelectedStop] = useState<RouteStop | null>(null);
  const [deliveryForm, setDeliveryForm] = useState({
    bags_delivered: 0,
    payment_method: '',
    payment_amount: 0,
    notes: ''
  });
  const [fuelData, setFuelData] = useState({
    current_level: 75,
    fuel_added: 0,
    fuel_cost: 0,
    odometer: 125430
  });
  const [isTracking, setIsTracking] = useState(false);
  const [watchId, setWatchId] = useState<string | number | null>(null);

  useEffect(() => {
    setCurrentRoute({
      id: 'route-001',
      route_number: 'LA-001',
      driver_name: 'Field Technician',
      vehicle_id: 'LA-ICE-01',
      start_time: '08:00 AM',
      estimated_completion: '04:30 PM',
      total_stops: 12,
      completed_stops: 3,
      total_bags: 240,
      delivered_bags: 60,
      stops: [
        {
          id: 'stop-1',
          address: '123 Main St, Lake Charles, LA',
          customer: 'Corner Store #1',
          bags: 20,
          status: 'delivered',
          payment_method: 'cash',
          payment_amount: 45.00,
          delivery_time: '09:15 AM'
        },
        {
          id: 'stop-2',
          address: '456 Oak Ave, Lake Charles, LA',
          customer: 'Gas Station Plus',
          bags: 25,
          status: 'delivered',
          payment_method: 'credit',
          payment_amount: 56.25,
          delivery_time: '10:30 AM'
        },
        {
          id: 'stop-3',
          address: '789 Pine St, Lake Charles, LA',
          customer: 'Quick Mart',
          bags: 15,
          status: 'delivered',
          payment_method: 'check',
          payment_amount: 33.75,
          delivery_time: '11:45 AM'
        },
        {
          id: 'stop-4',
          address: '321 Elm Dr, Lake Charles, LA',
          customer: 'Food Express',
          bags: 30,
          status: 'pending'
        }
      ]
    });

    const initializeLocation = async () => {
      try {
        const position = await getCurrentPosition();
        setCurrentLocation({
          lat: position.coords.latitude,
          lng: position.coords.longitude
        });
      } catch (error) {
        console.error('GPS Error:', error);
      }
    };

    initializeLocation();
  }, []);

  const startGPSTracking = async () => {
    try {
      setIsTracking(true);
      const id = await watchPosition((position) => {
        const newLocation = {
          lat: position.coords.latitude,
          lng: position.coords.longitude
        };
        setCurrentLocation(newLocation);
        
        if (currentRoute) {
          fetch('/api/drivers/driver-001/location', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify({
              lat: newLocation.lat,
              lng: newLocation.lng,
              timestamp: new Date().toISOString(),
              route_id: currentRoute.route_number
            })
          }).catch(error => console.error('Failed to update location:', error));
        }
      });
      setWatchId(id);
    } catch (error) {
      console.error('GPS Tracking Error:', error);
      setIsTracking(false);
    }
  };

  const stopGPSTracking = async () => {
    try {
      setIsTracking(false);
      if (watchId !== null) {
        await clearWatch(watchId);
        setWatchId(null);
      }
    } catch (error) {
      console.error('Error stopping GPS tracking:', error);
    }
  };

  const handleDeliveryComplete = (stop: RouteStop) => {
    if (!currentRoute) return;
    
    const updatedStops = currentRoute.stops.map(s => 
      s.id === stop.id 
        ? { 
            ...s, 
            status: 'delivered' as const,
            payment_method: deliveryForm.payment_method as 'cash' | 'check' | 'credit',
            payment_amount: deliveryForm.payment_amount,
            delivery_time: new Date().toLocaleTimeString()
          }
        : s
    );

    setCurrentRoute({
      ...currentRoute,
      stops: updatedStops,
      completed_stops: currentRoute.completed_stops + 1,
      delivered_bags: currentRoute.delivered_bags + deliveryForm.bags_delivered
    });

    setSelectedStop(null);
    setDeliveryForm({ bags_delivered: 0, payment_method: '', payment_amount: 0, notes: '' });
  };

  const printReceipt = async (stop: RouteStop) => {
    if ('bluetooth' in navigator) {
      try {
        await (navigator as { bluetooth: { requestDevice: (options: { filters: { services: string[] }[] }) => Promise<unknown> } }).bluetooth.requestDevice({
          filters: [{ services: ['000018f0-0000-1000-8000-00805f9b34fb'] }]
        });
        
        const receiptData = `
ARCTIC ICE SOLUTIONS
Delivery Receipt
------------------------
Customer: ${stop.customer}
Address: ${stop.address}
Bags Delivered: ${stop.bags}
Amount: $${stop.payment_amount?.toFixed(2)}
Payment: ${stop.payment_method?.toUpperCase()}
Time: ${stop.delivery_time}
Driver: ${currentRoute?.driver_name}
Route: ${currentRoute?.route_number}
------------------------
Thank you for your business!
        `;
        
        console.log('Printing receipt:', receiptData);
        alert('Receipt sent to printer!');
      } catch (error) {
        console.error('Bluetooth printing error:', error);
        alert('Printer not available. Receipt saved locally.');
      }
    } else {
      alert('Bluetooth not supported. Receipt saved locally.');
    }
  };

  if (!currentRoute) {
    return <div className="flex items-center justify-center h-64">Loading route...</div>;
  }

  return (
    <div className="p-4 space-y-4">
      <div>
        <h2 className="text-xl font-bold text-gray-900 mb-4">Driver Dashboard</h2>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Route {currentRoute.route_number}</span>
            <Badge variant="outline">{currentRoute.vehicle_id}</Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{currentRoute.completed_stops}/{currentRoute.total_stops}</div>
              <div className="text-xs text-gray-500">Stops Completed</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{currentRoute.delivered_bags}/{currentRoute.total_bags}</div>
              <div className="text-xs text-gray-500">Bags Delivered</div>
            </div>
          </div>
          <div className="mt-4 flex space-x-2">
            <Button 
              variant={isTracking ? "destructive" : "default"} 
              size="sm" 
              onClick={isTracking ? stopGPSTracking : startGPSTracking}
              className="flex-1"
            >
              <Navigation className="h-4 w-4 mr-2" />
              {isTracking ? 'Stop Tracking' : 'Start GPS Tracking'}
            </Button>
            {currentLocation && (
              <Button variant="outline" size="sm">
                <MapPin className="h-4 w-4 mr-2" />
                GPS: {currentLocation.lat.toFixed(4)}, {currentLocation.lng.toFixed(4)}
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Route Stops</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {currentRoute.stops.map((stop, index) => (
              <div key={stop.id} className="border rounded-lg p-3">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <Badge variant={stop.status === 'delivered' ? 'default' : 'secondary'}>
                        Stop {index + 1}
                      </Badge>
                      <span className="font-medium">{stop.customer}</span>
                    </div>
                    <p className="text-sm text-gray-600 mt-1">{stop.address}</p>
                    <div className="flex items-center space-x-4 mt-2">
                      <span className="text-sm">
                        <Package className="h-3 w-3 inline mr-1" />
                        {stop.bags} bags
                      </span>
                      {stop.payment_amount && (
                        <span className="text-sm">
                          <DollarSign className="h-3 w-3 inline mr-1" />
                          ${stop.payment_amount.toFixed(2)} ({stop.payment_method})
                        </span>
                      )}
                      {stop.delivery_time && (
                        <span className="text-sm">
                          <Clock className="h-3 w-3 inline mr-1" />
                          {stop.delivery_time}
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="flex flex-col space-y-1">
                    {stop.status === 'pending' && (
                      <Button size="sm" onClick={() => setSelectedStop(stop)}>
                        Deliver
                      </Button>
                    )}
                    {stop.status === 'delivered' && (
                      <Button size="sm" variant="outline" onClick={() => printReceipt(stop)}>
                        <Bluetooth className="h-3 w-3 mr-1" />
                        Print
                      </Button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Fuel & Load Tracking</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="fuel-level">Current Fuel Level (%)</Label>
              <Input
                id="fuel-level"
                type="number"
                value={fuelData.current_level}
                onChange={(e) => setFuelData({...fuelData, current_level: parseInt(e.target.value)})}
              />
            </div>
            <div>
              <Label htmlFor="odometer">Odometer Reading</Label>
              <Input
                id="odometer"
                type="number"
                value={fuelData.odometer}
                onChange={(e) => setFuelData({...fuelData, odometer: parseInt(e.target.value)})}
              />
            </div>
            <div>
              <Label htmlFor="fuel-added">Fuel Added (gallons)</Label>
              <Input
                id="fuel-added"
                type="number"
                step="0.1"
                value={fuelData.fuel_added}
                onChange={(e) => setFuelData({...fuelData, fuel_added: parseFloat(e.target.value)})}
              />
            </div>
            <div>
              <Label htmlFor="fuel-cost">Fuel Cost ($)</Label>
              <Input
                id="fuel-cost"
                type="number"
                step="0.01"
                value={fuelData.fuel_cost}
                onChange={(e) => setFuelData({...fuelData, fuel_cost: parseFloat(e.target.value)})}
              />
            </div>
          </div>
          <Button className="w-full mt-4">
            <Fuel className="h-4 w-4 mr-2" />
            Update Fuel Log
          </Button>
        </CardContent>
      </Card>

      {selectedStop && (
        <Card>
          <CardHeader>
            <CardTitle>Complete Delivery - {selectedStop.customer}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <Label htmlFor="bags-delivered">Bags Delivered</Label>
                <Input
                  id="bags-delivered"
                  type="number"
                  value={deliveryForm.bags_delivered}
                  onChange={(e) => setDeliveryForm({...deliveryForm, bags_delivered: parseInt(e.target.value)})}
                  placeholder={`Max: ${selectedStop.bags}`}
                />
              </div>
              <div>
                <Label htmlFor="payment-method">Payment Method</Label>
                <Select value={deliveryForm.payment_method} onValueChange={(value) => setDeliveryForm({...deliveryForm, payment_method: value})}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select payment method" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="cash">Cash</SelectItem>
                    <SelectItem value="check">Check</SelectItem>
                    <SelectItem value="credit">Credit Card</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="payment-amount">Payment Amount ($)</Label>
                <Input
                  id="payment-amount"
                  type="number"
                  step="0.01"
                  value={deliveryForm.payment_amount}
                  onChange={(e) => setDeliveryForm({...deliveryForm, payment_amount: parseFloat(e.target.value)})}
                />
              </div>
              <div>
                <Label htmlFor="delivery-notes">Delivery Notes</Label>
                <Input
                  id="delivery-notes"
                  value={deliveryForm.notes}
                  onChange={(e) => setDeliveryForm({...deliveryForm, notes: e.target.value})}
                  placeholder="Optional notes"
                />
              </div>
              <div className="flex space-x-2">
                <Button onClick={() => handleDeliveryComplete(selectedStop)} className="flex-1">
                  Complete Delivery
                </Button>
                <Button variant="outline" onClick={() => setSelectedStop(null)}>
                  Cancel
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
