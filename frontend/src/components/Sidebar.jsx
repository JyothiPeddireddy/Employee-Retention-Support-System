import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  LayoutDashboard,
  HeartHandshake,
  Users,
  Network,
  Briefcase,
  Clock,
  DollarSign,
  MessageSquareHeart,
  BarChart3,
  ShieldCheck,
  Settings,
  LogOut,
  UserCheck,
  ChevronRight,
  Shield
} from 'lucide-react';

export const Sidebar = () => {
  const { user, role, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const navItemClass = ({ isActive }) =>
    `flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-medium transition-all ${
      isActive
        ? 'bg-sidebar-hover text-white shadow-sm font-semibold'
        : 'text-sidebar-muted hover:bg-forest-900/60 hover:text-white'
    }`;

  const navItems = [
    {
      group: 'Overview & Decisions',
      items: [
        { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
        {
          name: 'Retention Workbench',
          path: '/workbench',
          icon: UserCheck,
          roles: ['MANAGER', 'HR_PARTNER', 'ADMIN', 'SYSTEM_ADMIN'],
        },
        { name: 'Employee Directory', path: '/employees', icon: Users },
      ],
    },
    {
      group: 'Workforce Signals',
      items: [
        { name: 'Teams & Transfers', path: '/teams', icon: Network },
        { name: 'Job Roles', path: '/roles', icon: Briefcase },
        {
          name: 'Engagement Surveys',
          path: '/engagement',
          icon: HeartHandshake,
          roles: ['MANAGER', 'HR_PARTNER', 'ADMIN', 'SYSTEM_ADMIN'],
        },
        {
          name: 'Workload & Capacity',
          path: '/workload',
          icon: Clock,
          roles: ['MANAGER', 'HR_PARTNER', 'IT_OPS_PARTNER', 'ADMIN', 'SYSTEM_ADMIN'],
        },
        {
          name: 'Compensation & Bands',
          path: '/compensation',
          icon: DollarSign,
          roles: ['MANAGER', 'HR_PARTNER', 'ADMIN', 'SYSTEM_ADMIN'],
        },
      ],
    },
    {
      group: 'Support & Governance',
      items: [
        {
          name: 'Supportive Check-ins',
          path: '/interventions',
          icon: MessageSquareHeart,
          roles: ['MANAGER', 'HR_PARTNER', 'IT_OPS_PARTNER', 'ADMIN', 'SYSTEM_ADMIN'],
        },
        {
          name: 'Analytics & Trends',
          path: '/analytics',
          icon: BarChart3,
          roles: ['MANAGER', 'HR_PARTNER', 'ADMIN', 'SYSTEM_ADMIN'],
        },
        {
          name: 'Data Quality & Audit',
          path: '/data-quality',
          icon: ShieldCheck,
          roles: ['HR_PARTNER', 'ADMIN', 'SYSTEM_ADMIN', 'AUDITOR'],
        },
        {
          name: 'System Admin',
          path: '/admin',
          icon: Settings,
          roles: ['ADMIN', 'SYSTEM_ADMIN'],
        },
      ],
    },
  ];

  return (
    <aside className="w-64 bg-sidebar-bg border-r border-sidebar-border flex flex-col flex-shrink-0 min-h-screen text-sidebar-text">
      {/* Brand Header */}
      <div className="p-5 border-b border-sidebar-border flex items-center space-x-3">
        <div className="w-9 h-9 rounded-xl bg-forest-600 flex items-center justify-center text-white shadow-md shadow-forest-950/20">
          <Shield className="w-5 h-5 text-emerald-200" />
        </div>
        <div>
          <h1 className="text-sm font-bold tracking-tight text-white leading-tight">Retention Signal</h1>
          <p className="text-[11px] text-sidebar-muted font-medium">Supportive Decision Engine</p>
        </div>
      </div>

      {/* Navigation Sections */}
      <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-6">
        {navItems.map((group, idx) => {
          const visibleItems = group.items.filter(
            (item) => !item.roles || (role && item.roles.includes(role))
          );
          if (visibleItems.length === 0) return null;

          return (
            <div key={idx}>
              <h2 className="px-3 text-[10px] font-bold uppercase tracking-wider text-emerald-300/70 mb-2">
                {group.group}
              </h2>
              <div className="space-y-1">
                {visibleItems.map((item) => {
                  const Icon = item.icon;
                  return (
                    <NavLink key={item.path} to={item.path} className={navItemClass}>
                      <div className="flex items-center space-x-3">
                        <Icon className="w-4 h-4 flex-shrink-0" />
                        <span>{item.name}</span>
                      </div>
                      <ChevronRight className="w-3.5 h-3.5 opacity-40" />
                    </NavLink>
                  );
                })}
              </div>
            </div>
          );
        })}
      </nav>

      {/* Footer Profile & Logout */}
      <div className="p-3 border-t border-sidebar-border bg-forest-950/40">
        <div className="flex items-center justify-between p-2 rounded-xl bg-forest-900/40">
          <div className="flex items-center space-x-2.5 overflow-hidden">
            <div className="w-8 h-8 rounded-lg bg-emerald-700 flex items-center justify-center text-white text-xs font-bold flex-shrink-0">
              {user?.username ? user.username.slice(0, 2).toUpperCase() : 'US'}
            </div>
            <div className="overflow-hidden">
              <p className="text-xs font-semibold text-white truncate">{user?.username || 'User'}</p>
              <p className="text-[10px] text-emerald-300 font-medium truncate">{role || 'EMPLOYEE'}</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            title="Sign Out"
            className="p-1.5 rounded-lg text-emerald-300/80 hover:text-white hover:bg-forest-800 transition"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
