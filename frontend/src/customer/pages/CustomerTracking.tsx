import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';
import { Truck } from 'lucide-react';

interface CustomerOrder {
  id: string;
  invoiceNumber?: string;
  requestedDeliveryDate: string;
  status: string;
  trackingInfo?: {
    driverName: string;
    estimatedArrival: string;
    vehicleId: string;
  };
}

export function CustomerTracking() {
  const [orders, setOrders] = useState<CustomerOrder[]>([]);

  useEffect(() => {
    const mockOrders: CustomerOrder[] = [
      {
        id: 'order-002',
        invoiceNumber: 'INV-002',
        requestedDeliveryDate: '2024-01-17',
        status: 'out-for-delivery',
        trackingInfo: {
          driverName: 'John Smith',
          estimatedArrival: '2:30 PM',
          vehicleId: 'TRUCK-001'
        }
      },
      {
        id: 'order-003',
        invoiceNumber: 'INV-003',
        requestedDeliveryDate: '2024-01-18',
        status: 'in-production',
      }
    ];
    setOrders(mockOrders);

    const interval = setInterval(() => {
      setOrders(prevOrders => 
        prevOrders.map(order => ({
          ...order,
          trackingInfo: order.trackingInfo ? {
            ...order.trackingInfo,
            estimatedArrival: new Date(Date.now() + Math.random() * 3600000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
          } : undefined
        }))
      );
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="p-4 space-y-4">
      <div>
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Track Deliveries</h2>
      </div>

      <Card className="dark:bg-gray-800 dark:border-gray-700">
        <CardHeader>
          <CardTitle className="flex items-center text-gray-900 dark:text-white">
            <Truck className="w-5 h-5 mr-2" />
            Track Your Deliveries
          </CardTitle>
        </CardHeader>
        <CardContent>
          {orders.filter(o => ['confirmed', 'in-production', 'out-for-delivery'].includes(o.status)).length === 0 ? (
            <p className="text-center text-gray-500 dark:text-gray-400 py-4">No active deliveries to track</p>
          ) : (
            <div className="space-y-3">
              {orders
                .filter(o => ['confirmed', 'in-production', 'out-for-delivery'].includes(o.status))
                .map((order) => (
                  <div key={order.id} className="border dark:border-gray-600 rounded-lg p-3">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <p className="font-medium text-gray-900 dark:text-white">Order #{order.invoiceNumber || order.id}</p>
                        <p className="text-sm text-gray-600 dark:text-gray-300">{order.requestedDeliveryDate}</p>
                      </div>
                      <Badge>{order.status}</Badge>
                    </div>
                    {order.trackingInfo && (
                      <div className="mt-2 p-2 bg-blue-50 dark:bg-blue-900/20 rounded">
                        <p className="text-sm text-gray-900 dark:text-white"><strong>Driver:</strong> {order.trackingInfo.driverName}</p>
                        <p className="text-sm text-gray-900 dark:text-white"><strong>ETA:</strong> {order.trackingInfo.estimatedArrival}</p>
                        <p className="text-sm text-gray-900 dark:text-white"><strong>Vehicle:</strong> {order.trackingInfo.vehicleId}</p>
                      </div>
                    )}
                  </div>
                ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
