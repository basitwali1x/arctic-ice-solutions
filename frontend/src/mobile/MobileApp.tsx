import { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { MobileDashboard } from './pages/MobileDashboard';
import { MobileWorkOrders } from './pages/MobileWorkOrders';
import { MobileProfile } from './pages/MobileProfile';
import { MobileNavigation } from './components/MobileNavigation';
import { MobileHeader } from './components/MobileHeader';

function MobileApp() {
  const [currentUser] = useState({
    name: 'Field Technician',
    role: 'technician',
    location: 'Mobile Unit'
  });

  return (
    <Router>
      <div className="flex flex-col h-screen bg-gray-50">
        <MobileHeader currentUser={currentUser} />
        <main className="flex-1 overflow-y-auto pb-16">
          <Routes>
            <Route path="/mobile" element={<Navigate to="/mobile/dashboard" replace />} />
            <Route path="/mobile/dashboard" element={<MobileDashboard />} />
            <Route path="/mobile/work-orders" element={<MobileWorkOrders />} />
            <Route path="/mobile/profile" element={<MobileProfile />} />
          </Routes>
        </main>
        <MobileNavigation />
      </div>
    </Router>
  );
}

export default MobileApp;
