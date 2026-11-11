import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { User, KeyRound, LogOut, Shield, Database, ExternalLink } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';

export const Header = ({ title, subtitle }) => {
  const { user, role, logout } = useAuth();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const getRoleBadgeStyle = (r) => {
    switch (r) {
      case 'ADMIN':
      case 'SYSTEM_ADMIN':
        return 'bg-purple-100 text-purple-800 border-purple-200';
      case 'HR_PARTNER':
        return 'bg-emerald-100 text-emerald-800 border-emerald-200';
      case 'MANAGER':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'IT_OPS_PARTNER':
        return 'bg-amber-100 text-amber-800 border-amber-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  return (
    <header className="h-16 bg-white border-b border-gray-200 px-6 flex items-center justify-between sticky top-0 z-20 shadow-xs">
      <div>
        <h2 className="text-base font-bold text-gray-900 tracking-tight leading-tight">{title}</h2>
        {subtitle && <p className="text-xs text-gray-500 font-medium">{subtitle}</p>}
      </div>

      <div className="flex items-center space-x-4">
        {/* PostgreSQL / System status pill */}
        <div className="hidden sm:inline-flex items-center px-2.5 py-1 rounded-full text-[11px] font-semibold bg-forest-50 text-forest-800 border border-forest-200 shadow-xs">
          <span className="w-2 h-2 rounded-full bg-forest-600 mr-1.5 animate-pulse" />
          <Database className="w-3 h-3 mr-1 text-forest-700" />
          PostgreSQL 18 Online
        </div>

        {/* Role badge */}
        <span
          className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${getRoleBadgeStyle(
            role
          )}`}
        >
          <Shield className="w-3 h-3 mr-1 opacity-70" />
          {role}
        </span>

        {/* User Dropdown */}
        <div className="relative">
          <button
            onClick={() => setDropdownOpen(!dropdownOpen)}
            className="flex items-center space-x-2 p-1.5 rounded-xl hover:bg-gray-100 transition focus:outline-hidden"
          >
            <div className="w-8 h-8 rounded-lg bg-forest-700 text-white flex items-center justify-center font-bold text-xs shadow-xs">
              {user?.username ? user.username.slice(0, 2).toUpperCase() : 'U'}
            </div>
            <span className="hidden md:inline-block text-xs font-semibold text-gray-800">{user?.username}</span>
          </button>

          {dropdownOpen && (
            <div
              className="absolute right-0 mt-2 w-56 rounded-2xl bg-white shadow-xl border border-gray-100 py-2 z-50 animate-fade-in"
              onMouseLeave={() => setDropdownOpen(false)}
            >
              <div className="px-4 py-2 border-b border-gray-100">
                <p className="text-xs font-bold text-gray-900">{user?.username}</p>
                <p className="text-[11px] text-gray-500 truncate">{user?.email || 'Logged in user'}</p>
                {user?.employee_id && (
                  <p className="text-[10px] text-forest-700 font-mono mt-0.5">ID: {user.employee_id}</p>
                )}
              </div>

              <Link
                to="/profile"
                onClick={() => setDropdownOpen(false)}
                className="flex items-center px-4 py-2 text-xs text-gray-700 hover:bg-gray-50 transition"
              >
                <User className="w-3.5 h-3.5 mr-2 text-gray-400" />
                Profile & Security
              </Link>

              <button
                onClick={() => {
                  setDropdownOpen(false);
                  handleLogout();
                }}
                className="w-full flex items-center px-4 py-2 text-xs text-rose-600 hover:bg-rose-50 transition"
              >
                <LogOut className="w-3.5 h-3.5 mr-2 text-rose-500" />
                Sign Out
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;
