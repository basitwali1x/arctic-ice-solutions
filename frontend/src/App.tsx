import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { LoginPage } from './components/LoginPage';
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
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={
            <ProtectedRoute>
              <div className="flex h-screen bg-gray-100">
                <Sidebar />
                <div className="flex-1 flex flex-col overflow-hidden">
                  <Header />
                  <main className="flex-1 overflow-x-hidden overflow-y-auto bg-gray-100 p-6">
                    <Dashboard />
                  </main>
                </div>
              </div>
            </ProtectedRoute>
          } />
          <Route path="/production" element={
            <ProtectedRoute>
              <div className="flex h-screen bg-gray-100">
                <Sidebar />
                <div className="flex-1 flex flex-col overflow-hidden">
                  <Header />
                  <main className="flex-1 overflow-x-hidden overflow-y-auto bg-gray-100 p-6">
                    <ProductionInventory />
                  </main>
                </div>
              </div>
            </ProtectedRoute>
          } />
          <Route path="/fleet" element={
            <ProtectedRoute>
              <div className="flex h-screen bg-gray-100">
                <Sidebar />
                <div className="flex-1 flex flex-col overflow-hidden">
                  <Header />
                  <main className="flex-1 overflow-x-hidden overflow-y-auto bg-gray-100 p-6">
                    <FleetManagement />
                  </main>
                </div>
              </div>
            </ProtectedRoute>
          } />
          <Route path="/customers" element={
            <ProtectedRoute>
              <div className="flex h-screen bg-gray-100">
                <Sidebar />
                <div className="flex-1 flex flex-col overflow-hidden">
                  <Header />
                  <main className="flex-1 overflow-x-hidden overflow-y-auto bg-gray-100 p-6">
                    <CustomerManagement />
                  </main>
                </div>
              </div>
            </ProtectedRoute>
          } />
          <Route path="/maintenance" element={
            <ProtectedRoute>
              <div className="flex h-screen bg-gray-100">
                <Sidebar />
                <div className="flex-1 flex flex-col overflow-hidden">
                  <Header />
                  <main className="flex-1 overflow-x-hidden overflow-y-auto bg-gray-100 p-6">
                    <Maintenance />
                  </main>
                </div>
              </div>
            </ProtectedRoute>
          } />
          <Route path="/production-manager" element={
            <ProtectedRoute>
              <div className="flex h-screen bg-gray-100">
                <Sidebar />
                <div className="flex-1 flex flex-col overflow-hidden">
                  <Header />
                  <main className="flex-1 overflow-x-hidden overflow-y-auto bg-gray-100 p-6">
                    <ProductionManager />
                  </main>
                </div>
              </div>
            </ProtectedRoute>
          } />
          <Route path="/financial" element={
            <ProtectedRoute>
              <div className="flex h-screen bg-gray-100">
                <Sidebar />
                <div className="flex-1 flex flex-col overflow-hidden">
                  <Header />
                  <main className="flex-1 overflow-x-hidden overflow-y-auto bg-gray-100 p-6">
                    <Financial />
                  </main>
                </div>
              </div>
            </ProtectedRoute>
          } />
          <Route path="/settings" element={
            <ProtectedRoute>
              <div className="flex h-screen bg-gray-100">
                <Sidebar />
                <div className="flex-1 flex flex-col overflow-hidden">
                  <Header />
                  <main className="flex-1 overflow-x-hidden overflow-y-auto bg-gray-100 p-6">
                    <Settings />
                  </main>
                </div>
              </div>
            </ProtectedRoute>
          } />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
