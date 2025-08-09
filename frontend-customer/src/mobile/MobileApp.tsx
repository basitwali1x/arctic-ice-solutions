import { useState, useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { MobileDashboard } from './pages/MobileDashboard';
import { MobileProfile } from './pages/MobileProfile';
import { MobileCustomer } from './pages/MobileCustomer';
import { MobileSettings } from './pages/MobileSettings';
import { MobileNavigation } from './components/MobileNavigation';
import { MobileHeader } from './components/MobileHeader';
import { MobileLocationAuth } from './components/MobileLocationAuth';
import { initializeCapacitor, getCurrentPosition, initializePushNotifications } from '../utils/capacitor';

function MobileApp() {
  const { user } = useAuth();
  const [locationVerified, setLocationVerified] = useState(false);
  const [, setCurrentLocation] = useState<{ lat: number; lng: number } | null>(null);

  useEffect(() => {
    const initializeApp = async () => {
      try {
        await initializeCapacitor();
        await initializePushNotifications();
        
        const position = await getCurrentPosition();
        setCurrentLocation({
          lat: position.coords.latitude,
          lng: position.coords.longitude
        });
        setLocationVerified(true);
      } catch (error) {
        console.error('Initialization Error:', error);
        setLocationVerified(true);
      }
    };

    initializeApp();
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
    
    if (userRole !== 'customer') {
      return (
        <Routes>
          <Route path="*" element={<div className="p-4 text-center">Access denied. This app is for customers only.</div>} />
        </Routes>
      );
    }
    
    return (
      <Routes>
        <Route path="/" element={<Navigate to="/mobile/dashboard" replace />} />
        <Route path="/dashboard" element={<MobileDashboard />} />
        <Route path="/customer" element={<MobileCustomer />} />
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
