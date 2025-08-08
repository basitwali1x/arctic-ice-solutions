import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from 'next-themes';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { PRProvider } from './contexts/PRContext';
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
import { Maintenance } from './pages/Maintenance';
import { ProductionManager } from './pages/ProductionManager';
import MobileApp from './mobile/MobileApp';
import EmployeeApp from './employee/EmployeeApp';
import { useIsMobile } from './hooks/use-mobile';
import React, { Suspense } from 'react';

const RoleBasedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user } = useAuth();
  const isMobile = useIsMobile();
  
  if (user?.role === 'customer') {
    return <Navigate to="/mobile/customer" replace />;
  }
  
  if (user?.role === 'employee') {
    return <Navigate to="/employee" replace />;
  }
  
  if (isMobile) {
    return <Navigate to="/mobile" replace />;
  }
  
  return <>{children}</>;
};

function App() {

  return (
    <ErrorBoundary>
      <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
        <AuthProvider>
          <Router>
            <PRProvider>
            <Routes>
              <Route path="/login" element={<LoginPage />} />
              
              <Route path="/pr/:prNumber/login" element={<LoginPage />} />
              <Route
                path="/pr/:prNumber/mobile/*"
                element={
                  <ProtectedRoute>
                    <ErrorBoundary>
                      <MobileApp />
                    </ErrorBoundary>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/pr/:prNumber/*"
                element={
                  <ProtectedRoute>
                    <RoleBasedRoute>
                      <div className="flex h-screen bg-gray-100">
                        <Sidebar />
                        <div className="flex-1 flex flex-col overflow-hidden">
                          <Header />
                          <main className="flex-1 overflow-x-hidden overflow-y-auto bg-gray-100 p-6">
                            <ErrorBoundary>
                              <Routes>
                                <Route path="/" element={<Navigate to="dashboard" replace />} />
                                <Route path="/dashboard" element={
                                  <Suspense fallback={<div className="flex items-center justify-center h-64">Loading dashboard...</div>}>
                                    <Dashboard />
                                  </Suspense>
                                } />
                                <Route path="/production-inventory" element={<ProductionInventory />} />
                                <Route path="/fleet" element={<FleetManagement />} />
                                <Route path="/customers" element={<CustomerManagement />} />
                                <Route path="/financial" element={<Financial />} />
                                <Route path="/maintenance" element={<Maintenance />} />
                                <Route path="/production" element={<ProductionManager />} />
                                <Route path="/settings" element={<Settings />} />
                              </Routes>
                            </ErrorBoundary>
                          </main>
                        </div>
                      </div>
                    </RoleBasedRoute>
                  </ProtectedRoute>
                }
              />
              
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
                path="/employee/*"
                element={
                  <ProtectedRoute>
                    <ErrorBoundary>
                      <EmployeeApp />
                    </ErrorBoundary>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/*"
                element={
                  <ProtectedRoute>
                    <RoleBasedRoute>
                      <div className="flex h-screen bg-gray-100">
                        <Sidebar />
                        <div className="flex-1 flex flex-col overflow-hidden">
                          <Header />
                          <main className="flex-1 overflow-x-hidden overflow-y-auto bg-gray-100 p-6">
                            <ErrorBoundary>
                              <Routes>
                                <Route path="/" element={<Navigate to="/dashboard" replace />} />
                                <Route path="/dashboard" element={
                                  <Suspense fallback={<div className="flex items-center justify-center h-64">Loading dashboard...</div>}>
                                    <Dashboard />
                                  </Suspense>
                                } />
                                <Route path="/production-inventory" element={<ProductionInventory />} />
                                <Route path="/fleet" element={<FleetManagement />} />
                                <Route path="/customers" element={<CustomerManagement />} />
                                <Route path="/financial" element={<Financial />} />
                                <Route path="/maintenance" element={<Maintenance />} />
                                <Route path="/production" element={<ProductionManager />} />
                                <Route path="/settings" element={<Settings />} />
                              </Routes>
                            </ErrorBoundary>
                          </main>
                        </div>
                      </div>
                    </RoleBasedRoute>
                  </ProtectedRoute>
                }
              />
            </Routes>
            <Toaster />
          </PRProvider>
        </Router>
      </AuthProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App;
