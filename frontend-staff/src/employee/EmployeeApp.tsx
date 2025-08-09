import { Routes, Route, Navigate } from 'react-router-dom';
import { EmployeeHeader } from './components/EmployeeHeader';
import { EmployeeNavigation } from './components/EmployeeNavigation';
import { EmployeeTraining } from './pages/EmployeeTraining';
import { EmployeeCertifications } from './pages/EmployeeCertifications';
import { EmployeeSafety } from './pages/EmployeeSafety';
import { EmployeeProgress } from './pages/EmployeeProgress';

export default function EmployeeApp() {
  return (
    <div className="min-h-screen bg-background">
      <EmployeeHeader />
      <div className="flex">
        <EmployeeNavigation />
        <main className="flex-1 p-6">
          <Routes>
            <Route path="/" element={<Navigate to="/employee/training" replace />} />
            <Route path="/training" element={<EmployeeTraining />} />
            <Route path="/certifications" element={<EmployeeCertifications />} />
            <Route path="/safety" element={<EmployeeSafety />} />
            <Route path="/progress" element={<EmployeeProgress />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}
