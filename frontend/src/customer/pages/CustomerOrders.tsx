import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge } from '../../components/ui/badge';
import { Input } from '../../components/ui/input';
import { Eye } from 'lucide-react';

interface OrderItem {
  productId: string;
  productName: string;
  quantity: number;
  unitPrice: number;
  totalPrice: number;
}

interface CustomerOrder {
  id: string;
  customerId: string;
  orderDate: string;
  requestedDeliveryDate: string;
  status: string;
  items: OrderItem[];
  subtotal: number;
  tax: number;
  deliveryFee: number;
  totalAmount: number;
  deliveryAddress: string;
  specialInstructions: string;
  paymentMethod: string;
  paymentStatus: string;
  invoiceNumber?: string;
}

const sampleProducts = [
  { id: 'ice-5lb', name: '5lb Ice Bag', price: 2.50 },
  { id: 'ice-10lb', name: '10lb Ice Bag', price: 4.00 },
  { id: 'ice-20lb', name: '20lb Ice Bag', price: 7.50 }
];

export function CustomerOrders() {
  const [orders, setOrders] = useState<CustomerOrder[]>([]);
  const [newOrder, setNewOrder] = useState({
    items: [] as OrderItem[],
    deliveryAddress: '',
    specialInstructions: '',
    requestedDeliveryDate: ''
  });

  useEffect(() => {
    const mockOrders: CustomerOrder[] = [
      {
        id: 'order-001',
        customerId: 'cust-001',
        orderDate: '2024-01-15',
        requestedDeliveryDate: '2024-01-16',
        status: 'delivered',
        items: [
          { productId: 'ice-10lb', productName: '10lb Ice Bag', quantity: 5, unitPrice: 4.00, totalPrice: 20.00 }
        ],
        subtotal: 20.00,
        tax: 1.80,
        deliveryFee: 25.00,
        totalAmount: 46.80,
        deliveryAddress: '123 Main St, Lake Charles, LA',
        specialInstructions: '',
        paymentMethod: 'credit',
        paymentStatus: 'paid',
        invoiceNumber: 'INV-001'
      }
    ];
    setOrders(mockOrders);

    setNewOrder(prev => ({
      ...prev,
      deliveryAddress: '123 Main St, Lake Charles, LA',
      items: sampleProducts.map(p => ({
        productId: p.id,
        productName: p.name,
        quantity: 0,
        unitPrice: p.price,
        totalPrice: 0
      }))
    }));
  }, []);

  const calculateOrderTotal = () => {
    return newOrder.items.reduce((total: number, item: OrderItem) => total + item.totalPrice, 0);
  };

  const updateOrderItem = (productId: string, quantity: number) => {
    setNewOrder(prev => ({
      ...prev,
      items: prev.items.map((item: OrderItem) => 
        item.productId === productId 
          ? { ...item, quantity, totalPrice: quantity * item.unitPrice }
          : item
      )
    }));
  };

  const submitOrder = () => {
    const orderItems = newOrder.items.filter((item: OrderItem) => item.quantity > 0);
    if (orderItems.length === 0) {
      alert('Please add at least one item to your order');
      return;
    }

    const subtotal = calculateOrderTotal();
    const tax = subtotal * 0.09;
    const deliveryFee = 25.00;
    const totalAmount = subtotal + tax + deliveryFee;

    const order: CustomerOrder = {
      id: `order-${Date.now()}`,
      customerId: 'cust-001',
      orderDate: new Date().toISOString().split('T')[0],
      requestedDeliveryDate: newOrder.requestedDeliveryDate,
      status: 'pending',
      items: orderItems,
      subtotal,
      tax,
      deliveryFee,
      totalAmount,
      deliveryAddress: newOrder.deliveryAddress,
      specialInstructions: newOrder.specialInstructions,
      paymentMethod: 'credit',
      paymentStatus: 'pending'
    };

    setOrders(prev => [order, ...prev]);
    setNewOrder(prev => ({
      ...prev,
      items: prev.items.map((item: OrderItem) => ({ ...item, quantity: 0, totalPrice: 0 })),
      specialInstructions: '',
      requestedDeliveryDate: ''
    }));
    
    alert('Order submitted successfully!');
  };

  return (
    <div className="p-4 space-y-4">
      <div>
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Orders</h2>
      </div>

      <Card className="dark:bg-gray-800 dark:border-gray-700">
        <CardHeader>
          <CardTitle className="text-gray-900 dark:text-white">Place New Order</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1 text-gray-900 dark:text-white">Delivery Address</label>
            <Input
              value={newOrder.deliveryAddress}
              onChange={(e) => setNewOrder(prev => ({ ...prev, deliveryAddress: e.target.value }))}
              placeholder="Enter delivery address"
              autoComplete="street-address"
              className="dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1 text-gray-900 dark:text-white">Requested Delivery Date</label>
            <Input
              type="date"
              value={newOrder.requestedDeliveryDate}
              onChange={(e) => setNewOrder(prev => ({ ...prev, requestedDeliveryDate: e.target.value }))}
              autoComplete="off"
              className="dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            />
          </div>

          <div className="space-y-3">
            <h4 className="font-medium text-gray-900 dark:text-white">Products</h4>
            {newOrder.items.map((item: OrderItem) => (
              <div key={item.productId} className="flex items-center justify-between p-3 border dark:border-gray-600 rounded-lg">
                <div className="flex-1">
                  <p className="font-medium text-gray-900 dark:text-white">{item.productName}</p>
                  <p className="text-sm text-gray-600 dark:text-gray-300">${item.unitPrice.toFixed(2)} each</p>
                </div>
                <div className="flex items-center space-x-2">
                  <Input
                    type="number"
                    min="0"
                    value={item.quantity}
                    autoComplete="off"
                    onChange={(e) => updateOrderItem(item.productId, parseInt(e.target.value) || 0)}
                    className="w-20 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  />
                  <span className="text-sm font-medium w-16 text-right text-gray-900 dark:text-white">
                    ${item.totalPrice.toFixed(2)}
                  </span>
                </div>
              </div>
            ))}
          </div>

          <div>
            <label className="block text-sm font-medium mb-1 text-gray-900 dark:text-white">Special Instructions</label>
            <Input
              value={newOrder.specialInstructions}
              onChange={(e) => setNewOrder(prev => ({ ...prev, specialInstructions: e.target.value }))}
              placeholder="Any special delivery instructions"
              autoComplete="off"
              className="dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            />
          </div>

          <div className="border-t dark:border-gray-600 pt-3">
            <div className="flex justify-between text-lg font-semibold text-gray-900 dark:text-white">
              <span>Total:</span>
              <span>${(calculateOrderTotal() * 1.09 + 25).toFixed(2)}</span>
            </div>
            <p className="text-xs text-gray-500 dark:text-gray-400">Includes tax and delivery fee</p>
          </div>

          <Button className="w-full" onClick={submitOrder}>
            Submit Order
          </Button>
        </CardContent>
      </Card>

      <Card className="dark:bg-gray-800 dark:border-gray-700">
        <CardHeader>
          <CardTitle className="text-gray-900 dark:text-white">Recent Orders</CardTitle>
        </CardHeader>
        <CardContent>
          {orders.length === 0 ? (
            <p className="text-center text-gray-500 dark:text-gray-400 py-4">No orders yet</p>
          ) : (
            <div className="space-y-3">
              {orders.map((order) => (
                <div key={order.id} className="border dark:border-gray-600 rounded-lg p-3">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <p className="font-medium text-gray-900 dark:text-white">Order #{order.invoiceNumber || order.id}</p>
                      <p className="text-sm text-gray-600 dark:text-gray-300">{order.orderDate}</p>
                    </div>
                    <Badge variant={order.status === 'delivered' ? 'default' : 'secondary'}>
                      {order.status}
                    </Badge>
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-300 mb-2">{order.items.length} items</p>
                  <div className="flex justify-between items-center">
                    <span className="font-medium text-gray-900 dark:text-white">${order.totalAmount.toFixed(2)}</span>
                    <Button size="sm" variant="outline">
                      <Eye className="w-4 h-4 mr-1" />
                      View
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
