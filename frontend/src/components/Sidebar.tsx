import { Link, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Package, 
  Truck, 
  Users, 
  DollarSign, 
  Settings,
  Snowflake,
  Wrench,
  Factory
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { usePR } from '../contexts/PRContext';

export function Sidebar() {
  const { user } = useAuth();
  const { getNavigationPath } = usePR();
  const location = useLocation();

  const menuItems = [
    { path: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { path: '/production-inventory', icon: Package, label: 'Production & Inventory' },
    { path: '/fleet', icon: Truck, label: 'Fleet & Routes' },
    { path: '/customers', icon: Users, label: 'Customer Management' },
    { path: '/maintenance', icon: Wrench, label: 'Maintenance' },
    { path: '/production', icon: Factory, label: 'Production Manager' },
    { path: '/financial', icon: DollarSign, label: 'Financial' },
    { path: '/settings', icon: Settings, label: 'Settings' },
  ];

  const getVisibleMenuItems = () => {
    const role = user?.role?.toLowerCase();
    
    if (role === 'manager') {
      return menuItems;
    }
    
    if (role === 'dispatcher') {
      return menuItems.filter(item => 
        ['dashboard', 'fleet', 'customers'].includes(item.path.substring(1))
      );
    }
    
    if (role === 'accountant') {
      return menuItems.filter(item => 
        ['dashboard', 'financial'].includes(item.path.substring(1))
      );
    }
    
    if (role === 'driver') {
      return menuItems.filter(item => 
        ['dashboard', 'fleet'].includes(item.path.substring(1))
      );
    }
    
    return menuItems;
  };

  const getLocationName = (locationId: string) => {
    const locationMap: { [key: string]: string } = {
      'loc_1': 'Leesville HQ',
      'loc_2': 'Lake Charles',
      'loc_3': 'Lufkin',
      'loc_4': 'Jasper'
    };
    return locationMap[locationId] || locationId;
  };

  const visibleMenuItems = getVisibleMenuItems();

  return (
    <div className="bg-blue-900 text-white w-64 min-h-screen p-4">
      <div className="flex items-center mb-8">
        <Snowflake className="h-8 w-8 mr-3" />
        <div>
          <h1 className="text-xl font-bold">Arctic Ice</h1>
          <p className="text-blue-200 text-sm">Solutions</p>
        </div>
      </div>

      <div className="mb-6 p-3 bg-blue-800 rounded-lg">
        <p className="text-sm text-blue-200">Logged in as</p>
        <p className="font-semibold">{user?.full_name}</p>
        <p className="text-sm text-blue-200">
          {user?.role} • {user?.location_id ? getLocationName(user.location_id) : 'Unknown'}
        </p>
      </div>

      <nav>
        <ul className="space-y-2">
          {visibleMenuItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            
            return (
              <li key={item.path}>
                <Link
                  to={getNavigationPath(item.path)}
                  className={`flex items-center p-3 rounded-lg transition-colors ${
                    isActive 
                      ? 'bg-blue-700 text-white' 
                      : 'text-blue-100 hover:bg-blue-800'
                  }`}
                >
                  <Icon className="h-5 w-5 mr-3" />
                  {item.label}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>
    </div>
  );
}
