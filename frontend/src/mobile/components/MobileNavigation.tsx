import { useLocation, useNavigate } from 'react-router-dom';
import { Home, Wrench, User, Truck } from 'lucide-react';
import { Button } from '../../components/ui/button';

export function MobileNavigation() {
  const location = useLocation();
  const navigate = useNavigate();

  const navItems = [
    { path: '/mobile/dashboard', icon: Home, label: 'Dashboard' },
    { path: '/mobile/work-orders', icon: Wrench, label: 'Work Orders' },
    { path: '/mobile/driver', icon: Truck, label: 'Driver' },
    { path: '/mobile/profile', icon: User, label: 'Profile' },
  ];

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 px-4 py-2">
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
              className={`flex flex-col items-center space-y-1 p-2 ${
                isActive ? 'text-blue-600' : 'text-gray-500'
              }`}
            >
              <Icon className="h-5 w-5" />
              <span className="text-xs">{item.label}</span>
            </Button>
          );
        })}
      </div>
    </nav>
  );
}
