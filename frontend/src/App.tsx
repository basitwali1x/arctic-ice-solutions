import { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { Dashboard } from './pages/Dashboard';
import { ProductionInventory } from './pages/ProductionInventory';
import { FleetManagement } from './pages/FleetManagement';
import { CustomerManagement } from './pages/CustomerManagement';
import { Financial } from './pages/Financial';
import { Settings } from './pages/Settings';
import { Maintenance } from './pages/Maintenance';
import { ProductionManager } from './pages/ProductionManager';

function App() {
  const [currentUser] = useState({
    name: 'John Manager',
    role: 'manager',
    location: 'Leesville HQ'
  });

  return (
    <Router>
      <div className="flex h-screen bg-gray-100">
        <Sidebar currentUser={currentUser} />
        <div className="flex-1 flex flex-col overflow-hidden">
          <Header currentUser={currentUser} />
          <main className="flex-1 overflow-x-hidden overflow-y-auto bg-gray-100 p-6">
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/production" element={<ProductionInventory />} />
              <Route path="/fleet" element={<FleetManagement />} />
              <Route path="/customers" element={<CustomerManagement />} />
              <Route path="/maintenance" element={<Maintenance />} />
              <Route path="/production-manager" element={<ProductionManager />} />
              <Route path="/financial" element={<Financial />} />
              <Route path="/settings" element={<Settings />} />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  );
}

export default App;
