import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Package, Plus, Truck, DollarSign } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

interface CustomerUser {
  id: string;
  name: string;
  company: string;
  creditLimit: number;
  accountBalance: number;
  creditTerms: string;
}

export function CustomerDashboard() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [currentUser, setCurrentUser] = useState<CustomerUser | null>(null);
  const [orderCount, setOrderCount] = useState(0);

  useEffect(() => {
    const mockUser: CustomerUser = {
      id: user?.id || 'cust-001',
      name: user?.full_name || 'Customer User',
      company: 'Sample Company',
      creditLimit: 50000,
      accountBalance: 2500.00,
      creditTerms: 'Net 30'
    };
    setCurrentUser(mockUser);
    setOrderCount(12);
  }, [user]);

  if (!currentUser) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-xl font-semibold mb-2 text-gray-900 dark:text-white">Loading...</h2>
          <p className="text-gray-600 dark:text-gray-300">Please wait while we load your account</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 space-y-4">
      <div>
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Customer Dashboard</h2>
      </div>

      <Card className="dark:bg-gray-800 dark:border-gray-700">
        <CardHeader>
          <CardTitle className="flex items-center text-gray-900 dark:text-white">
            <Package className="w-5 h-5 mr-2" />
            Account Overview
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="text-center p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
              <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">{orderCount}</p>
              <p className="text-sm text-gray-600 dark:text-gray-300">Total Orders</p>
            </div>
            <div className="text-center p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
              <p className="text-2xl font-bold text-green-600 dark:text-green-400">${currentUser.accountBalance.toFixed(2)}</p>
              <p className="text-sm text-gray-600 dark:text-gray-300">Balance</p>
            </div>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-sm text-gray-600 dark:text-gray-300">Credit Terms:</span>
              <span className="text-sm font-medium text-gray-900 dark:text-white">{currentUser.creditTerms}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600 dark:text-gray-300">Credit Limit:</span>
              <span className="text-sm font-medium text-gray-900 dark:text-white">${currentUser.creditLimit.toLocaleString()}</span>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card className="dark:bg-gray-800 dark:border-gray-700">
        <CardHeader>
          <CardTitle className="text-gray-900 dark:text-white">Quick Actions</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          <Button className="w-full" onClick={() => navigate('/customer/orders')}>
            <Plus className="w-4 h-4 mr-2" />
            Place New Order
          </Button>
          <Button variant="outline" className="w-full" onClick={() => navigate('/customer/tracking')}>
            <Truck className="w-4 h-4 mr-2" />
            Track Deliveries
          </Button>
          <Button variant="outline" className="w-full" onClick={() => navigate('/customer/billing')}>
            <DollarSign className="w-4 h-4 mr-2" />
            View Invoices
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
