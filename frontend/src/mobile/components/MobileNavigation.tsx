import { useLocation, useNavigate } from 'react-router-dom';
import { Home, Wrench, User, Truck, Route, ClipboardCheck } from 'lucide-react';
import { Button } from '../../components/ui/button';
import { useAuth } from '../../contexts/AuthContext';

export function MobileNavigation() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user } = useAuth();

  const allNavItems = [
    { path: '/mobile/dashboard', icon: Home, label: 'Dashboard', roles: ['manager', 'dispatcher', 'driver', 'technician'] },
    { path: '/mobile/work-orders', icon: Wrench, label: 'Work Orders', roles: ['manager', 'technician'] },
    { path: '/mobile/routes', icon: Route, label: 'Routes', roles: ['manager', 'dispatcher', 'driver'] },
    { path: '/mobile/driver', icon: Truck, label: 'Driver', roles: ['manager', 'driver'] },
    { path: '/mobile/customer', icon: User, label: 'Customer Portal', roles: ['customer'] },
    { path: '/mobile/inspection', icon: ClipboardCheck, label: 'Inspection', roles: ['manager', 'driver', 'technician'] },
    { path: '/mobile/profile', icon: User, label: 'Profile', roles: ['manager', 'dispatcher', 'driver', 'technician', 'customer'] },
  ];

  const getVisibleNavItems = () => {
    const userRole = user?.role?.toLowerCase();
    if (!userRole) return allNavItems;

    return allNavItems.filter(item => item.roles.includes(userRole));
  };

  const navItems = getVisibleNavItems();

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 px-2 py-2">
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
                isActive ? 'text-blue-600' : 'text-gray-500'
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
