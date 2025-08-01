import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge } from '../../components/ui/badge';
import { Input } from '../../components/ui/input';
import { 
  ShoppingCart, 
  Package,
  Star,
  DollarSign,
  MessageSquare,
  Truck,
  Plus,
  Eye,
  Download,
  Send
} from 'lucide-react';
import { CustomerUser, CustomerOrder, CustomerFeedback, Invoice, OrderItem } from '../../types/api';
import { customerUsers, products, sampleOrders, sampleFeedback, sampleInvoices } from '../../lib/customerData';

interface CustomerAppProps {
  customerId?: string;
}

export function MobileCustomer({ 
  customerId = 'cust-001'
}: CustomerAppProps) {
  const [currentUser, setCurrentUser] = useState<CustomerUser | null>(null);
  const [currentView, setCurrentView] = useState<'home' | 'orders' | 'track' | 'billing' | 'feedback'>('home');
  const [orders, setOrders] = useState<CustomerOrder[]>([]);
  const [feedback, setFeedback] = useState<CustomerFeedback[]>([]);
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [newOrder, setNewOrder] = useState({
    items: [] as OrderItem[],
    deliveryAddress: '',
    specialInstructions: '',
    requestedDeliveryDate: ''
  });
  const [newFeedback, setNewFeedback] = useState({
    type: 'delivery' as const,
    rating: 5 as const,
    subject: '',
    message: '',
    orderId: ''
  });

  useEffect(() => {
    const user = customerUsers.find(u => u.id === customerId);
    if (user) {
      setCurrentUser(user);
      setOrders(sampleOrders.filter(o => o.customerId === customerId));
      setFeedback(sampleFeedback.filter(f => f.customerId === customerId));
      setInvoices(sampleInvoices.filter(i => i.customerId === customerId));
      setNewOrder(prev => ({
        ...prev,
        deliveryAddress: user.address,
        items: products.map(p => ({
          productId: p.id,
          productName: p.name,
          quantity: 0,
          unitPrice: p.price,
          totalPrice: 0
        }))
      }));
    }
  }, [customerId]);

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
      customerId: customerId,
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
    setCurrentView('orders');
  };

  const submitFeedback = () => {
    if (!newFeedback.subject || !newFeedback.message) {
      alert('Please fill in all feedback fields');
      return;
    }

    const feedback: CustomerFeedback = {
      id: `feedback-${Date.now()}`,
      customerId: customerId,
      orderId: newFeedback.orderId || undefined,
      type: newFeedback.type,
      rating: newFeedback.rating,
      subject: newFeedback.subject,
      message: newFeedback.message,
      submittedAt: new Date().toISOString(),
      status: 'new'
    };

    setFeedback(prev => [feedback, ...prev]);
    setNewFeedback({
      type: 'delivery',
      rating: 5,
      subject: '',
      message: '',
      orderId: ''
    });
    
    alert('Feedback submitted successfully!');
  };

  const handleDownloadInvoice = async (invoiceId: string) => {
    try {
      const response = await fetch(`/api/invoices/${invoiceId}/download`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to download invoice');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `invoice_${invoiceId}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading invoice:', error);
      alert('Failed to download invoice. Please try again.');
    }
  };

  if (!currentUser) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-xl font-semibold mb-2">Loading...</h2>
          <p className="text-gray-600">Please wait while we load your account</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 px-4 py-3">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-lg font-semibold text-gray-900">Arctic Ice Solutions</h1>
            <p className="text-sm text-gray-600">{currentUser.name}</p>
          </div>
          <div className="text-right">
            <p className="text-sm font-medium">{currentUser.company}</p>
            <p className="text-xs text-gray-500">Credit: ${currentUser.creditLimit.toLocaleString()}</p>
          </div>
        </div>
      </header>

      <nav className="bg-white border-b border-gray-200 px-4 py-2">
        <div className="flex space-x-1 overflow-x-auto">
          {[
            { key: 'home', label: 'Dashboard', icon: Package },
            { key: 'orders', label: 'Orders', icon: ShoppingCart },
            { key: 'track', label: 'Track', icon: Truck },
            { key: 'billing', label: 'Billing', icon: DollarSign },
            { key: 'feedback', label: 'Feedback', icon: MessageSquare }
          ].map(({ key, label, icon: Icon }) => (
            <Button
              key={key}
              variant={currentView === key ? "default" : "ghost"}
              size="sm"
              className="flex-shrink-0"
              onClick={() => setCurrentView(key as 'home' | 'orders' | 'track' | 'billing' | 'feedback')}
            >
              <Icon className="w-4 h-4 mr-1" />
              {label}
            </Button>
          ))}
        </div>
      </nav>

      <main className="p-4 space-y-4">
        {currentView === 'home' && (
          <div className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Package className="w-5 h-5 mr-2" />
                  Account Overview
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center p-3 bg-blue-50 rounded-lg">
                    <p className="text-2xl font-bold text-blue-600">{orders.length}</p>
                    <p className="text-sm text-gray-600">Total Orders</p>
                  </div>
                  <div className="text-center p-3 bg-green-50 rounded-lg">
                    <p className="text-2xl font-bold text-green-600">${currentUser.accountBalance.toFixed(2)}</p>
                    <p className="text-sm text-gray-600">Balance</p>
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Credit Terms:</span>
                    <span className="text-sm font-medium">{currentUser.creditTerms}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Credit Limit:</span>
                    <span className="text-sm font-medium">${currentUser.creditLimit.toLocaleString()}</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <Button className="w-full" onClick={() => setCurrentView('orders')}>
                  <Plus className="w-4 h-4 mr-2" />
                  Place New Order
                </Button>
                <Button variant="outline" className="w-full" onClick={() => setCurrentView('track')}>
                  <Truck className="w-4 h-4 mr-2" />
                  Track Deliveries
                </Button>
                <Button variant="outline" className="w-full" onClick={() => setCurrentView('billing')}>
                  <DollarSign className="w-4 h-4 mr-2" />
                  View Invoices
                </Button>
              </CardContent>
            </Card>
          </div>
        )}

        {currentView === 'orders' && (
          <div className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Place New Order</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Delivery Address</label>
                  <Input
                    value={newOrder.deliveryAddress}
                    onChange={(e) => setNewOrder(prev => ({ ...prev, deliveryAddress: e.target.value }))}
                    placeholder="Enter delivery address"
                    autoComplete="street-address"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium mb-1">Requested Delivery Date</label>
                  <Input
                    type="date"
                    value={newOrder.requestedDeliveryDate}
                    onChange={(e) => setNewOrder(prev => ({ ...prev, requestedDeliveryDate: e.target.value }))}
                    autoComplete="off"
                  />
                </div>

                <div className="space-y-3">
                  <h4 className="font-medium">Products</h4>
                  {newOrder.items.map((item: OrderItem) => (
                    <div key={item.productId} className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex-1">
                        <p className="font-medium">{item.productName}</p>
                        <p className="text-sm text-gray-600">${item.unitPrice.toFixed(2)} each</p>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Input
                          type="number"
                          min="0"
                          value={item.quantity}
                          autoComplete="off"
                          onChange={(e) => updateOrderItem(item.productId, parseInt(e.target.value) || 0)}
                          className="w-20"
                        />
                        <span className="text-sm font-medium w-16 text-right">
                          ${item.totalPrice.toFixed(2)}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">Special Instructions</label>
                  <Input
                    value={newOrder.specialInstructions}
                    onChange={(e) => setNewOrder(prev => ({ ...prev, specialInstructions: e.target.value }))}
                    placeholder="Any special delivery instructions"
                    autoComplete="off"
                  />
                </div>

                <div className="border-t pt-3">
                  <div className="flex justify-between text-lg font-semibold">
                    <span>Total:</span>
                    <span>${(calculateOrderTotal() * 1.09 + 25).toFixed(2)}</span>
                  </div>
                  <p className="text-xs text-gray-500">Includes tax and delivery fee</p>
                </div>

                <Button className="w-full" onClick={submitOrder}>
                  Submit Order
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Recent Orders</CardTitle>
              </CardHeader>
              <CardContent>
                {orders.length === 0 ? (
                  <p className="text-center text-gray-500 py-4">No orders yet</p>
                ) : (
                  <div className="space-y-3">
                    {orders.map((order) => (
                      <div key={order.id} className="border rounded-lg p-3">
                        <div className="flex justify-between items-start mb-2">
                          <div>
                            <p className="font-medium">Order #{order.invoiceNumber || order.id}</p>
                            <p className="text-sm text-gray-600">{order.orderDate}</p>
                          </div>
                          <Badge variant={order.status === 'delivered' ? 'default' : 'secondary'}>
                            {order.status}
                          </Badge>
                        </div>
                        <p className="text-sm text-gray-600 mb-2">{order.items.length} items</p>
                        <div className="flex justify-between items-center">
                          <span className="font-medium">${order.totalAmount.toFixed(2)}</span>
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
        )}

        {currentView === 'track' && (
          <div className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Truck className="w-5 h-5 mr-2" />
                  Track Your Deliveries
                </CardTitle>
              </CardHeader>
              <CardContent>
                {orders.filter(o => ['confirmed', 'in-production', 'out-for-delivery'].includes(o.status)).length === 0 ? (
                  <p className="text-center text-gray-500 py-4">No active deliveries to track</p>
                ) : (
                  <div className="space-y-3">
                    {orders
                      .filter(o => ['confirmed', 'in-production', 'out-for-delivery'].includes(o.status))
                      .map((order) => (
                        <div key={order.id} className="border rounded-lg p-3">
                          <div className="flex justify-between items-start mb-2">
                            <div>
                              <p className="font-medium">Order #{order.invoiceNumber || order.id}</p>
                              <p className="text-sm text-gray-600">{order.requestedDeliveryDate}</p>
                            </div>
                            <Badge>{order.status}</Badge>
                          </div>
                          {order.trackingInfo && (
                            <div className="mt-2 p-2 bg-blue-50 rounded">
                              <p className="text-sm"><strong>Driver:</strong> {order.trackingInfo.driverName}</p>
                              <p className="text-sm"><strong>ETA:</strong> {order.trackingInfo.estimatedArrival}</p>
                            </div>
                          )}
                        </div>
                      ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        )}

        {currentView === 'billing' && (
          <div className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <DollarSign className="w-5 h-5 mr-2" />
                  Invoices & Billing
                </CardTitle>
              </CardHeader>
              <CardContent>
                {invoices.length === 0 ? (
                  <p className="text-center text-gray-500 py-4">No invoices available</p>
                ) : (
                  <div className="space-y-3">
                    {invoices.map((invoice) => (
                      <div key={invoice.id} className="border rounded-lg p-3">
                        <div className="flex justify-between items-start mb-2">
                          <div>
                            <p className="font-medium">Invoice #{invoice.invoiceNumber}</p>
                            <p className="text-sm text-gray-600">Due: {invoice.dueDate}</p>
                          </div>
                          <Badge variant={invoice.status === 'paid' ? 'default' : 'destructive'}>
                            {invoice.status}
                          </Badge>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="font-medium">${invoice.totalAmount.toFixed(2)}</span>
                          <Button size="sm" variant="outline" onClick={() => handleDownloadInvoice(invoice.id)}>
                            <Download className="w-4 h-4 mr-1" />
                            Download
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        )}

        {currentView === 'feedback' && (
          <div className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Submit Feedback</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Feedback Type</label>
                  <select
                    value={newFeedback.type}
                    onChange={(e) => setNewFeedback(prev => ({ ...prev, type: e.target.value as typeof prev.type }))}
                    className="w-full p-2 border rounded-md"
                  >
                    <option value="delivery">Delivery</option>
                    <option value="product">Product Quality</option>
                    <option value="service">Customer Service</option>
                    <option value="complaint">Complaint</option>
                    <option value="suggestion">Suggestion</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">Rating</label>
                  <div className="flex space-x-1">
                    {[1, 2, 3, 4, 5].map((rating) => (
                      <Button
                        key={rating}
                        variant={newFeedback.rating >= rating ? "default" : "outline"}
                        size="sm"
                        onClick={() => setNewFeedback(prev => ({ ...prev, rating: rating as typeof prev.rating }))}
                      >
                        <Star className="w-4 h-4" />
                      </Button>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">Subject</label>
                  <Input
                    value={newFeedback.subject}
                    onChange={(e) => setNewFeedback(prev => ({ ...prev, subject: e.target.value }))}
                    placeholder="Brief subject line"
                    autoComplete="off"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">Message</label>
                  <textarea
                    value={newFeedback.message}
                    onChange={(e) => setNewFeedback(prev => ({ ...prev, message: e.target.value }))}
                    placeholder="Your detailed feedback"
                    className="w-full p-2 border rounded-md h-24"
                  />
                </div>

                <Button className="w-full" onClick={submitFeedback}>
                  <Send className="w-4 h-4 mr-2" />
                  Submit Feedback
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Previous Feedback</CardTitle>
              </CardHeader>
              <CardContent>
                {feedback.length === 0 ? (
                  <p className="text-center text-gray-500 py-4">No feedback submitted yet</p>
                ) : (
                  <div className="space-y-3">
                    {feedback.map((item) => (
                      <div key={item.id} className="border rounded-lg p-3">
                        <div className="flex justify-between items-start mb-2">
                          <div>
                            <p className="font-medium">{item.subject}</p>
                            <div className="flex items-center space-x-1">
                              {[1, 2, 3, 4, 5].map((star) => (
                                <Star
                                  key={star}
                                  className={`w-3 h-3 ${star <= item.rating ? 'text-yellow-400 fill-current' : 'text-gray-300'}`}
                                />
                              ))}
                            </div>
                          </div>
                          <Badge variant={item.status === 'resolved' ? 'default' : 'secondary'}>
                            {item.status}
                          </Badge>
                        </div>
                        <p className="text-sm text-gray-600">{item.message}</p>
                        {item.response && (
                          <div className="mt-2 p-2 bg-green-50 rounded">
                            <p className="text-sm"><strong>Response:</strong> {item.response}</p>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        )}
      </main>
    </div>
  );
}
