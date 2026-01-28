import { useState, useEffect } from 'react';
import { Card, CardContent } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge } from '../../components/ui/badge';
import { Truck, MapPin, Navigation, Clock, Play, CheckCircle, Smartphone } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { apiRequest } from '../../utils/api';
import { useNavigate } from 'react-router-dom';

export function MobileDashboard() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [activeRoute, setActiveRoute] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await apiRequest('/api/routes');
        if (res && res.ok) {
          const routes = await res.json();
          // Find first active or planned route
          const route = routes.find((r: any) => r.status === 'active' || r.status === 'planned');
          setActiveRoute(route);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) return <div className="p-4 text-center text-slate-500 uppercase font-black text-xs animate-pulse">Configuring Mission...</div>;

  const nextStop = activeRoute?.stops?.find((s: any) => s.status === 'pending');

  return (
    <div className="p-6 space-y-8 bg-[#020617] min-h-full">
      <header className="space-y-1">
        <h1 className="text-2xl font-black text-white italic tracking-tighter uppercase">Command <span className="text-blue-500">Center</span></h1>
        <p className="text-xs text-slate-500 font-bold uppercase tracking-widest">Driver: {user?.full_name}</p>
      </header>

      {/* Main Action Hub */}
      {!nextStop ? (
        <Card className="bg-[#0f172a] border-slate-800 shadow-2xl overflow-hidden relative border-t-4 border-t-amber-500">
          <CardContent className="p-8 text-center space-y-6">
            <div className="w-16 h-16 bg-amber-500/10 rounded-full flex items-center justify-center mx-auto">
              <Truck className="h-8 w-8 text-amber-500" />
            </div>
            <div className="space-y-2">
              <h2 className="text-xl font-bold text-white uppercase italic">No Active Shift</h2>
              <p className="text-sm text-slate-400">Please contact dispatch to assign your route for today.</p>
            </div>
            <Button onClick={() => navigate('/mobile/routes')} className="w-full bg-blue-600 hover:bg-blue-500 h-14 text-lg font-black uppercase tracking-widest italic rounded-2xl ice-glow">
              VIEW AVAILABLE ROUTES
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-6">
          {/* Next Stop Hero */}
          <Card className="bg-gradient-to-br from-blue-600 to-indigo-700 border-none shadow-2xl rounded-3xl overflow-hidden relative">
            <div className="absolute top-0 right-0 p-4 opacity-20">
              <Navigation className="h-24 w-24 text-white" />
            </div>
            <CardContent className="p-8 space-y-6 relative z-10 text-white">
              <div className="flex justify-between items-start">
                <Badge className="bg-white/20 text-white hover:bg-white/20 border-white/30 backdrop-blur-md uppercase text-[10px] font-black tracking-widest">
                  Next Priority Stop
                </Badge>
                <div className="text-right">
                  <p className="text-[10px] font-black uppercase tracking-widest opacity-70">Distance</p>
                  <p className="text-sm font-bold">12.4 mi</p>
                </div>
              </div>

              <div className="space-y-2">
                <h2 className="text-3xl font-black italic uppercase leading-none">{nextStop?.customer_name || 'Destination Alpha'}</h2>
                <div className="flex items-center text-white/80 text-sm font-bold">
                  <MapPin className="h-4 w-4 mr-2" />
                  {nextStop?.address || '123 Route 66, Lake Charles, LA'}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="p-3 bg-white/10 rounded-2xl border border-white/5 backdrop-blur-sm">
                  <span className="text-[10px] uppercase font-black opacity-60 block">Cargo</span>
                  <span className="text-sm font-black">128 BAGS (8LB)</span>
                </div>
                <div className="p-3 bg-white/10 rounded-2xl border border-white/5 backdrop-blur-sm">
                  <span className="text-[10px] uppercase font-black opacity-60 block">ETA</span>
                  <span className="text-sm font-black">2:15 PM</span>
                </div>
              </div>

              <Button
                onClick={() => navigate('/mobile/driver')}
                className="w-full bg-white text-blue-700 hover:bg-blue-50 h-16 text-lg font-black uppercase tracking-widest italic rounded-2xl shadow-xl flex items-center justify-center space-x-3"
              >
                <Play className="h-6 w-6 fill-current" />
                <span>RESUME MISSION</span>
              </Button>
            </CardContent>
          </Card>

          {/* Secondary Stats */}
          <div className="grid grid-cols-2 gap-4">
            <Card className="bg-[#0f172a] border-slate-800 rounded-2xl">
              <CardContent className="p-4 flex items-center space-x-4">
                <div className="p-3 bg-emerald-500/10 rounded-xl">
                  <CheckCircle className="h-5 w-5 text-emerald-500" />
                </div>
                <div>
                  <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Completed</p>
                  <p className="text-lg font-black text-white">{activeRoute.stops?.filter((s: any) => s.status === 'completed').length || 0} / {activeRoute.stops?.length || 0}</p>
                </div>
              </CardContent>
            </Card>
            <Card className="bg-[#0f172a] border-slate-800 rounded-2xl">
              <CardContent className="p-4 flex items-center space-x-4">
                <div className="p-3 bg-blue-500/10 rounded-xl">
                  <Clock className="h-5 w-5 text-blue-500" />
                </div>
                <div>
                  <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Time Remaining</p>
                  <p className="text-lg font-black text-white">4h 12m</p>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      )}

      {/* Quick Ops */}
      <div className="space-y-4 pt-4">
        <h3 className="text-[10px] font-black text-slate-500 uppercase tracking-widest pl-1">Operational Quick-Actions</h3>
        <div className="grid grid-cols-1 gap-3">
          <Button variant="outline" className="h-14 border-slate-800 bg-[#0f172a] text-slate-200 justify-start px-6 rounded-2xl hover:bg-slate-800 group">
            <Smartphone className="h-5 w-5 mr-4 text-blue-500 group-hover:scale-110 transition-transform" />
            <span className="font-bold">Contact Operations Dispatch</span>
          </Button>
          <Button variant="outline" className="h-14 border-slate-800 bg-[#0f172a] text-slate-200 justify-start px-6 rounded-2xl hover:bg-slate-800 group">
            <Clock className="h-5 w-5 mr-4 text-emerald-500 group-hover:scale-110 transition-transform" />
            <span className="font-bold">Request Shift Overtime</span>
          </Button>
        </div>
      </div>
    </div>
  );
}
