import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { CustomerDashboard } from './pages/CustomerDashboard';
import { CustomerOrders } from './pages/CustomerOrders';
import { CustomerTracking } from './pages/CustomerTracking';
import { CustomerBilling } from './pages/CustomerBilling';
import { CustomerFeedback } from './pages/CustomerFeedback';
import { CustomerNavigation } from './components/CustomerNavigation';
import { CustomerHeader } from './components/CustomerHeader';

function CustomerApp() {
  const { user } = useAuth();

  if (!user) {
    return <div>Loading...</div>;
  }

  const currentUser = {
    name: user.full_name,
    role: user.role,
    location: user.location_id
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50 dark:bg-gray-900">
      <CustomerHeader currentUser={currentUser} />
      <main className="flex-1 overflow-y-auto pb-16">
        <Routes>
          <Route path="/" element={<Navigate to="/customer/dashboard" replace />} />
          <Route path="/dashboard" element={<CustomerDashboard />} />
          <Route path="/orders" element={<CustomerOrders />} />
          <Route path="/tracking" element={<CustomerTracking />} />
          <Route path="/billing" element={<CustomerBilling />} />
          <Route path="/feedback" element={<CustomerFeedback />} />
        </Routes>
      </main>
      <CustomerNavigation />
    </div>
  );
}

export default CustomerApp;
