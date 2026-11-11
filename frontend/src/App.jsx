import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import AppLayout from './layouts/AppLayout';

// Auth Pages
import LoginPage from './pages/auth/LoginPage';
import RegisterPage from './pages/auth/RegisterPage';
import ProfilePage from './pages/auth/ProfilePage';

// Main Application Pages
import DashboardPage from './pages/dashboard/DashboardPage';
import RetentionWorkbenchPage from './pages/workbench/RetentionWorkbenchPage';
import EmployeeDirectoryPage from './pages/employees/EmployeeDirectoryPage';
import EmployeeProfilePage from './pages/employees/EmployeeProfilePage';
import TeamsPage from './pages/teams/TeamsPage';
import RolesPage from './pages/roles/RolesPage';
import EngagementSurveysPage from './pages/engagement/EngagementSurveysPage';
import WorkloadPage from './pages/workload/WorkloadPage';
import CompensationPage from './pages/compensation/CompensationPage';
import InterventionsPage from './pages/interventions/InterventionsPage';
import AnalyticsPage from './pages/analytics/AnalyticsPage';
import DataQualityPage from './pages/data_quality/DataQualityPage';
import AdminPage from './pages/admin/AdminPage';
import NotFoundPage from './pages/NotFoundPage';

export function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public Routes */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          {/* Protected Application Workspace */}
          <Route
            element={
              <ProtectedRoute>
                <AppLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<DashboardPage />} />
            
            {/* Retention Decision Workbench */}
            <Route
              path="workbench"
              element={
                <ProtectedRoute allowedRoles={['MANAGER', 'HR_PARTNER', 'ADMIN', 'SYSTEM_ADMIN']}>
                  <RetentionWorkbenchPage />
                </ProtectedRoute>
              }
            />

            {/* Employee Directory & 360 Profiles */}
            <Route path="employees" element={<EmployeeDirectoryPage />} />
            <Route path="employees/:id" element={<EmployeeProfilePage />} />
            <Route path="employees/:id/timeline" element={<EmployeeProfilePage />} />

            {/* Organization Structure */}
            <Route path="teams" element={<TeamsPage />} />
            <Route path="roles" element={<RolesPage />} />

            {/* Longitudinal Signal Streams */}
            <Route
              path="engagement"
              element={
                <ProtectedRoute allowedRoles={['MANAGER', 'HR_PARTNER', 'ADMIN', 'SYSTEM_ADMIN']}>
                  <EngagementSurveysPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="workload"
              element={
                <ProtectedRoute allowedRoles={['MANAGER', 'HR_PARTNER', 'IT_OPS_PARTNER', 'ADMIN', 'SYSTEM_ADMIN']}>
                  <WorkloadPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="compensation"
              element={
                <ProtectedRoute allowedRoles={['MANAGER', 'HR_PARTNER', 'ADMIN', 'SYSTEM_ADMIN']}>
                  <CompensationPage />
                </ProtectedRoute>
              }
            />

            {/* Supportive Action & Governance */}
            <Route
              path="interventions"
              element={
                <ProtectedRoute allowedRoles={['MANAGER', 'HR_PARTNER', 'IT_OPS_PARTNER', 'ADMIN', 'SYSTEM_ADMIN']}>
                  <InterventionsPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="analytics"
              element={
                <ProtectedRoute allowedRoles={['MANAGER', 'HR_PARTNER', 'ADMIN', 'SYSTEM_ADMIN']}>
                  <AnalyticsPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="data-quality"
              element={
                <ProtectedRoute allowedRoles={['HR_PARTNER', 'ADMIN', 'SYSTEM_ADMIN', 'AUDITOR']}>
                  <DataQualityPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="admin"
              element={
                <ProtectedRoute allowedRoles={['ADMIN', 'SYSTEM_ADMIN']}>
                  <AdminPage />
                </ProtectedRoute>
              }
            />
            <Route path="profile" element={<ProfilePage />} />

            {/* Fallback 404 inside layout */}
            <Route path="*" element={<NotFoundPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
