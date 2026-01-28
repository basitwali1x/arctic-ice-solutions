import { useLocation, useNavigate } from 'react-router-dom';
import { Home, User, Truck, Route, ClipboardCheck } from 'lucide-react';
import { Button } from '../../components/ui/button';
import { useAuth } from '../../contexts/AuthContext';
import { usePR } from '../../contexts/PRContext';

export function MobileNavigation() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user } = useAuth();
  const { getNavigationPath } = usePR();

  const allNavItems = [
    { path: '/mobile/dashboard', icon: Home, label: 'HUB', roles: ['manager', 'dispatcher', 'driver', 'technician'] },
    { path: '/mobile/routes', icon: Route, label: 'MAP', roles: ['manager', 'dispatcher', 'driver'] },
    { path: '/mobile/driver', icon: Truck, label: 'MISSION', roles: ['manager', 'driver'] },
    { path: '/mobile/inspection', icon: ClipboardCheck, label: 'GEAR', roles: ['manager', 'driver', 'technician'] },
    { path: '/mobile/profile', icon: User, label: 'USER', roles: ['manager', 'dispatcher', 'driver', 'technician'] },
  ];

  const getVisibleNavItems = () => {
    const userRole = user?.role?.toLowerCase();
    if (!userRole) return allNavItems;

    return allNavItems.filter(item => item.roles.includes(item.roles.includes('all') ? 'all' : userRole));
  };

  // Simplified filter for safety
  const navItems = allNavItems.filter(item =>
    item.roles.includes('all') ||
    item.roles.includes(user?.role?.toLowerCase() || '')
  );

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-[#020617]/90 backdrop-blur-xl border-t border-slate-800 px-4 py-3 z-50 shadow-[0_-10px_30px_rgba(0,0,0,0.5)]">
      <div className="flex justify-around items-center">
        {navItems.map((item) => {
          const isActive = location.pathname.includes(item.path);
          const Icon = item.icon;

          return (
            <Button
              key={item.path}
              variant="ghost"
              size="sm"
              onClick={() => navigate(getNavigationPath(item.path))}
              className={`flex flex-col items-center justify-center space-y-1 p-0 h-10 min-w-[64px] rounded-xl transition-all duration-300 relative ${isActive ? 'text-blue-500 scale-110' : 'text-slate-500 hover:text-slate-300'
                }`}
            >
              {isActive && (
                <div className="absolute -top-3 w-8 h-1 bg-blue-500 rounded-full shadow-[0_0_10px_#3b82f6]" />
              )}
              <Icon className={`h-5 w-5 ${isActive ? 'stroke-[2.5px]' : 'stroke-2'}`} />
              <span className="text-[9px] font-black uppercase tracking-widest">{item.label}</span>
            </Button>
          );
        })}
      </div>
    </nav>
  );
}
