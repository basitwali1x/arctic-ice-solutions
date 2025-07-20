import { useState, useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { MobileDashboard } from './pages/MobileDashboard';
import { MobileWorkOrders } from './pages/MobileWorkOrders';
import { MobileProfile } from './pages/MobileProfile';
import { MobileRoutes } from './pages/MobileRoutes';
import { MobileDriver } from './pages/MobileDriver';
import { MobileInspection } from './pages/MobileInspection';
import { MobileSettings } from './pages/MobileSettings';
import { MobileNavigation } from './components/MobileNavigation';
import { MobileHeader } from './components/MobileHeader';
import { MobileLocationAuth } from './components/MobileLocationAuth';

function MobileApp() {
  const { user } = useAuth();
  const [locationVerified, setLocationVerified] = useState(false);
  const [, setCurrentLocation] = useState<{ lat: number; lng: number } | null>(null);

  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setCurrentLocation({
            lat: position.coords.latitude,
            lng: position.coords.longitude
          });
          setLocationVerified(true);
        },
        (error) => {
          console.error('GPS Error:', error);
          setLocationVerified(true);
        }
      );
    } else {
      setLocationVerified(true);
    }
  }, []);

  if (!user) {
    return <div>Loading...</div>;
  }

  if (!locationVerified) {
    return <MobileLocationAuth onLocationVerified={() => setLocationVerified(true)} />;
  }

  const currentUser = {
    name: user.full_name,
    role: user.role,
    location: user.location_id
  };

  const getRoleBasedRoutes = () => {
    const userRole = user?.role?.toLowerCase();
    
    return (
      <Routes>
        <Route path="/" element={<Navigate to="/mobile/dashboard" replace />} />
        <Route path="/dashboard" element={<MobileDashboard />} />
        
        {(userRole === 'technician' || userRole === 'manager') && (
          <Route path="/work-orders" element={<MobileWorkOrders />} />
        )}
        
        {(userRole === 'driver' || userRole === 'dispatcher' || userRole === 'manager') && (
          <Route path="/routes" element={<MobileRoutes />} />
        )}
        
        {(userRole === 'driver' || userRole === 'manager') && (
          <Route path="/driver" element={<MobileDriver />} />
        )}
        
        {(userRole === 'driver' || userRole === 'technician' || userRole === 'manager') && (
          <Route path="/inspection" element={<MobileInspection />} />
        )}
        
        <Route path="/settings" element={<MobileSettings />} />
        <Route path="/profile" element={<MobileProfile />} />
      </Routes>
    );
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      <MobileHeader currentUser={currentUser} />
      <main className="flex-1 overflow-y-auto pb-16">
        {getRoleBasedRoutes()}
      </main>
      <MobileNavigation />
    </div>
  );
}

export default MobileApp;
