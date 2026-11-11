import React, { useState } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { Shield, Lock, User, ArrowRight, CheckCircle2 } from 'lucide-react';
import Alert from '../../components/Alert';

export const LoginPage = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const queryParams = new URLSearchParams(location.search);
  const isSessionExpired = queryParams.get('expired') === '1';

  const demoAccounts = [
    { label: 'System Admin', user: 'sys_admin', pass: 'AdminPass123!', role: 'ADMIN' },
    { label: 'HR Partner', user: 'hr_partner_1', pass: 'HrPass123!', role: 'HR_PARTNER' },
    { label: 'Team Manager', user: 'manager_apollo', pass: 'ManagerPass123!', role: 'MANAGER' },
    { label: 'IT/Ops Partner', user: 'it_ops_lead', pass: 'ItOpsPass123!', role: 'IT_OPS_PARTNER' },
  ];

  const handleQuickFill = (acc) => {
    setUsername(acc.user);
    setPassword(acc.pass);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!username.trim() || !password.trim()) {
      setErrorMessage('Please enter both username and password.');
      return;
    }

    setLoading(true);
    setErrorMessage('');

    try {
      await login(username.trim(), password);
      const from = location.state?.from?.pathname || '/dashboard';
      navigate(from, { replace: true });
    } catch (err) {
      setErrorMessage(err.message || 'Authentication failed. Please verify credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        <div className="w-12 h-12 rounded-2xl bg-forest-800 text-white flex items-center justify-center mx-auto shadow-lg shadow-forest-900/20">
          <Shield className="w-6 h-6 text-emerald-300" />
        </div>
        <h2 className="mt-4 text-2xl font-bold tracking-tight text-gray-900">
          Retention Signal Engine
        </h2>
        <p className="mt-1 text-xs text-gray-500 font-medium">
          Supportive Employee Retention & Longitudinal Analytics Platform
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-6 shadow-sm border border-gray-200 rounded-2xl sm:px-10">
          {isSessionExpired && (
            <div className="mb-5">
              <Alert
                type="warning"
                message="Session Expired"
                details="Your login session has ended. Please sign in again."
              />
            </div>
          )}

          {errorMessage && (
            <div className="mb-5">
              <Alert type="error" message="Sign In Failed" details={errorMessage} />
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-gray-700">
                Username or Email
              </label>
              <div className="mt-1 relative rounded-xl shadow-xs">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-gray-400">
                  <User className="h-4 w-4" />
                </div>
                <input
                  type="text"
                  required
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="e.g. sys_admin or alex@company.internal"
                  className="block w-full pl-10 pr-3.5 py-2.5 text-sm rounded-xl border border-gray-300 focus:outline-hidden focus:ring-2 focus:ring-forest-600 focus:border-transparent transition"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-gray-700">
                Password
              </label>
              <div className="mt-1 relative rounded-xl shadow-xs">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-gray-400">
                  <Lock className="h-4 w-4" />
                </div>
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="block w-full pl-10 pr-3.5 py-2.5 text-sm rounded-xl border border-gray-300 focus:outline-hidden focus:ring-2 focus:ring-forest-600 focus:border-transparent transition"
                />
              </div>
            </div>

            <div>
              <button
                type="submit"
                disabled={loading}
                className="w-full flex items-center justify-center py-2.5 px-4 border border-transparent rounded-xl shadow-xs text-sm font-semibold text-white bg-forest-700 hover:bg-forest-800 focus:outline-hidden focus:ring-2 focus:ring-offset-2 focus:ring-forest-600 disabled:opacity-50 transition"
              >
                {loading ? (
                  <span className="inline-flex items-center">
                    <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                    Authenticating...
                  </span>
                ) : (
                  <span className="inline-flex items-center">
                    Sign In
                    <ArrowRight className="w-4 h-4 ml-1.5" />
                  </span>
                )}
              </button>
            </div>
          </form>

          {/* Quick-Fill Demo Roles */}
          <div className="mt-6 pt-5 border-t border-gray-100">
            <p className="text-[11px] font-semibold uppercase tracking-wider text-gray-500 mb-2.5 text-center">
              Quick-Fill Demo Credentials
            </p>
            <div className="grid grid-cols-2 gap-2">
              {demoAccounts.map((acc) => (
                <button
                  key={acc.user}
                  type="button"
                  onClick={() => handleQuickFill(acc)}
                  className="text-left px-2.5 py-2 rounded-lg border border-gray-200 hover:border-forest-600 hover:bg-forest-50/50 transition group"
                >
                  <p className="text-xs font-semibold text-gray-800 group-hover:text-forest-800 truncate">
                    {acc.label}
                  </p>
                  <p className="text-[10px] text-gray-400 font-mono truncate">{acc.user}</p>
                </button>
              ))}
            </div>
          </div>

          <div className="mt-6 text-center">
            <p className="text-xs text-gray-500">
              Need a new user account?{' '}
              <Link to="/register" className="font-semibold text-forest-700 hover:text-forest-800">
                Register here
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
