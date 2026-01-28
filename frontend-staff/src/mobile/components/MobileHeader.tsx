import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Bell, Menu, X, LogOut, Shield } from 'lucide-react';
import { Button } from '../../components/ui/button';
import { Badge } from '../../components/ui/badge';
import { Card, CardContent } from '../../components/ui/card';
import { useAuth } from '../../contexts/AuthContext';
import { usePR } from '../../contexts/PRContext';
import { useNotifications } from '../../hooks/useNotifications';

interface MobileHeaderProps {
  currentUser: {
    name: string;
    role: string;
    location: string;
  };
}

export function MobileHeader({ currentUser }: MobileHeaderProps) {
  const { user, logout } = useAuth();
  const { getNavigationPath } = usePR();
  const navigate = useNavigate();
  const [showMenu, setShowMenu] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const { notifications, unreadCount } = useNotifications();

  return (
    <>
      <header className="bg-[#020617] border-b border-slate-800 px-4 py-3 flex items-center justify-between relative z-50 shadow-lg">
        <div className="flex items-center space-x-3">
          <Button
            variant="ghost"
            size="sm"
            className="p-2 text-slate-400 hover:text-white hover:bg-slate-800"
            onClick={() => setShowMenu(!showMenu)}
          >
            <Menu className="h-6 w-6" />
          </Button>
          <div>
            <h1 className="text-sm font-black text-white uppercase tracking-tighter italic">Your Choice <span className="text-blue-500">Ice</span></h1>
            <div className="flex items-center space-x-1">
              <div className="w-1 h-1 rounded-full bg-emerald-500 animate-pulse" />
              <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest leading-none">Live Ops</p>
            </div>
          </div>
        </div>
        <div className="flex items-center space-x-1">
          <Button
            variant="ghost"
            size="sm"
            className="relative p-2 text-slate-400 hover:text-white"
            onClick={() => setShowNotifications(!showNotifications)}
          >
            <Bell className="h-5 w-5" />
            {unreadCount > 0 && (
              <Badge className="absolute top-1 right-1 h-4 w-4 rounded-full p-0 flex items-center justify-center text-[10px] bg-red-600 border-none text-white font-black">
                {unreadCount}
              </Badge>
            )}
          </Button>
          <div className="w-8 h-8 rounded-lg bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400 font-black text-[10px] uppercase">
            {currentUser.name.split(' ').map(n => n[0]).join('')}
          </div>
        </div>
      </header>

      {showMenu && (
        <div className="fixed inset-0 z-[100] bg-black/60 backdrop-blur-sm transition-all" onClick={() => setShowMenu(false)}>
          <div className="fixed left-0 top-0 h-full w-72 bg-[#020617] border-r border-slate-800 shadow-2xl flex flex-col" onClick={(e) => e.stopPropagation()}>
            <div className="p-6 border-b border-slate-800 bg-[#0f172a]/50">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xs font-black text-slate-500 uppercase tracking-widest">Fleet Navigation</h2>
                <Button variant="ghost" size="sm" onClick={() => setShowMenu(false)} className="text-slate-500 hover:text-white">
                  <X className="h-5 w-5" />
                </Button>
              </div>
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 rounded-2xl bg-blue-600 flex items-center justify-center text-white font-black text-xl shadow-lg ice-glow">
                  {currentUser.name[0]}
                </div>
                <div>
                  <h3 className="text-sm font-black text-white uppercase italic">{currentUser.name}</h3>
                  <Badge variant="outline" className="text-[10px] border-slate-700 text-blue-400 bg-blue-400/5">{currentUser.role.toUpperCase()}</Badge>
                </div>
              </div>
            </div>

            <div className="flex-1 p-4 space-y-1 overflow-y-auto">
              {[
                { label: 'Mission Overview', path: '/mobile/dashboard', roles: ['all'] },
                { label: 'Work Orders', path: '/mobile/work-orders', roles: ['technician', 'manager'] },
                { label: 'Fleet Routes', path: '/mobile/routes', roles: ['driver', 'dispatcher', 'manager'] },
                { label: 'Active Delivery', path: '/mobile/driver', roles: ['driver', 'manager'] },
                { label: 'Vehicle Inspection', path: '/mobile/inspection', roles: ['driver', 'technician', 'manager'] },
                { label: 'Operator Profile', path: '/mobile/profile', roles: ['all'] },
                { label: 'System Settings', path: '/mobile/settings', roles: ['all'] },
              ].map((item, i) => {
                const isVisible = item.roles.includes('all') || item.roles.includes(user?.role?.toLowerCase() || '');
                if (!isVisible) return null;
                return (
                  <Button
                    key={i}
                    variant="ghost"
                    className="w-full justify-start h-12 text-slate-400 hover:text-white hover:bg-slate-800/50 rounded-xl px-4 font-bold text-sm"
                    onClick={() => { navigate(getNavigationPath(item.path)); setShowMenu(false); }}
                  >
                    {item.label}
                  </Button>
                )
              })}
            </div>

            <div className="p-4 border-t border-slate-800">
              <Button variant="ghost" className="w-full justify-start h-12 text-red-400 hover:text-red-300 hover:bg-red-400/5 rounded-xl px-4 font-black text-xs uppercase tracking-widest" onClick={() => { logout(); setShowMenu(false); }}>
                <LogOut className="h-4 w-4 mr-3" />
                Terminate Session
              </Button>
            </div>
          </div>
        </div>
      )}

      {showNotifications && (
        <div className="fixed inset-0 z-[100] bg-black/60 backdrop-blur-sm" onClick={() => setShowNotifications(false)}>
          <div className="fixed right-0 top-0 h-full w-80 bg-[#020617] border-l border-slate-800 shadow-2xl flex flex-col" onClick={(e) => e.stopPropagation()}>
            <div className="p-6 border-b border-slate-800">
              <div className="flex items-center justify-between">
                <h2 className="text-xs font-black text-slate-500 uppercase tracking-widest">Active Alerts</h2>
                <Button variant="ghost" size="sm" onClick={() => setShowNotifications(false)} className="text-slate-500">
                  <X className="h-5 w-5" />
                </Button>
              </div>
            </div>
            <div className="flex-1 p-4 space-y-4 overflow-y-auto">
              {notifications.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full space-y-4 opacity-20">
                  <Shield className="h-12 w-12 text-slate-500" />
                  <p className="text-xs font-black text-slate-500 uppercase tracking-widest">No Alerts Detected</p>
                </div>
              ) : (
                notifications.map((notification) => (
                  <Card key={notification.id} className="bg-[#0f172a] border-slate-800 group hover:border-blue-500/30 transition-all">
                    <CardContent className="p-4 space-y-2">
                      <div className="flex justify-between items-start">
                        <h3 className="font-black text-white text-xs uppercase italic">{notification.title}</h3>
                        <span className="text-[10px] text-slate-500 font-medium">2m</span>
                      </div>
                      <p className="text-xs text-slate-400 leading-relaxed font-medium">{notification.message}</p>
                    </CardContent>
                  </Card>
                ))
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
