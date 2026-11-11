import React from 'react';
import { Navigate, useLocation, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { ShieldAlert, ArrowLeft } from 'lucide-react';
import LoadingSpinner from './LoadingSpinner';

export const ProtectedRoute = ({ allowedRoles = [], children }) => {
  const { isAuthenticated, loading, role, user } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <LoadingSpinner size="lg" message="Authenticating session..." />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (allowedRoles.length > 0 && !allowedRoles.includes(role)) {
    return (
      <div className="min-h-[70vh] flex items-center justify-center p-6">
        <div className="max-w-md w-full bg-white rounded-2xl border border-gray-200 p-8 shadow-sm text-center">
          <div className="w-14 h-14 bg-rose-50 text-rose-600 rounded-2xl flex items-center justify-center mx-auto mb-4 border border-rose-100">
            <ShieldAlert className="w-8 h-8" />
          </div>
          <h2 className="text-xl font-bold text-gray-900">Access Restricted</h2>
          <p className="mt-2 text-sm text-gray-600">
            Your current role (<span className="font-semibold text-rose-700">{role}</span>) does not have authorization to view this resource.
          </p>
          <div className="mt-4 p-3 bg-gray-50 rounded-xl text-xs text-gray-500 border border-gray-100">
            Required Roles: {allowedRoles.join(', ')}
          </div>
          <div className="mt-6 flex justify-center space-x-3">
            <Link
              to="/dashboard"
              className="inline-flex items-center px-4 py-2 rounded-xl text-sm font-medium text-white bg-forest-700 hover:bg-forest-800 transition shadow-xs"
            >
              <ArrowLeft className="w-4 h-4 mr-1.5" />
              Return to Dashboard
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return children;
};

export default ProtectedRoute;
