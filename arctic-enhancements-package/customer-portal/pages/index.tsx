import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Package, Clock, MapPin, DollarSign } from 'lucide-react';
import { config } from '../src/lib/config';

interface CustomerOrder {
  id: string;
  order_date: string;
  status: string;
  total_amount: number;
  delivery_address: string;
  items: Array<{
    product_type: string;
    quantity: number;
    unit_price: number;
  }>;
}

export default function CustomerPortal() {
  const [orders, setOrders] = useState<CustomerOrder[]>([]);
  const [loading, setLoading] = useState(true);
  const [customer, setCustomer] = useState<any>(null);

  useEffect(() => {
    const fetchCustomerData = async () => {
      try {
        const token = localStorage.getItem('arctic_auth_token');
        const response = await fetch(`${config.api.baseURL}/customers/me`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            ...config.api.headers
          }
        });
        
        if (response.ok) {
          const customerData = await response.json();
          setCustomer(customerData);
          
          const ordersResponse = await fetch(`${config.api.baseURL}/customers/${customerData.id}/orders`, {
            headers: {
              'Authorization': `Bearer ${token}`,
              ...config.api.headers
            }
          });
          
          if (ordersResponse.ok) {
            const ordersData = await ordersResponse.json();
            setOrders(ordersData);
          }
        }
      } catch (error) {
        console.error('Failed to fetch customer data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchCustomerData();
  }, []);

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
        return 'bg-green-500';
      case 'in-progress':
        return 'bg-blue-500';
      case 'pending':
        return 'bg-yellow-500';
      default:
        return 'bg-gray-500';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading your orders...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Customer Portal</h1>
        <p className="text-muted-foreground">
          Welcome back, {customer?.name || 'Customer'}! Manage your orders and account.
        </p>
      </div>

      {customer && (
        <Card>
          <CardHeader>
            <CardTitle>Account Overview</CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex items-center space-x-2">
              <Package className="h-5 w-5 text-blue-600" />
              <div>
                <p className="text-sm text-muted-foreground">Total Orders</p>
                <p className="text-2xl font-bold">{orders.length}</p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <DollarSign className="h-5 w-5 text-green-600" />
              <div>
                <p className="text-sm text-muted-foreground">Account Balance</p>
                <p className="text-2xl font-bold">${customer.balance || '0.00'}</p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <Clock className="h-5 w-5 text-orange-600" />
              <div>
                <p className="text-sm text-muted-foreground">Last Order</p>
                <p className="text-sm">{orders[0]?.order_date ? new Date(orders[0].order_date).toLocaleDateString() : 'No orders'}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      <div>
        <h2 className="text-2xl font-bold mb-4">Recent Orders</h2>
        <div className="grid gap-4">
          {orders.length === 0 ? (
            <Card>
              <CardContent className="p-8 text-center">
                <Package className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">No Orders Yet</h3>
                <p className="text-muted-foreground mb-4">
                  Start by placing your first ice delivery order
                </p>
                <Button>Place New Order</Button>
              </CardContent>
            </Card>
          ) : (
            orders.map((order) => (
              <Card key={order.id}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">Order #{order.id}</CardTitle>
                    <Badge className={getStatusColor(order.status)}>
                      {order.status}
                    </Badge>
                  </div>
                  <CardDescription>
                    Ordered on {new Date(order.order_date).toLocaleDateString()}
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center space-x-2">
                    <MapPin className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm">{order.delivery_address}</span>
                  </div>
                  
                  <div className="space-y-2">
                    <h4 className="font-semibold">Items:</h4>
                    {order.items?.map((item, index) => (
                      <div key={index} className="flex justify-between text-sm">
                        <span>{item.quantity}x {item.product_type}</span>
                        <span>${(item.quantity * item.unit_price).toFixed(2)}</span>
                      </div>
                    ))}
                  </div>
                  
                  <div className="flex justify-between items-center pt-2 border-t">
                    <span className="font-semibold">Total: ${order.total_amount.toFixed(2)}</span>
                    <Button variant="outline" size="sm">
                      View Details
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
