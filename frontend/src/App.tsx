import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { LoginPage } from './components/LoginPage';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { ErrorBoundary } from './components/ErrorBoundary';
import { Toaster } from './components/ui/toaster';
import { Dashboard } from './pages/Dashboard';
import { ProductionInventory } from './pages/ProductionInventory';
import { FleetManagement } from './pages/FleetManagement';
import { CustomerManagement } from './pages/CustomerManagement';
import { Financial } from './pages/Financial';
import { Settings } from './pages/Settings';
import AdminPricingDashboard from './pages/AdminPricingDashboard';
import EmployeeManagement from './pages/EmployeeManagement';
import { Maintenance } from './pages/Maintenance';
import { ProductionManager } from './pages/ProductionManager';
import MobileApp from './mobile/MobileApp';
import { useIsMobile } from './hooks/use-mobile';

function App() {
  const isMobile = useIsMobile();

  return (
    <ErrorBoundary>
      <AuthProvider>
        <Router>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route
              path="/mobile/*"
              element={
                <ProtectedRoute>
                  <ErrorBoundary>
                    <MobileApp />
                  </ErrorBoundary>
                </ProtectedRoute>
              }
            />
            <Route
              path="/*"
              element={
                <ProtectedRoute>
                  {isMobile ? (
                    <Navigate to="/mobile" replace />
                  ) : (
                    <div className="flex h-screen bg-gray-100">
                      <Sidebar />
                      <div className="flex-1 flex flex-col overflow-hidden">
                        <Header />
                        <main className="flex-1 overflow-x-hidden overflow-y-auto bg-gray-100 p-6">
                          <ErrorBoundary>
                            <Routes>
                              <Route path="/" element={<Navigate to="/dashboard" replace />} />
                              <Route path="/dashboard" element={<Dashboard />} />
                              <Route path="/production-inventory" element={<ProductionInventory />} />
                              <Route path="/fleet" element={<FleetManagement />} />
                              <Route path="/customers" element={<CustomerManagement />} />
                              <Route path="/financial" element={<Financial />} />
                              <Route path="/maintenance" element={<Maintenance />} />
                              <Route path="/production" element={<ProductionManager />} />
                              <Route path="/pricing" element={<AdminPricingDashboard />} />
                              <Route path="/employees" element={<EmployeeManagement />} />
                              <Route path="/settings" element={<Settings />} />
                            </Routes>
                          </ErrorBoundary>
                        </main>
                      </div>
                    </div>
                  )}
                </ProtectedRoute>
              }
            />
          </Routes>
          <Toaster />
        </Router>
      </AuthProvider>
    </ErrorBoundary>
  );
}

export default App;
