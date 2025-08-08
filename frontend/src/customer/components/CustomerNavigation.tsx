import { useLocation, useNavigate } from 'react-router-dom';
import { Home, ShoppingCart, Truck, DollarSign, MessageSquare } from 'lucide-react';
import { Button } from '../../components/ui/button';

export function CustomerNavigation() {
  const location = useLocation();
  const navigate = useNavigate();

  const navItems = [
    { path: '/customer/dashboard', icon: Home, label: 'Dashboard' },
    { path: '/customer/orders', icon: ShoppingCart, label: 'Orders' },
    { path: '/customer/tracking', icon: Truck, label: 'Track' },
    { path: '/customer/billing', icon: DollarSign, label: 'Billing' },
    { path: '/customer/feedback', icon: MessageSquare, label: 'Feedback' }
  ];

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 px-2 py-2">
      <div className="flex justify-around">
        {navItems.map((item) => {
          const isActive = location.pathname === item.path;
          const Icon = item.icon;
          
          return (
            <Button
              key={item.path}
              variant="ghost"
              size="sm"
              onClick={() => navigate(item.path)}
              className={`flex flex-col items-center space-y-1 p-2 min-w-0 flex-1 ${
                isActive ? 'text-blue-600 dark:text-blue-400' : 'text-gray-500 dark:text-gray-400'
              }`}
            >
              <Icon className="h-4 w-4" />
              <span className="text-xs truncate">{item.label}</span>
            </Button>
          );
        })}
      </div>
    </nav>
  );
}
