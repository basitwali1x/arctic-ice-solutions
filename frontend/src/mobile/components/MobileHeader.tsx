import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Bell, Menu, X } from 'lucide-react';
import { Button } from '../../components/ui/button';
import { Badge } from '../../components/ui/badge';
import { Card, CardContent } from '../../components/ui/card';
import { useAuth } from '../../contexts/AuthContext';

interface MobileHeaderProps {
  currentUser: {
    name: string;
    role: string;
    location: string;
  };
}

export function MobileHeader({ currentUser }: MobileHeaderProps) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [showMenu, setShowMenu] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);

  const notifications = [
    { id: 1, title: 'Work Order Approved', message: 'TX-ICE-01 maintenance approved', time: '5 min ago' },
    { id: 2, title: 'New Route Assignment', message: 'Route 3 assigned for today', time: '1 hour ago' },
    { id: 3, title: 'Vehicle Check Required', message: 'LA-ICE-02 needs inspection', time: '2 hours ago' }
  ];

  return (
    <>
      <header className="bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between relative z-50">
        <div className="flex items-center space-x-3">
          <Button 
            variant="ghost" 
            size="sm" 
            className="p-2"
            onClick={() => setShowMenu(!showMenu)}
          >
            <Menu className="h-5 w-5" />
          </Button>
          <div>
            <h1 className="text-lg font-semibold text-gray-900">Arctic Ice</h1>
            <p className="text-xs text-gray-500">{currentUser.name}</p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <Button 
            variant="ghost" 
            size="sm" 
            className="relative p-2"
            onClick={() => setShowNotifications(!showNotifications)}
          >
            <Bell className="h-5 w-5" />
            <Badge className="absolute -top-1 -right-1 h-5 w-5 rounded-full p-0 flex items-center justify-center text-xs bg-red-500">
              {notifications.length}
            </Badge>
          </Button>
        </div>
      </header>

      {/* Side Menu */}
      {showMenu && (
        <div className="fixed inset-0 z-40 bg-black bg-opacity-50" onClick={() => setShowMenu(false)}>
          <div className="fixed left-0 top-0 h-full w-64 bg-white shadow-lg" onClick={(e) => e.stopPropagation()}>
            <div className="p-4 border-b">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold">Menu</h2>
                <Button variant="ghost" size="sm" onClick={() => setShowMenu(false)}>
                  <X className="h-5 w-5" />
                </Button>
              </div>
            </div>
            <div className="p-4 space-y-2">
              <Button variant="ghost" className="w-full justify-start" onClick={() => { navigate('/mobile/dashboard'); setShowMenu(false); }}>
                Dashboard
              </Button>
              {(user?.role === 'technician' || user?.role === 'manager') && (
                <Button variant="ghost" className="w-full justify-start" onClick={() => { navigate('/mobile/work-orders'); setShowMenu(false); }}>
                  Work Orders
                </Button>
              )}
              {(user?.role === 'driver' || user?.role === 'dispatcher' || user?.role === 'manager') && (
                <Button variant="ghost" className="w-full justify-start" onClick={() => { navigate('/mobile/routes'); setShowMenu(false); }}>
                  Routes and Deliveries
                </Button>
              )}
              {(user?.role === 'driver' || user?.role === 'manager') && (
                <Button variant="ghost" className="w-full justify-start" onClick={() => { navigate('/mobile/driver'); setShowMenu(false); }}>
                  Driver Dashboard
                </Button>
              )}
              {(user?.role === 'customer' || user?.role === 'manager') && (
                <Button variant="ghost" className="w-full justify-start" onClick={() => { navigate('/mobile/customer'); setShowMenu(false); }}>
                  Customer Portal
                </Button>
              )}
              {(user?.role === 'driver' || user?.role === 'technician' || user?.role === 'manager') && (
                <Button variant="ghost" className="w-full justify-start" onClick={() => { navigate('/mobile/inspection'); setShowMenu(false); }}>
                  Pre-Trip Inspection
                </Button>
              )}
              <Button variant="ghost" className="w-full justify-start" onClick={() => { navigate('/mobile/profile'); setShowMenu(false); }}>
                Profile
              </Button>
              <Button variant="ghost" className="w-full justify-start" onClick={() => { navigate('/mobile/settings'); setShowMenu(false); }}>
                Settings
              </Button>
              <hr className="my-2" />
              <Button variant="ghost" className="w-full justify-start text-red-600" onClick={() => { logout(); setShowMenu(false); }}>
                Sign Out
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Notifications Panel */}
      {showNotifications && (
        <div className="fixed inset-0 z-40 bg-black bg-opacity-50" onClick={() => setShowNotifications(false)}>
          <div className="fixed right-0 top-0 h-full w-80 bg-white shadow-lg" onClick={(e) => e.stopPropagation()}>
            <div className="p-4 border-b">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold">Notifications</h2>
                <Button variant="ghost" size="sm" onClick={() => setShowNotifications(false)}>
                  <X className="h-5 w-5" />
                </Button>
              </div>
            </div>
            <div className="p-4 space-y-3">
              {notifications.map((notification) => (
                <Card key={notification.id}>
                  <CardContent className="p-3">
                    <h3 className="font-medium text-sm">{notification.title}</h3>
                    <p className="text-xs text-gray-600 mt-1">{notification.message}</p>
                    <p className="text-xs text-gray-400 mt-2">{notification.time}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
