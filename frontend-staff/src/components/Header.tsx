import { Search, MapPin, LogOut, TrendingUp, AlertTriangle, Users, Map, Bell } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { useEffect, useState } from 'react';
import { apiRequest } from '../utils/api';

export function Header() {
  const { user, logout } = useAuth();
  const [metrics, setMetrics] = useState<any>(null);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const res = await apiRequest('/api/dashboard/overview');
        if (res?.ok) {
          const data = await res.json();
          setMetrics(data);
        }
      } catch (err) {
        console.error('Failed to fetch header metrics', err);
      }
    };

    fetchMetrics();
    const interval = setInterval(fetchMetrics, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  const getLocationName = (locationId: string) => {
    const locationMap: { [key: string]: string } = {
      'loc_1': 'Leesville HQ',
      'loc_2': 'Lake Charles',
      'loc_3': 'Lufkin',
      'loc_4': 'Jasper'
    };
    return locationMap[locationId] || locationId;
  };

  return (
    <header className="fixed top-0 right-0 left-64 z-50 bg-[#0f172a] border-b border-slate-800 h-16 shadow-2xl">
      <div className="h-full px-6 flex items-center justify-between gap-4">
        {/* Live Answers Bar */}
        <div className="flex items-center space-x-8 text-sm font-medium overflow-x-auto no-scrollbar">
          <div className="flex flex-col">
            <span className="text-slate-400 text-[10px] uppercase tracking-wider">Revenue Today</span>
            <span className="text-emerald-400 font-bold flex items-center">
              ${metrics?.revenue_today?.toLocaleString() || '0'}
              <TrendingUp className="h-3 w-3 ml-1" />
            </span>
          </div>

          <div className="h-8 w-[1px] bg-slate-800" />

          <div className="flex flex-col">
            <span className="text-slate-400 text-[10px] uppercase tracking-wider">Active Drivers</span>
            <span className="text-blue-400 font-bold flex items-center">
              {metrics?.active_drivers || 0} / {metrics?.total_drivers || 0}
              <Users className="h-3 w-3 ml-1" />
            </span>
          </div>

          <div className="h-8 w-[1px] bg-slate-800" />

          <div className="flex flex-col">
            <span className="text-slate-400 text-[10px] uppercase tracking-wider">Alerts</span>
            <span className={`${metrics?.alerts_count > 0 ? 'text-amber-400' : 'text-slate-400'} font-bold flex items-center`}>
              {metrics?.alerts_count || 0}
              <Bell className="h-3 w-3 ml-1" />
            </span>
          </div>

          <div className="h-8 w-[1px] bg-slate-800" />

          <div className="flex flex-col">
            <span className="text-slate-400 text-[10px] uppercase tracking-wider">Missed Stops</span>
            <span className={`${metrics?.missed_stops > 0 ? 'text-red-400' : 'text-slate-400'} font-bold flex items-center`}>
              {metrics?.missed_stops || 0}
              <Map className="h-3 w-3 ml-1" />
            </span>
          </div>

          <div className="h-8 w-[1px] bg-slate-800" />

          <div className="flex flex-col">
            <span className="text-slate-400 text-[10px] uppercase tracking-wider">Red Flag</span>
            <span className={`${metrics?.red_flag ? 'text-red-500' : 'text-emerald-500'} font-black flex items-center`}>
              {metrics?.red_flag ? 'YES ⚠' : 'NO ✅'}
            </span>
          </div>
        </div>

        {/* Global Layer Actions */}
        <div className="flex items-center space-x-6">
          <div className="relative group hidden lg:block">
            <Search className="h-4 w-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500 group-focus-within:text-blue-400 transition-colors" />
            <input
              type="text"
              placeholder="Search customers, fleet, orders..."
              className="bg-slate-900 border border-slate-800 rounded-full pl-9 pr-4 py-1.5 text-xs w-64 focus:outline-none focus:ring-1 focus:ring-blue-500/50 focus:border-blue-500/50 transition-all placeholder:text-slate-600"
            />
          </div>

          <div className="flex items-center space-x-3 pl-4 border-l border-slate-800">
            <div className="flex flex-col items-end mr-1">
              <span className="text-[11px] font-bold text-slate-200 leading-none">{user?.full_name}</span>
              <span className="text-[10px] text-slate-500">{user?.role} • {user?.location_id ? getLocationName(user.location_id) : 'Unknown'}</span>
            </div>

            <button
              onClick={logout}
              className="p-2 transition-all rounded-lg text-slate-400 hover:text-red-400 hover:bg-red-400/10 group"
              title="Logout"
            >
              <LogOut className="h-5 w-5 group-hover:scale-110 transition-transform" />
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
