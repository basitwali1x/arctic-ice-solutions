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
  UserCircle,
  ChevronRight
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { usePR } from '../contexts/PRContext';

export function Sidebar() {
  const { user } = useAuth();
  const { getNavigationPath } = usePR();
  const location = useLocation();

  const menuItems = [
    { path: '/dashboard', icon: LayoutDashboard, label: 'Overview' },
    { path: '/fleet', icon: Truck, label: 'Routes & Fleet' },
    { path: '/production-inventory', icon: Package, label: 'Inventory' },
    { path: '/customers', icon: Users, label: 'Customers' },
    { path: '/employees', icon: UserCircle, label: 'Employees' },
    { path: '/financial', icon: DollarSign, label: 'Financials' },
    { path: '/maintenance', icon: Wrench, label: 'Maintenance' },
    { path: '/settings', icon: Settings, label: 'Settings' },
  ];

  const getVisibleMenuItems = () => {
    const role = user?.role?.toLowerCase();

    if (role === 'manager') {
      return menuItems;
    }

    if (role === 'dispatcher') {
      return menuItems.filter(item =>
        ['dashboard', 'fleet', 'customers', 'maintenance'].includes(item.path.substring(1))
      );
    }

    if (role === 'accountant') {
      return menuItems.filter(item =>
        ['dashboard', 'financial', 'settings'].includes(item.path.substring(1))
      );
    }

    return menuItems;
  };

  const visibleMenuItems = getVisibleMenuItems();

  return (
    <div className="fixed inset-y-0 left-0 w-64 bg-[#0f172a] border-r border-slate-800 flex flex-col z-50">
      {/* Brand */}
      <div className="p-6 flex items-center space-x-3">
        <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center ice-glow">
          <Snowflake className="h-6 w-6 text-white" />
        </div>
        <div>
          <h1 className="text-lg font-black tracking-tighter text-white uppercase italic">
            Your Choice <span className="text-blue-500">Ice</span>
          </h1>
          <p className="text-[10px] text-slate-500 font-bold tracking-widest uppercase">Operations Control</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 py-4 space-y-1 overflow-y-auto no-scrollbar">
        {visibleMenuItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path || (location.pathname === '/' && item.path === '/dashboard');

          return (
            <Link
              key={item.path}
              to={getNavigationPath(item.path)}
              className={`group flex items-center justify-between p-3 rounded-xl transition-all duration-200 ${isActive
                ? 'bg-blue-600/10 text-blue-400 border border-blue-500/20'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                }`}
            >
              <div className="flex items-center">
                <Icon className={`h-5 w-5 mr-3 transition-colors ${isActive ? 'text-blue-400' : 'group-hover:text-blue-400'}`} />
                <span className="text-sm font-semibold tracking-wide">{item.label}</span>
              </div>
              {isActive && <div className="w-1.5 h-1.5 rounded-full bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.8)]" />}
              {!isActive && <ChevronRight className="h-3 w-3 opacity-0 group-hover:opacity-100 transition-opacity" />}
            </Link>
          );
        })}
      </nav>

      {/* Footer / Meta */}
      <div className="p-4 border-t border-slate-800">
        <div className="bg-slate-900/50 rounded-2xl p-4 border border-slate-800">
          <div className="flex items-center space-x-3 mb-2">
            <div className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">System Healthy</span>
          </div>
          <p className="text-[10px] text-slate-500 leading-relaxed font-medium">
            Deploying AI Routes to Distribution Centers via OR-Tools.
          </p>
        </div>
      </div>
    </div>
  );
}
