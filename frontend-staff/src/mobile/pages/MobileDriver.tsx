import { useState, useEffect } from 'react';
import { Card, CardContent } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge } from '../../components/ui/badge';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import {
  MapPin,
  Navigation,
  Package,
  Camera as CameraIcon,
  PenTool,
  ChevronRight,
  CheckCircle2,
  Phone
} from 'lucide-react';
import { Camera, CameraResultType, CameraSource } from '@capacitor/camera';
import { SignaturePad } from '../../components/SignaturePad';
import { apiRequest } from '../../utils/api';
import { useNavigate } from 'react-router-dom';

export function MobileDriver() {
  const navigate = useNavigate();
  const [activeRoute, setActiveRoute] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [showVerification, setShowVerification] = useState(false);
  const [showSignaturePad, setShowSignaturePad] = useState(false);
  const [deliveryStatus, setDeliveryStatus] = useState<'pending' | 'success' | 'refused' | 'shorted'>('pending');

  const [deliveryForm, setDeliveryForm] = useState({
    bags_delivered: 0,
    payment_method: 'account',
    payment_amount: 0,
    notes: '',
    photo: null as Blob | null,
    photoPreview: '',
    signature: ''
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await apiRequest('/api/routes');
        if (res && res.ok) {
          const routes = await res.json();
          const route = routes.find((r: any) => r.status === 'active' || r.status === 'planned');
          setActiveRoute(route);

          const nextStop = route?.stops?.find((s: any) => s.status === 'pending');
          if (nextStop) {
            setDeliveryForm(prev => ({
              ...prev,
              bags_delivered: nextStop.bags || 0,
              payment_amount: (nextStop.bags || 0) * 2.25 // Default pricing mock
            }));
          }
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const nextStop = activeRoute?.stops?.find((s: any) => s.status === 'pending');

  const handleTakePhoto = async () => {
    try {
      const image = await Camera.getPhoto({
        quality: 90,
        allowEditing: false,
        resultType: CameraResultType.Uri,
        source: CameraSource.Camera
      });

      if (image.webPath) {
        const response = await fetch(image.webPath);
        const blob = await response.blob();
        setDeliveryForm(prev => ({
          ...prev,
          photo: blob,
          photoPreview: image.webPath || ''
        }));
      }
    } catch (error) {
      console.error('Camera error:', error);
    }
  };

  const handleComplete = async () => {
    if (!nextStop) return;
    setLoading(true);
    try {
      const res = await apiRequest(`/api/orders/${nextStop.order_id || nextStop.id}/complete`, {
        method: 'POST',
        body: JSON.stringify({
          status: deliveryStatus === 'success' ? 'delivered' : deliveryStatus,
          bags_delivered: deliveryForm.bags_delivered,
          payment_method: deliveryForm.payment_method,
          payment_amount: deliveryForm.payment_amount,
          notes: deliveryForm.notes,
        })
      });

      if (res && res.ok) {
        navigate('/mobile/dashboard');
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading && !activeRoute) return <div className="p-4 text-center text-white bg-[#020617] h-screen pt-20 font-black uppercase text-xs animate-pulse">Locating Cargo...</div>;

  if (!nextStop) {
    return (
      <div className="p-8 text-center bg-[#020617] h-screen flex flex-col items-center justify-center space-y-6">
        <CheckCircle2 className="h-20 w-20 text-emerald-500 animate-bounce" />
        <h1 className="text-2xl font-black text-white uppercase italic">Route Complete</h1>
        <p className="text-slate-400">All stops delivered. Return to base or wait for new orders.</p>
        <Button onClick={() => navigate('/mobile/dashboard')} className="w-full bg-blue-600 h-14 rounded-2xl font-black italic uppercase">BACK TO COMMAND CENTER</Button>
      </div>
    );
  }

  return (
    <div className="bg-[#020617] min-h-screen flex flex-col">
      <div className="h-48 bg-blue-600 relative overflow-hidden flex items-end p-6">
        <div className="absolute top-0 right-0 p-4 opacity-10">
          <Package className="h-40 w-40 text-black" />
        </div>
        <div className="relative z-10 space-y-2 text-white">
          <Badge className="bg-black/20 text-white border-white/20 mb-2 uppercase text-[10px] font-black tracking-widest">Target Destination</Badge>
          <h1 className="text-3xl font-black leading-none uppercase italic">{nextStop.customer_name}</h1>
          <div className="flex items-center text-white/80 text-sm font-bold">
            <MapPin className="h-4 w-4 mr-2" />
            {nextStop.address}
          </div>
        </div>
      </div>

      <div className="flex-1 p-6 space-y-6">
        {!showVerification ? (
          <div className="space-y-6 animate-in slide-in-from-bottom-5 duration-500">
            <div className="flex gap-3">
              <Button variant="outline" className="flex-1 h-14 bg-[#0f172a] border-slate-800 text-blue-400 rounded-2xl font-bold">
                <Phone className="h-4 w-4 mr-2" /> Call Customer
              </Button>
              <Button variant="outline" className="flex-1 h-14 bg-[#0f172a] border-slate-800 text-blue-400 rounded-2xl font-bold">
                <Navigation className="h-4 w-4 mr-2" /> Open Maps
              </Button>
            </div>

            <Card className="bg-[#0f172a] border-slate-800 rounded-3xl overflow-hidden shadow-2xl">
              <CardContent className="p-6 space-y-4">
                <div className="flex justify-between items-center pb-4 border-b border-slate-800">
                  <span className="text-xs font-black text-slate-500 uppercase tracking-widest">Expected Payload</span>
                  <div className="text-right">
                    <p className="text-2xl font-black text-white italic">{nextStop.bags} BAGS</p>
                    <p className="text-[10px] font-bold text-slate-500 uppercase">8lb Bags • Standard</p>
                  </div>
                </div>
                <div className="space-y-2">
                  <Label className="text-[10px] uppercase font-black text-slate-500">Delivery Instructions</Label>
                  <p className="text-sm font-bold text-slate-300 italic">"Leave by the back freezer. Codes: 1234. Watch for the cat."</p>
                </div>
              </CardContent>
            </Card>

            <div className="grid grid-cols-1 gap-4">
              <Button
                onClick={() => { setDeliveryStatus('success'); setShowVerification(true); }}
                className="h-24 bg-emerald-600 hover:bg-emerald-500 text-white rounded-3xl flex flex-col items-center justify-center space-y-1 shadow-lg ice-glow"
              >
                <p className="text-xl font-black italic uppercase tracking-tighter">CONFIRM FULL DELIVERY</p>
                <p className="text-[10px] font-bold opacity-80 uppercase tracking-widest text-white">Mark as Delivered</p>
              </Button>

              <div className="grid grid-cols-2 gap-4">
                <Button
                  onClick={() => { setDeliveryStatus('shorted'); setShowVerification(true); }}
                  className="h-20 bg-[#0f172a] border-2 border-amber-500 text-amber-500 rounded-2xl flex flex-col items-center justify-center"
                >
                  <p className="font-black italic uppercase text-amber-500">SHORTED</p>
                  <p className="text-[10px] font-bold opacity-80 uppercase text-amber-500">Partial Load</p>
                </Button>
                <Button
                  onClick={() => { setDeliveryStatus('refused'); setShowVerification(true); }}
                  className="h-20 bg-[#0f172a] border-2 border-red-500 text-red-500 rounded-2xl flex flex-col items-center justify-center"
                >
                  <p className="font-black italic uppercase text-red-500">REFUSED</p>
                  <p className="text-[10px] font-bold opacity-80 uppercase text-red-500">No Delivery</p>
                </Button>
              </div>
            </div>
          </div>
        ) : (
          <div className="space-y-6 animate-in slide-in-from-right-5 duration-500">
            <div className="flex items-center justify-between">
              <Button variant="ghost" onClick={() => setShowVerification(false)} className="text-slate-400 hover:text-white">
                <ChevronRight className="h-5 w-5 rotate-180 mr-2" /> Back
              </Button>
              <Badge className={`${deliveryStatus === 'success' ? 'bg-emerald-500' : deliveryStatus === 'shorted' ? 'bg-amber-500' : 'bg-red-500'} uppercase text-[10px] font-black tracking-widest border-none text-white`}>
                Status: {deliveryStatus}
              </Badge>
            </div>

            <Card className="bg-[#0f172a] border-slate-800 rounded-3xl">
              <CardContent className="p-6 space-y-6">
                <div className="space-y-4">
                  <Label className="text-[10px] font-black text-slate-500 uppercase">Input Payload</Label>
                  <div className="flex items-center space-x-4">
                    <Button
                      onClick={() => setDeliveryForm(prev => ({ ...prev, bags_delivered: Math.max(0, prev.bags_delivered - 1) }))}
                      className="h-14 w-14 rounded-2xl bg-slate-800 text-2xl font-black text-white hover:bg-slate-700"
                    >-</Button>
                    <Input
                      type="number"
                      value={deliveryForm.bags_delivered}
                      onChange={(e) => setDeliveryForm({ ...deliveryForm, bags_delivered: parseInt(e.target.value) })}
                      className="h-14 text-center text-2xl font-black bg-transparent border-slate-800 text-white"
                    />
                    <Button
                      onClick={() => setDeliveryForm(prev => ({ ...prev, bags_delivered: prev.bags_delivered + 1 }))}
                      className="h-14 w-14 rounded-2xl bg-blue-600 text-2xl font-black text-white hover:bg-blue-500"
                    >+</Button>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <Button
                    onClick={handleTakePhoto}
                    className={`h-28 flex flex-col items-center justify-center space-y-2 rounded-2xl border-2 border-dashed ${deliveryForm.photoPreview ? 'border-blue-500 bg-blue-500/10' : 'border-slate-800 bg-slate-900'} transition-all`}
                  >
                    {deliveryForm.photoPreview ? (
                      <img src={deliveryForm.photoPreview} className="h-full w-full object-cover rounded-2xl" alt="Proof" />
                    ) : (
                      <>
                        <CameraIcon className="h-8 w-8 text-blue-500" />
                        <span className="text-[10px] font-black text-slate-500 uppercase">Proof Photo</span>
                      </>
                    )}
                  </Button>
                  <Button
                    onClick={() => setShowSignaturePad(true)}
                    className={`h-28 flex flex-col items-center justify-center space-y-2 rounded-2xl border-2 border-dashed ${deliveryForm.signature ? 'border-blue-500 bg-blue-500/10' : 'border-slate-800 bg-slate-900'} transition-all`}
                  >
                    {deliveryForm.signature ? (
                      <img src={deliveryForm.signature} className="h-full object-contain p-2" alt="Signature" />
                    ) : (
                      <>
                        <PenTool className="h-8 w-8 text-blue-500" />
                        <span className="text-[10px] font-black text-slate-500 uppercase">Signature</span>
                      </>
                    )}
                  </Button>
                </div>

                <div className="space-y-2">
                  <Label className="text-[10px] font-black text-slate-500 uppercase">Field Notes</Label>
                  <Input
                    placeholder="Condition of freezer, stock levels, etc..."
                    value={deliveryForm.notes}
                    onChange={(e) => setDeliveryForm({ ...deliveryForm, notes: e.target.value })}
                    className="bg-slate-900 border-slate-800 text-white italic"
                  />
                </div>
              </CardContent>
            </Card>

            <Button
              onClick={handleComplete}
              className="w-full h-16 bg-blue-600 hover:bg-blue-500 text-white rounded-3xl text-lg font-black italic uppercase tracking-widest shadow-2xl ice-glow"
            >
              TRANSMIT DELIVERY DATA
            </Button>
            <p className="text-center text-[10px] text-slate-500 font-bold uppercase tracking-widest">Digital Satellite Uplink Active</p>
          </div>
        )}
      </div>

      {showSignaturePad && (
        <div className="fixed inset-0 z-[100] bg-black/80 flex items-center justify-center p-4">
          <SignaturePad
            onSave={(sig) => {
              setDeliveryForm({ ...deliveryForm, signature: sig });
              setShowSignaturePad(false);
            }}
            onCancel={() => setShowSignaturePad(false)}
          />
        </div>
      )}
    </div>
  );
}
