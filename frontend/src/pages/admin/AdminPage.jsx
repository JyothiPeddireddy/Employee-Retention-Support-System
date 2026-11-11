import React, { useState, useEffect } from 'react';
import { adminApi } from '../../api/admin';
import { useAuth } from '../../context/AuthContext';
import Modal from '../../components/Modal';
import Alert from '../../components/Alert';
import LoadingSpinner from '../../components/LoadingSpinner';
import EmptyState from '../../components/EmptyState';
import {
  Settings,
  Users,
  Database,
  Shield,
  Activity,
  Plus,
  Edit,
  Clock,
  Filter
} from 'lucide-react';

export const AdminPage = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [usersList, setUsersList] = useState([]);
  const [auditLogs, setAuditLogs] = useState([]);
  const [activeTab, setActiveTab] = useState('users');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);

  // User Role Modal
  const [selectedUser, setSelectedUser] = useState(null);
  const [newRole, setNewRole] = useState('MANAGER');
  const [isRoleModalOpen, setIsRoleModalOpen] = useState(false);
  const [submittingRole, setSubmittingRole] = useState(false);

  // Create User Modal
  const [isCreateUserModalOpen, setIsCreateUserModalOpen] = useState(false);
  const [userForm, setUserForm] = useState({
    username: '',
    email: '',
    password: '',
    role: 'MANAGER',
    employee_id: '',
  });
  const [submittingUser, setSubmittingUser] = useState(false);

  // Audit Logs Filter
  const [auditActionFilter, setAuditActionFilter] = useState('');
  const [auditEntityFilter, setAuditEntityFilter] = useState('');

  const fetchAdminData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [statsRes, usersRes, logsRes] = await Promise.all([
        adminApi.getSystemStats(),
        adminApi.listUsers(),
        adminApi.getAuditLogs({ limit: 50 }),
      ]);
      setStats(statsRes);
      setUsersList(usersRes || []);
      setAuditLogs(logsRes || []);
    } catch (err) {
      setError(err.message || 'Failed to load system administration data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAdminData();
  }, []);

  const openRoleModal = (u) => {
    setSelectedUser(u);
    setNewRole(u.role);
    setIsRoleModalOpen(true);
  };

  const handleRoleSubmit = async (e) => {
    e.preventDefault();
    setSubmittingRole(true);
    try {
      await adminApi.updateUserRole(selectedUser.user_id, newRole);
      setSuccessMsg(`Role for user '${selectedUser.username}' updated to '${newRole}'.`);
      setIsRoleModalOpen(false);
      fetchAdminData();
    } catch (err) {
      setError(err.message || 'Failed to update user role.');
    } finally {
      setSubmittingRole(false);
    }
  };

  const handleCreateUserSubmit = async (e) => {
    e.preventDefault();
    setSubmittingUser(true);
    try {
      await adminApi.createUser({
        username: userForm.username.trim(),
        email: userForm.email.trim(),
        password: userForm.password,
        role: userForm.role,
        employee_id: userForm.employee_id.trim() || null,
      });
      setSuccessMsg(`User '${userForm.username}' created successfully.`);
      setIsCreateUserModalOpen(false);
      setUserForm({ username: '', email: '', password: '', role: 'MANAGER', employee_id: '' });
      fetchAdminData();
    } catch (err) {
      setError(err.message || 'Failed to create user account.');
    } finally {
      setSubmittingUser(false);
    }
  };

  if (loading) {
    return <LoadingSpinner size="lg" message="Loading admin control center..." />;
  }

  const filteredLogs = auditLogs.filter((log) => {
    if (auditActionFilter && log.action !== auditActionFilter) return false;
    if (auditEntityFilter && log.entity_name !== auditEntityFilter) return false;
    return true;
  });

  return (
    <div className="space-y-6">
      {successMsg && <Alert type="success" message={successMsg} onClose={() => setSuccessMsg(null)} />}
      {error && <Alert type="error" message="Notice" details={error} onClose={() => setError(null)} />}

      {/* System Stats Overview Banner */}
      <div className="bg-white rounded-2xl border border-gray-200 p-6 shadow-xs">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-gray-100 pb-4 mb-4">
          <div className="flex items-center space-x-3">
            <div className="p-2.5 rounded-xl bg-purple-50 text-purple-700">
              <Database className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-base font-bold text-gray-900">PostgreSQL Database System Health</h2>
              <p className="text-xs text-gray-500 font-mono mt-0.5">{stats?.database_url_masked}</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
              Engine: {stats?.database_engine?.toUpperCase()}
            </span>
            <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-purple-50 text-purple-700 border border-purple-200">
              Active Users: {stats?.active_users || 0}
            </span>
          </div>
        </div>

        {/* Database Table Counts */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          {stats?.table_counts &&
            Object.entries(stats.table_counts).map(([tbl, cnt]) => (
              <div key={tbl} className="p-3 bg-gray-50 rounded-xl border border-gray-200 text-center">
                <span className="text-[10px] uppercase font-semibold text-gray-400 block truncate">{tbl}</span>
                <span className="text-lg font-bold text-gray-900">{cnt.toLocaleString()}</span>
              </div>
            ))}
        </div>
      </div>

      {/* Admin Tabs */}
      <div className="border-b border-gray-200 bg-white rounded-t-2xl px-4">
        <nav className="flex space-x-6" aria-label="Tabs">
          <button
            onClick={() => setActiveTab('users')}
            className={`py-3.5 px-1 border-b-2 font-semibold text-xs flex items-center space-x-2 transition ${
              activeTab === 'users'
                ? 'border-forest-600 text-forest-700'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            <Users className="w-4 h-4" />
            <span>App Users & RBAC ({usersList.length})</span>
          </button>
          <button
            onClick={() => setActiveTab('audit')}
            className={`py-3.5 px-1 border-b-2 font-semibold text-xs flex items-center space-x-2 transition ${
              activeTab === 'audit'
                ? 'border-forest-600 text-forest-700'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            <Activity className="w-4 h-4" />
            <span>Immutable Audit Logs ({auditLogs.length})</span>
          </button>
        </nav>
      </div>

      {/* Tab 1: Users & RBAC */}
      {activeTab === 'users' && (
        <div className="bg-white rounded-b-2xl border-x border-b border-gray-200 p-6 shadow-xs space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold text-gray-900 uppercase tracking-wider">Registered System Accounts</h3>
            <button
              onClick={() => setIsCreateUserModalOpen(true)}
              className="inline-flex items-center px-3.5 py-2 rounded-xl text-xs font-semibold text-white bg-forest-700 hover:bg-forest-800 transition shadow-xs"
            >
              <Plus className="w-4 h-4 mr-1.5" />
              Provision User
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-gray-50/75 border-b border-gray-200 text-gray-500 uppercase font-semibold">
                  <th className="py-3 px-4">User ID</th>
                  <th className="py-3 px-4">Username & Email</th>
                  <th className="py-3 px-4">Role Assignment</th>
                  <th className="py-3 px-4">Linked Employee</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Created At</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {usersList.map((u) => (
                  <tr key={u.user_id} className="hover:bg-gray-50/80 transition">
                    <td className="py-3.5 px-4 font-mono font-medium text-gray-600">{u.user_id}</td>
                    <td className="py-3.5 px-4">
                      <strong className="text-gray-900">{u.username}</strong>
                      <p className="text-[11px] text-gray-400">{u.email}</p>
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-forest-50 text-forest-800 border border-forest-200">
                        {u.role}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 font-mono text-gray-600">{u.employee_id || '—'}</td>
                    <td className="py-3.5 px-4">
                      <span
                        className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold ${
                          u.is_active
                            ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                            : 'bg-rose-50 text-rose-700 border border-rose-200'
                        }`}
                      >
                        {u.is_active ? 'Active' : 'Deactivated'}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-gray-500 font-mono text-[11px]">
                      {new Date(u.created_at).toLocaleDateString()}
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <button
                        onClick={() => openRoleModal(u)}
                        className="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-semibold text-gray-700 bg-gray-100 hover:bg-gray-200 transition"
                      >
                        <Edit className="w-3 h-3 mr-1 text-gray-500" />
                        Change Role
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Tab 2: Audit Logs */}
      {activeTab === 'audit' && (
        <div className="bg-white rounded-b-2xl border-x border-b border-gray-200 p-6 shadow-xs space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <h3 className="text-xs font-bold text-gray-900 uppercase tracking-wider">
              Immutable Governance Audit Logs
            </h3>

            <div className="flex items-center space-x-3">
              <select
                value={auditActionFilter}
                onChange={(e) => setAuditActionFilter(e.target.value)}
                className="text-xs rounded-xl border border-gray-300 py-1.5 px-3 bg-white focus:ring-2 focus:ring-forest-600"
              >
                <option value="">All Actions</option>
                <option value="INSERT">INSERT</option>
                <option value="UPDATE">UPDATE</option>
                <option value="DELETE">DELETE</option>
              </select>

              <select
                value={auditEntityFilter}
                onChange={(e) => setAuditEntityFilter(e.target.value)}
                className="text-xs rounded-xl border border-gray-300 py-1.5 px-3 bg-white focus:ring-2 focus:ring-forest-600"
              >
                <option value="">All Entities</option>
                <option value="employees">employees</option>
                <option value="interventions">interventions</option>
                <option value="app_users">app_users</option>
                <option value="teams">teams</option>
                <option value="roles">roles</option>
              </select>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-gray-50/75 border-b border-gray-200 text-gray-500 uppercase font-semibold">
                  <th className="py-3 px-4">Log ID</th>
                  <th className="py-3 px-4">Timestamp</th>
                  <th className="py-3 px-4">Entity & ID</th>
                  <th className="py-3 px-4">Action</th>
                  <th className="py-3 px-4">Performed By</th>
                  <th className="py-3 px-4">Changes Detail</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {filteredLogs.map((log) => (
                  <tr key={log.log_id} className="hover:bg-gray-50/80 transition">
                    <td className="py-3.5 px-4 font-mono font-medium text-gray-600">{log.log_id}</td>
                    <td className="py-3.5 px-4 text-gray-500 font-mono text-[11px]">
                      {new Date(log.timestamp).toLocaleString()}
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="font-bold text-gray-900">{log.entity_name}</span>
                      <p className="text-[10px] font-mono text-gray-400">{log.entity_id}</p>
                    </td>
                    <td className="py-3.5 px-4">
                      <span
                        className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold ${
                          log.action === 'INSERT'
                            ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                            : log.action === 'UPDATE'
                            ? 'bg-blue-50 text-blue-700 border border-blue-200'
                            : 'bg-rose-50 text-rose-700 border border-rose-200'
                        }`}
                      >
                        {log.action}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 font-mono text-gray-700">{log.performed_by}</td>
                    <td className="py-3.5 px-4 font-mono text-[11px] text-gray-600 max-w-xs truncate">
                      {log.changes ? JSON.stringify(log.changes) : '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Change Role Modal */}
      <Modal
        isOpen={isRoleModalOpen}
        onClose={() => setIsRoleModalOpen(false)}
        title={`Change Role: ${selectedUser?.username}`}
        maxWidth="max-w-md"
      >
        <form onSubmit={handleRoleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-gray-700">
              Role Permission Level
            </label>
            <select
              value={newRole}
              onChange={(e) => setNewRole(e.target.value)}
              className="mt-1 block w-full px-3.5 py-2 text-sm rounded-xl border border-gray-300 focus:ring-2 focus:ring-forest-600 bg-white"
            >
              <option value="HR_PARTNER">HR_PARTNER (Retention decisions & full audits)</option>
              <option value="MANAGER">MANAGER (Team oversight & check-ins)</option>
              <option value="IT_OPS_PARTNER">IT_OPS_PARTNER (Workload capacity logging)</option>
              <option value="EMPLOYEE">EMPLOYEE (Self profile access)</option>
              <option value="ADMIN">ADMIN (System administration)</option>
              <option value="AUDITOR">AUDITOR (Compliance oversight)</option>
            </select>
          </div>

          <div className="flex justify-end space-x-3 pt-2">
            <button
              type="button"
              onClick={() => setIsRoleModalOpen(false)}
              className="px-4 py-2 rounded-xl text-xs font-semibold text-gray-700 hover:bg-gray-100"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submittingRole}
              className="px-5 py-2 rounded-xl text-xs font-semibold text-white bg-forest-700 hover:bg-forest-800 disabled:opacity-50"
            >
              {submittingRole ? 'Saving...' : 'Update Role'}
            </button>
          </div>
        </form>
      </Modal>

      {/* Provision User Modal */}
      <Modal
        isOpen={isCreateUserModalOpen}
        onClose={() => setIsCreateUserModalOpen(false)}
        title="Provision New User"
        maxWidth="max-w-md"
      >
        <form onSubmit={handleCreateUserSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-gray-700">
              Username
            </label>
            <input
              type="text"
              required
              value={userForm.username}
              onChange={(e) => setUserForm({ ...userForm, username: e.target.value })}
              className="mt-1 block w-full px-3.5 py-2 text-sm rounded-xl border border-gray-300 focus:ring-2 focus:ring-forest-600"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-gray-700">
              Corporate Email
            </label>
            <input
              type="email"
              required
              value={userForm.email}
              onChange={(e) => setUserForm({ ...userForm, email: e.target.value })}
              className="mt-1 block w-full px-3.5 py-2 text-sm rounded-xl border border-gray-300 focus:ring-2 focus:ring-forest-600"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-gray-700">
              Initial Password (min 8 chars)
            </label>
            <input
              type="password"
              required
              minLength={8}
              value={userForm.password}
              onChange={(e) => setUserForm({ ...userForm, password: e.target.value })}
              className="mt-1 block w-full px-3.5 py-2 text-sm rounded-xl border border-gray-300 focus:ring-2 focus:ring-forest-600"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-gray-700">
              Role
            </label>
            <select
              value={userForm.role}
              onChange={(e) => setUserForm({ ...userForm, role: e.target.value })}
              className="mt-1 block w-full px-3.5 py-2 text-sm rounded-xl border border-gray-300 focus:ring-2 focus:ring-forest-600 bg-white"
            >
              <option value="HR_PARTNER">HR_PARTNER</option>
              <option value="MANAGER">MANAGER</option>
              <option value="IT_OPS_PARTNER">IT_OPS_PARTNER</option>
              <option value="EMPLOYEE">EMPLOYEE</option>
              <option value="ADMIN">ADMIN</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-gray-700">
              Linked Employee ID <span className="text-gray-400 normal-case">(Optional)</span>
            </label>
            <input
              type="text"
              value={userForm.employee_id}
              onChange={(e) => setUserForm({ ...userForm, employee_id: e.target.value })}
              placeholder="e.g. EMP-000001"
              className="mt-1 block w-full px-3.5 py-2 text-sm rounded-xl border border-gray-300 focus:ring-2 focus:ring-forest-600 font-mono"
            />
          </div>

          <div className="flex justify-end space-x-3 pt-2">
            <button
              type="button"
              onClick={() => setIsCreateUserModalOpen(false)}
              className="px-4 py-2 rounded-xl text-xs font-semibold text-gray-700 hover:bg-gray-100"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submittingUser}
              className="px-5 py-2 rounded-xl text-xs font-semibold text-white bg-forest-700 hover:bg-forest-800 disabled:opacity-50"
            >
              {submittingUser ? 'Provisioning...' : 'Provision User'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default AdminPage;
