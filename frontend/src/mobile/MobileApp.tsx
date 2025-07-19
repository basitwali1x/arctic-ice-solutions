import { useState } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { MobileDashboard } from './pages/MobileDashboard';
import { MobileWorkOrders } from './pages/MobileWorkOrders';
import { MobileProfile } from './pages/MobileProfile';
import { MobileRoutes } from './pages/MobileRoutes';
import { MobileDriver } from './pages/MobileDriver';
import { MobileInspection } from './pages/MobileInspection';
import { MobileSettings } from './pages/MobileSettings';
import { MobileNavigation } from './components/MobileNavigation';
import { MobileHeader } from './components/MobileHeader';

function MobileApp() {
  const [currentUser] = useState({
    name: 'Field Technician',
    role: 'technician',
    location: 'Mobile Unit'
  });

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      <MobileHeader currentUser={currentUser} />
      <main className="flex-1 overflow-y-auto pb-16">
        <Routes>
          <Route path="/" element={<Navigate to="/mobile/dashboard" replace />} />
          <Route path="/dashboard" element={<MobileDashboard />} />
          <Route path="/work-orders" element={<MobileWorkOrders />} />
          <Route path="/routes" element={<MobileRoutes />} />
          <Route path="/driver" element={<MobileDriver />} />
          <Route path="/inspection" element={<MobileInspection />} />
          <Route path="/settings" element={<MobileSettings />} />
          <Route path="/profile" element={<MobileProfile />} />
        </Routes>
      </main>
      <MobileNavigation />
    </div>
  );
}

export default MobileApp;
